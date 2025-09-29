import sqlite3
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
import os

# Path to DB
DB_PATH = os.path.join(os.path.dirname(__file__), "dashboard_data.db")

# Load data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM audio_data", conn)
    summary = pd.read_sql_query("SELECT * FROM summary_statistics", conn)
    conn.close()
    return df, summary

df, summary = load_data()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

CYAN = "#00FFFF"

# Top metric cards, all in one row
metric_names = {
    "total_duration": "Total Duration",
    "total_utterances": "Total Utterances",
    "vocabulary_size": "Vocab Size",
    "alphabet_size": "Alphabet Size"
}
metric_cards = [
    dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H5(name, className="card-title"),
                html.H3(f"{summary.loc[0, col]:,}", style={"color": CYAN, "fontWeight": "bold"})
            ]),
            className="bg-dark text-white shadow-sm mb-2"
        ),
        md=3
    ) for col, name in metric_names.items()
]

# Alphabet card taking full width
alphabet_card = dbc.Col(
    dbc.Card(
        dbc.CardBody([
            html.H6("Alphabet", className="card-title"),
            html.Div(summary.loc[0, "alphabet"], style={"color": CYAN, "fontSize": "20px"})
        ]),
        className="bg-dark text-white shadow-sm mb-2"
    ),
    md=12
)

# Histogram charts
hist_titles = {
    "duration": "Duration per Audio File",
    "num_words": "Number of Words per Audio File",
    "num_characters": "Number of Characters per Audio File"
}
charts = []
for col, title in hist_titles.items():
    if col in df.columns:
        fig = px.histogram(
            df, x=col, nbins=30, title=title, color_discrete_sequence=[CYAN], template="plotly_dark"
        )
        fig.update_layout(
            title_font=dict(size=16, color=CYAN), xaxis_title_font=dict(size=14, color=CYAN),
            yaxis_title_font=dict(size=14, color=CYAN), margin=dict(l=20, r=20, t=40, b=20))
        charts.append(
            dbc.Col(dcc.Graph(figure=fig, config={"displayModeBar": False}), md=4)
        )

# Full layout - everything vertically aligned, centered, clean
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H2("Dataset Overview", className="text-center my-3", style={"color": CYAN, "fontWeight": "bold"}),
        dbc.Row(metric_cards, className="mb-3"),  # 1-row all metric cards
        dbc.Row([alphabet_card], className="mb-3"),  # Full-width alphabet row
        dbc.Row(charts)  # All charts in one row
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
