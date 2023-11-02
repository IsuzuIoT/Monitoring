import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import paho.mqtt.client as mqtt
import mysql.connector
import time
import threading
import csv
from io import StringIO

mqttServer = "3faf5e66f2c64a618c226e9421b6a461.s1.eu.hivemq.cloud"

# MySQL server configuration details
MYSQL_HOST = "localhost"
MYSQL_USER = "ISUZU"
MYSQL_PASSWORD = "12345"
MYSQL_DB = "isuzudb"

# Fetch the required data from the MySQL database
def fetch_data_from_mysql():
    connection = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM fanuc WHERE date=CURDATE()")
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def format_time(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

class RealTimeMonitor:
    def __init__(self):
        self.run_increment = False
        self.idle_increment = False
        self.down_increment = False
        self.run_seconds = 0
        self.idle_seconds = 0
        self.down_seconds = 0
        self.total_seconds = 0

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(mqttServer, 8883, 0)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("R01/ON")
        client.subscribe("R02/ON")
        client.subscribe("R12/OFF")

    def on_message(self, client, userdata, msg):
        print(f"{msg.topic}: {msg.payload.decode()}")
        c = msg.payload.decode()

        if msg.topic == "R01/ON":
            self.run_increment = (c == "true")
        elif msg.topic == "R02/ON":
            self.down_increment = (c == "true")
        elif msg.topic == "R12/OFF":
            self.idle_increment = (c == "true")

    def update_time(self):
        if self.run_increment:
            self.run_seconds += 1
        elif self.idle_increment:
            self.idle_seconds += 1
        elif self.down_increment:
            self.down_seconds += 1

        self.total_seconds = self.run_seconds + self.idle_seconds + self.down_seconds

    def get_time_data(self):
        date = time.strftime("%Y-%m-%d")
        clock = time.strftime("%H:%M:%S")
        runtime = format_time(self.run_seconds)
        idletime = format_time(self.idle_seconds)
        downtime = format_time(self.down_seconds)
        total_time = format_time(self.total_seconds)
        runtime_percent = (self.run_seconds / self.total_seconds) * 100 if self.total_seconds > 0 else 0
        idletime_percent = (self.idle_seconds / self.total_seconds) * 100 if self.total_seconds > 0 else 0
        downtime_percent = (self.down_seconds / self.total_seconds) * 100 if self.total_seconds > 0 else 0

        return date, clock, "Run Time", "Idle Time", "Down Time", runtime, idletime, downtime, total_time, runtime_percent, idletime_percent, downtime_percent

monitor = RealTimeMonitor()

def start_mqtt_thread():
    monitor.client.loop_forever()

# Start MQTT client loop in a separate thread
mqtt_thread = threading.Thread(target=start_mqtt_thread)
mqtt_thread.start()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.Div([
        html.H1("ISUZU Real-time Monitoring System", className="text-center my-4", style={"fontSize": "2rem", "color": "#E1E1E1"}),
    ], style={
        "backgroundImage": "url('/Users/NUC/isuzu.png')",
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
    
    # The row containing the export button
    dbc.Row([
        dbc.Col([
            dcc.Download(id="download-data"),
            html.Button("Export Data", id="export-data-button", className="btn btn-primary")
        ], width={"size": 2, "offset": 10}, style={"position": "absolute", "bottom": "20px", "right": "20px"})
    ], className="my-4")
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
def update_time(n):
    monitor.update_time()
    date, clock, _, _, _, runtime, idletime, downtime, total_time, runtime_percent, idletime_percent, downtime_percent = monitor.get_time_data()

    return (date, clock, "Run Time", "Idle Time", "Down Time", runtime, idletime, downtime, total_time, runtime_percent, idletime_percent, downtime_percent)

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
        csvwriter.writerow(["date", "start_time", "end_time", "duration", "status"])

        for row in data:
            csvwriter.writerow(row)

        # Convert the in-memory CSV data to a string and prepare it for download
        output.seek(0)
        return dict(content=output.getvalue(), filename="exported_data.csv")
    return None

def trigger_download(data):
    if data:
        return data
    return None

if __name__ == '__main__':
    try:
        app.run_server(debug=True, host=0.0.0.0, port=8080)
    except KeyboardInterrupt:
        print("\nScript terminated.")
        monitor.client.disconnect()  # Disconnect the MQTT client
        mqtt_thread.join()  # Wait for the MQTT client loop thread to finish before exitingw
