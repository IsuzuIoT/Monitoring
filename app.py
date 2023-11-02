import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

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
], fluid=True, id="app-container", style={"backgroundColor": "#212529", "minHeight": "100vh"})

if __name__ == '__main__':
    try:
        app.run_server(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\nScript terminated.")
