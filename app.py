import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from export_utils import generate_report

# Database configuration
DB_URL = "postgresql://neondb_owner:npg_OqnZp0BDwSE1@ep-shy-poetry-abbw3imb-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&options=endpoint%3Dep-shy-poetry-abbw3imb"

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Electricity Distribution Network Dashboard"

# Database query utility
def query_db(sql, params=None):
    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute(sql, params)
        data = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

# Dropdown query functions
def get_districts():
    return query_db("SELECT id, name FROM districts")

def get_substations(district_id):
    return query_db("SELECT id, name FROM substations WHERE district_id = %s", (district_id,))

def get_feeders(substation_id):
    return query_db("SELECT id, name FROM feeders WHERE substation_id = %s", (substation_id,))

# App layout
app.layout = html.Div(style={'backgroundColor': '#f0f8ff', 'padding': '20px'}, children=[
    html.H1("Electricity Distribution Network Dashboard", style={'textAlign': 'center', 'color': '#2e3d49'}),

    html.Label("Select District:"),
    dcc.Dropdown(id='district-dropdown', placeholder='Select a district'),

    html.Label("Select Substation:"),
    dcc.Dropdown(id='substation-dropdown', placeholder='Select a substation'),

    html.Label("Select Feeder:"),
    dcc.Dropdown(id='feeder-dropdown', placeholder='Select a feeder'),

    html.Br(),
    dcc.Graph(id='feeder-pie-chart'),
    dcc.Graph(id='feeder-bar-chart'),
    dcc.Graph(id='dtr-pie-chart'),
    dcc.Graph(id='dtr-bar-chart'),

    html.Br(),
    html.Label("Export Format:"),
    dcc.Dropdown(
        id='export-format',
        options=[
            {'label': 'PDF', 'value': 'pdf'},
            {'label': 'HTML', 'value': 'html'},
            {'label': 'CSV', 'value': 'csv'},
            {'label': 'Excel', 'value': 'excel'}
        ],
        value='pdf'
    ),
    html.Br(),
    html.Button("Export Report", id='export-button'),
    html.Div(id='download-link')
])

# Callbacks for dropdown updates
@app.callback(Output('district-dropdown', 'options'),
              Input('district-dropdown', 'id'))
def update_district_options(_):
    df = get_districts()
    return [{'label': row['name'], 'value': row['id']} for _, row in df.iterrows()]

@app.callback(Output('substation-dropdown', 'options'),
              Input('district-dropdown', 'value'))
def update_substation_options(district_id):
    if not district_id:
        return []
    df = get_substations(district_id)
    return [{'label': row['name'], 'value': row['id']} for _, row in df.iterrows()]

@app.callback(Output('feeder-dropdown', 'options'),
              Input('substation-dropdown', 'value'))
def update_feeder_options(substation_id):
    if not substation_id:
        return []
    df = get_feeders(substation_id)
    return [{'label': row['name'], 'value': row['id']} for _, row in df.iterrows()]

# Chart callback
@app.callback(
    [Output('feeder-pie-chart', 'figure'),
     Output('feeder-bar-chart', 'figure'),
     Output('dtr-pie-chart', 'figure'),
     Output('dtr-bar-chart', 'figure')],
    [Input('substation-dropdown', 'value'),
     Input('feeder-dropdown', 'value')]
)
def update_charts(substation_id, feeder_id):
    if feeder_id:
        dtr_df = query_db('''
            SELECT dtrs.name AS dtr_name,
                   COUNT(consumers.consumer_no) AS dtr_consumer_count,
                   SUM(consumers.load_kw) AS dtr_total_load_kw
            FROM dtrs
            LEFT JOIN consumers ON dtrs.id = consumers.dtr_id
            WHERE dtrs.feeder_id = %s
            GROUP BY dtrs.name''', (feeder_id,))

        pie = px.pie(dtr_df, values='dtr_total_load_kw', names='dtr_name', title='DTR Load Distribution')
        bar = px.bar(dtr_df, x='dtr_name',
                     y=dtr_df['dtr_total_load_kw'] / dtr_df['dtr_consumer_count'],
                     title='DTR Average Consumption')
        return go.Figure(), go.Figure(), pie, bar

    elif substation_id:
        feeder_df = query_db('''
            SELECT feeders.name AS feeder_name,
                   COUNT(consumers.consumer_no) AS feeder_consumer_count,
                   SUM(consumers.load_kw) AS feeder_total_load_kw
            FROM feeders
            LEFT JOIN dtrs ON feeders.id = dtrs.feeder_id
            LEFT JOIN consumers ON dtrs.id = consumers.dtr_id
            WHERE feeders.substation_id = %s
            GROUP BY feeders.name''', (substation_id,))

        pie = px.pie(feeder_df, values='feeder_total_load_kw', names='feeder_name', title='Feeder Load Distribution')
        bar = px.bar(feeder_df, x='feeder_name',
                     y=feeder_df['feeder_total_load_kw'] / feeder_df['feeder_consumer_count'],
                     title='Feeder Average Consumption')
        return pie, bar, go.Figure(), go.Figure()

    return go.Figure(), go.Figure(), go.Figure(), go.Figure()

# Export report callback
@app.callback(
    Output('download-link', 'children'),
    Input('export-button', 'n_clicks'),
    State('export-format', 'value'),
    State('district-dropdown', 'value'),
    State('substation-dropdown', 'value'),
    State('feeder-dropdown', 'value')
)
def export_report(n_clicks, export_format, district_id, substation_id, feeder_id):
    if not n_clicks:
        return ""

    filters = {
        "District ID": district_id,
        "Substation ID": substation_id,
        "Feeder ID": feeder_id
    }

    figs = update_charts(substation_id, feeder_id)
    titles = ["Feeder Pie", "Feeder Bar", "DTR Pie", "DTR Bar"]

    # Data export for CSV/Excel
    if export_format in ["csv", "excel"]:
        if feeder_id:
            df = query_db('''
                SELECT dtrs.name AS name,
                       COUNT(consumers.consumer_no) AS consumer_count,
                       SUM(consumers.load_kw) AS total_load_kw
                FROM dtrs
                LEFT JOIN consumers ON dtrs.id = consumers.dtr_id
                WHERE dtrs.feeder_id = %s
                GROUP BY dtrs.name''', (feeder_id,))
        elif substation_id:
            df = query_db('''
                SELECT feeders.name AS name,
                       COUNT(consumers.consumer_no) AS consumer_count,
                       SUM(consumers.load_kw) AS total_load_kw
                FROM feeders
                LEFT JOIN dtrs ON feeders.id = dtrs.feeder_id
                LEFT JOIN consumers ON dtrs.id = consumers.dtr_id
                WHERE feeders.substation_id = %s
                GROUP BY feeders.name''', (substation_id,))
        else:
            df = pd.DataFrame()
        href, filename = generate_report([], [], export_format, data_df=df, filters=filters)
    else:
        href, filename = generate_report(figs, titles, export_format, filters=filters)

    return html.A(f"Download {export_format.upper()} Report", href=href, download=filename, target="_blank")

# Run app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
