import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import time
import mysql.connector

# MySQL server configuration details
MYSQL_HOST = "10.63.29.96"
MYSQL_USER = "ISUZU"
MYSQL_PASSWORD = "12345"
MYSQL_DB = "isuzudb"

run_increment = False
idle_increment = False
down_increment = False
run_seconds = 0
idle_seconds = 0
down_seconds = 0
total_seconds = 0

def format_time(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

# Fetch the required data from the MySQL database
def fetch_status_from_mysql():
    connection = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
    cursor = connection.cursor()
    cursor.execute("SELECT status FROM fanuc WHERE date = CURDATE() AND duration IS NULL")
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    return data

def update_status():
    global run_increment, idle_increment, down_increment
    
    status = fetch_status_from_mysql()
    if status is not None:
        run_increment = status[0] == 'RUNNING'
        idle_increment = status[0] == 'IDLE'
        down_increment = status[0] == 'DOWN'
    else:
        pass

def update_time():
    global run_increment, idle_increment, down_increment, run_seconds, idle_seconds, down_seconds, total_seconds

    update_status()
    if run_increment:
        run_seconds += 1
    elif idle_increment:
        idle_seconds += 1
    elif down_increment:
        down_seconds += 1

    total_seconds = run_seconds + idle_seconds + down_seconds

def get_time_data():
    date = time.strftime("%Y-%m-%d")
    clock = time.strftime("%H:%M:%S")
    runtime = format_time(run_seconds)
    idletime = format_time(idle_seconds)
    downtime = format_time(down_seconds)
    total_time = format_time(total_seconds)
    runtime_percent = (run_seconds / total_seconds) * 100 if total_seconds > 0 else 0
    idletime_percent = (idle_seconds / total_seconds) * 100 if total_seconds > 0 else 0
    downtime_percent = (down_seconds / total_seconds) * 100 if total_seconds > 0 else 0

    return date, clock, "Run Time", "Idle Time", "Down Time", runtime, idletime, downtime, total_time, runtime_percent, idletime_percent, downtime_percent

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.Div([
        html.H1("ISUZU Real-time Monitoring System", className="text-center my-4", style={"fontSize": "2rem", "color": "#E1E1E1"}),
    ], style={
        "backgroundImage": "url('/assets/isuzu.png')",
        "backgroundRepeat": "no-repeat",
        "backgroundPosition": "center",
        "backgroundSize": "contain",
        "height": "150px",
        "lineHeight": "150px",
    }),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Current Date:  ", className="font-weight-bold display-5 text-light"),
                html.Span(id='live-date', className="font-weight-bold ml-2 display-5 text-light"),
            ], className="text-center my-2"),
            
            html.Div([
                html.Label("Current Time:", className="font-weight-bold display-5 text-light"),
                html.Span(id='live-time', className="font-weight-bold ml-2 display-5 text-light"),
            ], className="text-center my-2"),
            
            dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
        ], width=4)
    ], justify="center"),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Total Time Running: ", className="font-weight-bold display-5 text-light"),
                html.Span(id='total-time', className="font-weight-bold ml-2 display-5 text-light"),
            ], className="text-center my-2")
        ], width=4)
    ], justify="center"),

    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(className="card-title text-center display-5 text-dark mt-2"),
                        html.P(id='runtime-text', className="card-text text-center display-5 text-light mt-2"),
                        dbc.Progress(id="runtime-progress", value=50, max=100, striped=True, className="mb-2 mt-4", style={"height": "20px"}),
                        html.P(id='runtime-time', className="card-text text-center display-5 text-light", style={"marginTop": "20px"})
                    ], style={"backgroundColor": "#333", "borderRadius": "50%"})
                ], className="rounded-circle p-3 mb-4", style={"width": "350px", "height": "350px", "border": "6.75px solid green", "backgroundColor": "#333", "margin": "15px"})
            ], width=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(className="card-title text-center display-5 text-dark"),
                        html.P(id='idletime-text', className="card-text text-center display-5 text-light mt-2"),
                        dbc.Progress(id="idletime-progress", value=30, max=100, striped=True, className="mb-2 mt-4", style={"height": "20px"}),
                        html.P(id='idletime-time', className="card-text text-center display-5 text-light", style={"marginTop": "20px"})
                    ], style={"backgroundColor": "#333", "borderRadius": "50%"})
                ], className="rounded-circle p-2", style={"width": "350px", "height": "350px", "border": "6.75px solid yellow", "backgroundColor": "#333", "margin": "15px"})
            ], width=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(className="card-title text-center display-5 text-dark mt-2"),
                        html.P(id='downtime-text', className="card-text text-center display-5 text-light mt-2"),
                        dbc.Progress(id="downtime-progress", value=20, max=100, striped=True, className="mb-2 mt-4", style={"height": "20px"}),
                        html.P(id='downtime-time', className="card-text text-center display-5 text-light", style={"marginTop": "20px"})
                    ], style={"backgroundColor": "#333", "borderRadius": "50%"})
                ], className="rounded-circle p-2", style={"width": "350px", "height": "350px", "border": "6.75px solid red", "backgroundColor": "#333", "margin": "15px"})
            ], width=4)
        ], justify="center", className="my-4")
    ], style={"height": "27vh", "display": "flex", "justifyContent": "center", "alignItems": "center", "marginTop": "150px"}),
], fluid=True, id="app-container", style={"backgroundColor": "#212529", "minHeight": "100vh"})

@app.callback(
    [Output('live-date', 'children'),
     Output('live-time', 'children'),
     Output('runtime-text', 'children'),
     Output('idletime-text', 'children'),
     Output('downtime-text', 'children'),
     Output('runtime-time', 'children'),
     Output('idletime-time', 'children'),
     Output('downtime-time', 'children'),
     Output('total-time', 'children'),
     Output('runtime-progress', 'value'),
     Output('idletime-progress', 'value'),
     Output('downtime-progress', 'value')],
    [Input('interval-component', 'n_intervals')]
)
def update_ui(n_intervals):
    update_time()
    date, clock, _, _, _, runtime, idletime, downtime, total_time, runtime_percent, idletime_percent, downtime_percent = get_time_data()

    return (date, clock, "Run Time", "Idle Time", "Down Time", runtime, idletime, downtime, total_time, runtime_percent, idletime_percent, downtime_percent)

if __name__ == '__main__':
    try:
        app.run_server(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\nScript terminated.")
