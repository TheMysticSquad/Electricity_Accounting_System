import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from pymongo import MongoClient
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# MongoDB connection setup (Replace with your MongoDB online server details)
MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/test?retryWrites=true&w=majority"  # Use your MongoDB connection URI
client = MongoClient(MONGO_URI)
db = client["energy_data"]  # Replace with your actual database name
collection = db["consumption_data"]  # Replace with your actual collection name

# Define function to fetch real-time data from MongoDB
def fetch_data():
    # Query to get daily consumption data by feeder for the last 7 days
    data = list(collection.find({}))  # Modify this query as needed (e.g., based on date range)
    
    # If no data exists, return empty DataFrame
    if len(data) == 0:
        return pd.DataFrame()

    # Convert fetched data into pandas DataFrame for easier handling
    df = pd.DataFrame(data)
    
    # Ensure that the 'date' field is properly formatted
    df['date'] = pd.to_datetime(df['date'])

    return df

# Create the bar chart for daily energy consumption
def create_bar_chart(df):
    return px.bar(df, x='date', y='consumption', color='feeder', title="Energy Consumption by Feeder",
                 labels={'consumption': 'Energy Consumption (kWh)', 'date': 'Date'}, color_discrete_sequence=['#00BFFF', '#FF6347', '#32CD32'])

# Create the line chart for energy consumption growth
def create_line_chart(df):
    return px.line(df, x='date', y='consumption', color='feeder', title="Energy Consumption Growth Over Time",
                   labels={'consumption': 'Energy Consumption (kWh)', 'date': 'Date'}, line_shape='linear')

# Create a network graph visualization using Plotly
def create_network_graph(df):
    network_fig = go.Figure()

    # Example network visualization
    network_fig.add_trace(go.Scatter(x=[1, 2, 3], y=[2, 3, 1],
                                    mode='markers+text',
                                    text=['Feeder A', 'Feeder B', 'Feeder C'],
                                    marker=dict(size=30, color='#00BFFF'),
                                    textposition="bottom center"))

    # Connecting the nodes with lines
    network_fig.add_trace(go.Scatter(x=[1.5, 2.5], y=[2.5, 2], mode='lines', line=dict(color='#00BFFF', width=2)))

    network_fig.update_layout(title="Energy Flow Network",
                              showlegend=False,
                              plot_bgcolor="#f8f9fa",
                              xaxis=dict(showgrid=False, zeroline=False),
                              yaxis=dict(showgrid=False, zeroline=False),
                              margin=dict(t=40, b=40, l=40, r=40))

    return network_fig

# Define the layout of the Dashboard
app.layout = html.Div(style={'backgroundColor': '#f0f8ff'}, children=[
    html.H1("Energy Consumption Dashboard", style={'textAlign': 'center', 'color': '#2e3d49', 'fontSize': 36}),
    html.Div(style={'padding': '20px'}, children=[
        html.H3("Overview of Energy Consumption", style={'textAlign': 'center', 'color': '#2e3d49'}),
        dcc.Graph(id='energy-bar-chart', style={'height': '60vh'}),
    ]),
    html.Div(style={'padding': '20px'}, children=[
        html.H3("Growth of Energy Consumption Over Time", style={'textAlign': 'center', 'color': '#2e3d49'}),
        dcc.Graph(id='energy-line-chart', style={'height': '60vh'}),
    ]),
    html.Div(style={'padding': '20px'}, children=[
        html.H3("Energy Flow Network", style={'textAlign': 'center', 'color': '#2e3d49'}),
        dcc.Graph(id='energy-network-graph', style={'height': '60vh'}),
    ]),
])

# Callback to update the dashboard with real-time data
@app.callback(
    [Output('energy-bar-chart', 'figure'),
     Output('energy-line-chart', 'figure'),
     Output('energy-network-graph', 'figure')],
    [Input('energy-bar-chart', 'id')]
)
def update_dashboard(_):
    # Fetch the latest data from MongoDB
    df = fetch_data()
    
    if df.empty:
        # If no data is available, show a warning on the charts
        return go.Figure(), go.Figure(), go.Figure()

    # Create the visualizations with updated data
    bar_chart = create_bar_chart(df)
    line_chart = create_line_chart(df)
    network_graph = create_network_graph(df)
    
    return bar_chart, line_chart, network_graph

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
