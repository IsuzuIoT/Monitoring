# Importing necessary modules and libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import datetime
import mysql.connector
import traceback
import csv
from io import StringIO

# MySQL server configuration details
MYSQL_HOST = "localhost"
MYSQL_USER = "ISUZU"
MYSQL_PASSWORD = "12345"
MYSQL_DB = "isuzudb"

# Initialize the Dash app and include bootstrap styles for UI aesthetics
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Convert time in string format to a timedelta object for easy calculations
def str_to_timedelta(time_str):
    hours, minutes, seconds = map(int, time_str.split(":"))
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

# Fetch the required data from the MySQL database
def fetch_data_from_mysql():
    connection = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
    cursor = connection.cursor()
    cursor.execute("SELECT runTimeElapsed, idleTimeElapsed, downTimeElapsed FROM mesinsatu WHERE date=CURDATE() LIMIT 1")
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    return data

# Define the standard size for the UI cards (The Circles)
card_size = "350px" 

# Define the app layout which describes how the web page will look
app.layout = dbc.Container([
    html.Div([
        html.H1("ISUZU Real-time Monitoring System", className="text-center my-4", style={"fontSize": "2rem", "color": "#E1E1E1"}),
    ], style={
        "backgroundImage": "url('https://1000logos.net/wp-content/uploads/2021/04/Isuzu-logo.png')",
        "backgroundRepeat": "no-repeat",
        "backgroundPosition": "center",
        "backgroundSize": "contain",
        "height": "200px",
        "lineHeight": "150px",
    }),
    
    # The row containing the current date and time 
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
    
    # The row containing the total time running
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Total Time Running: ", className="font-weight-bold display-5 text-light"),
                html.Span(id='total-time', className="font-weight-bold ml-2 display-5 text-light"),
            ], className="text-center my-2")
        ], width=4)
    ], justify="center"),

    # The row containing the three circles for runtime, idletime, and downtime
    dbc.Container([
        dbc.Row([
            # For Run Time
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(className="card-title text-center display-5 text-dark mt-2"),
                        html.P(id='runtime-text', className="card-text text-center display-5 text-light mt-2"),
                        dbc.Progress(id="runtime-progress", value=50, max=100, striped=True, className="mb-2 mt-4", style={"height": "20px"}),
                        html.P(id='runtime-time', className="card-text text-center display-5 text-light", style={"marginTop": "20px"}) # marginTop added here
                    ], style={"backgroundColor": "#333", "borderRadius": "50%"})
                ], className="rounded-circle p-3 mb-4", style={"width": card_size, "height": card_size, "border": "6.75px solid green", "backgroundColor": "#333", "margin": "15px"}) 
            ], width=4),
            
            # For Idle Time
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(className="card-title text-center display-5 text-dark"),
                        html.P(id='idletime-text', className="card-text text-center display-5 text-light mt-2"),
                        dbc.Progress(id="idletime-progress", value=30, max=100, striped=True, className="mb-2 mt-4", style={"height": "20px"}),
                        html.P(id='idletime-time', className="card-text text-center display-5 text-light", style={"marginTop": "20px"}) # marginTop added here
                    ], style={"backgroundColor": "#333", "borderRadius": "50%"})
                ], className="rounded-circle p-2", style={"width": card_size, "height": card_size, "border": "6.75px solid yellow", "backgroundColor": "#333", "margin": "15px"})  
            ], width=4),
            
            # For Down Time
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(className="card-title text-center display-5 text-dark mt-2"),
                        html.P(id='downtime-text', className="card-text text-center display-5 text-light mt-2"),
                        dbc.Progress(id="downtime-progress", value=20, max=100, striped=True, className="mb-2 mt-4", style={"height": "20px"}),
                        html.P(id='downtime-time', className="card-text text-center display-5 text-light", style={"marginTop": "20px"}) # marginTop added here
                    ], style={"backgroundColor": "#333", "borderRadius": "50%"})
                ], className="rounded-circle p-2", style={"width": card_size, "height": card_size, "border": "6.75px solid red", "backgroundColor": "#333", "margin": "15px"}) 
            ], width=4)
        ], justify="center", className="my-4")
    ], style={"height": "27vh", "display": "flex", "justifyContent": "center", "alignItems": "center", "marginTop": "150px"}),

    # The row containing the export button
    dbc.Row([
        dbc.Col([
            dcc.Download(id="download-data"),
            html.Button("Export Data", id="export-data-button", className="btn btn-primary")
        ], width={"size": 2, "offset": 10}, style={"position": "absolute", "bottom": "20px", "right": "20px"})
    ], className="my-4")
], fluid=True, id="app-container", style={"backgroundColor": "#212529", "minHeight": "100vh"})

# The callback function that updates the time, percentages, and other metrics
@app.callback(
    [Output('live-date', 'children'),
     Output('live-time', 'children'),
     Output('runtime-text', 'children'),
     Output('idletime-text', 'children'),
     Output('downtime-text', 'children'),
     Output('total-time', 'children'),
     Output('runtime-progress', 'value'),
     Output('idletime-progress', 'value'),
     Output('downtime-progress', 'value'),
     Output('runtime-time', 'children'),
     Output('idletime-time', 'children'),
     Output('downtime-time', 'children')],
    [Input('interval-component', 'n_intervals')]
)

# The function that updates the time, percentages, and other metrics
def update_time(n):
    # Get the current date and time
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    
    # Fetch runtime, idletime, and downtime from the database
    runtime, idletime, downtime = fetch_data_from_mysql()
    
    # Convert these times from string to timedelta for calculations
    runtime_td = str_to_timedelta(runtime)
    idletime_td = str_to_timedelta(idletime)
    downtime_td = str_to_timedelta(downtime)
    
    # Calculate the total time by summing up the three times
    total_time = runtime_td + idletime_td + downtime_td
    
    # Calculate percentages of runtime, idletime, and downtime based on the total time
    total_seconds = total_time.total_seconds()
    if total_seconds != 0:
        runtime_percent = (runtime_td.total_seconds() / total_seconds) * 100
        idletime_percent = (idletime_td.total_seconds() / total_seconds) * 100
        downtime_percent = (downtime_td.total_seconds() / total_seconds) * 100
    else:
        runtime_percent, idletime_percent, downtime_percent = 0, 0, 0

    # Return the updated values to be displayed on the UI
    return (date, time, "Run Time", "Idle Time", "Down Time", str(total_time), runtime_percent, idletime_percent, downtime_percent, runtime, idletime, downtime)

# Callback function for exporting the data as a CSV when the export button is clicked
@app.callback(
    Output('download-data', 'data'),
    [Input('export-data-button', 'n_clicks')]
)

def prepare_export_data(n_clicks):
    if n_clicks:
        # Fetch data from MySQL
        data = fetch_data_from_mysql()

        # Create an in-memory CSV to hold the data
        output = StringIO()
        csvwriter = csv.writer(output)
        csvwriter.writerow(["runTimeElapsed", "idleTimeElapsed", "downTimeElapsed"])
        csvwriter.writerow(data)

        # Convert the in-memory CSV data to a string and prepare it for download
        output.seek(0)
        return dict(content=output.getvalue(), filename="exported_data.csv")
    return None

def trigger_download(data):
    if data:
        return data
    return None

# Define the server behavior (Important)
app.run_server(debug=True, port=8080)
