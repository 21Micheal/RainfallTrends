from flask import Flask, render_template, jsonify
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests

# Initialize Flask app
server = Flask(__name__)

# Flask route for API
@server.route("/api/weather/<city>")
def get_weather(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
    response = requests.get(url).json()
    
    if 'results' in response:
        lat, lon = response['results'][0]['latitude'], response['results'][0]['longitude']
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode&current_weather=true&timezone=auto"
        weather_response = requests.get(weather_url).json()
        return jsonify(weather_response)
    else:
        return jsonify({"error": "City not found"})

# Initialize Dash app
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/')

weather_codes = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense intensity",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy intensity",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    95: "Thunderstorm: Slight",
    96: "Thunderstorm: Slight hail",
    99: "Thunderstorm: Heavy hail"
}

app.layout = html.Div([
    html.H1("Weather Forecast", style={'textAlign': 'center', 'color': '#333'}),
    
    html.Div([
        dcc.Input(id='city-input', type='text', placeholder='Enter city name', debounce=True, style={'marginRight': '10px'}),
        html.Button('Get Weather', id='submit-button', n_clicks=0, style={'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 'padding': '5px 10px'})
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div(id='weather-output', style={'textAlign': 'center', 'fontSize': '18px', 'marginBottom': '20px'})
], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'})

@app.callback(
    Output('weather-output', 'children'),
    Input('submit-button', 'n_clicks'),
    Input('city-input', 'value')
)
def update_weather(n_clicks, city):
    if city and n_clicks > 0:
        url = f"http://127.0.0.1:5000/api/weather/{city}"
        response = requests.get(url).json()
        if 'current_weather' in response and 'daily' in response:
            today_code = response['daily']['weathercode'][0]
            tomorrow_code = response['daily']['weathercode'][1]
            today_weather = weather_codes.get(today_code, "Unknown")
            tomorrow_weather = weather_codes.get(tomorrow_code, "Unknown")
            return f"Today's Weather: {today_weather}, Tomorrow's Weather: {tomorrow_weather}"
        else:
            return "City not found. Try again."
    return ""

if __name__ == '__main__':
    server.run(debug=True)
