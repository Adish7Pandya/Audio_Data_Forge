import sqlite3
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc
import os

# --- Configuration ---
DB_PATH = os.path.join(os.path.dirname(__file__), "dashboard_data.db")
CARD_BACKGROUND = "#1f001f" 
BACKGROUND_DARK = "#120012" 
PRIMARY_RED = "#d4004c"
ACCENT_PINK = "#ff6f9f"
TEXT_LIGHT = "#ffffff"

# --- Load Data ---
def load_data():
    """Loads data from the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM audio_data", conn)
        summary = pd.read_sql_query("SELECT * FROM summary_statistics", conn)
        conn.close()
        return df, summary
    except (sqlite3.OperationalError, pd.io.sql.DatabaseError) as e:
        print(f"Database error: {e}. Returning empty dataframes.")
        return pd.DataFrame(), pd.DataFrame(columns=[
            "total_duration", "total_utterances", "vocabulary_size", "alphabet_size", "alphabet"
        ])

df, summary = load_data()

# --- Initialize Dash App ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# --- Helper Function for Cards ---
def create_metric_card(title, value, unit=""):
    """Creates a styled dbc.Card for a given metric."""
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H5(title, className="card-title", style={"color": ACCENT_PINK, "fontSize": "1rem"}),
                html.H3(f"{value:,.2f}{unit}" if isinstance(value, float) else f"{value:,}{unit}", 
                        style={"color": PRIMARY_RED, "fontWeight": "bold"})
            ]),
            style={
                "backgroundColor": CARD_BACKGROUND, 
                "border": f"1px solid {PRIMARY_RED}",
                "color": TEXT_LIGHT
            },
            className="shadow-lg m-1"
        ),
        lg=3, md=6
    )

# --- Prepare Data for Display ---
if not summary.empty:
    summary_data = summary.iloc[0].to_dict()
else:
    summary_data = {
        "total_duration": 0, "total_utterances": 0, "vocabulary_size": 0, "alphabet_size": 0, "alphabet": ""
    }

# --- Card Creation ---
metric_cards_1 = [
    create_metric_card("Total Duration (s)", summary_data["total_duration"]),
    create_metric_card("Total Utterances", summary_data["total_utterances"]),
    create_metric_card("Vocabulary Size", summary_data["vocabulary_size"]),
    create_metric_card("Alphabet Size", summary_data["alphabet_size"]),
]

alphabet_card = None
if not summary.empty and "alphabet" in summary.columns:
    raw_alphabet = summary_data["alphabet"]
    formatted_alphabet = f"[{', '.join([repr(char) for char in raw_alphabet])}]"
    alphabet_card = dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H6("Alphabet", className="card-title", style={"color": ACCENT_PINK}),
                html.Div(
                    formatted_alphabet, 
                    style={
                        "color": TEXT_LIGHT, 
                        "fontSize": "1.2rem", 
                        "wordBreak": "break-all",
                        "fontFamily": "monospace"
                    }
                )
            ]),
            style={"backgroundColor": CARD_BACKGROUND, "border": f"1px solid {PRIMARY_RED}"},
            className="shadow-lg mb-4"
        ),
        md=12
    )

# --- Chart Generation ---
hist_titles = {
    "duration": "Duration per Audio File",
    "num_characters": "Number of Characters per Audio File",
    "num_words": "Number of Words per Audio File"
}
charts = []
for col, title in hist_titles.items():
    if col in df.columns:
        fig = px.histogram(
            df, x=col, nbins=30, color_discrete_sequence=[PRIMARY_RED]
        )
        # ⭐️ THIS IS THE UPDATED SECTION ⭐️
        fig.update_layout(
            # --- Title Styling ---
            title=dict(
                text=f"<b>{title}</b>", # Using <b> tag for bold text
                font=dict(size=18, color=ACCENT_PINK), # Increased size
                x=0.5 # Center the title
            ),
            # --- General Layout Styling ---
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT_LIGHT,
            # --- X-Axis Styling ---
            xaxis=dict(
                showgrid=False,
                linecolor=PRIMARY_RED,
                title_font=dict(size=14), # Increased axis title size
                tickfont=dict(size=12)  # Increased tick label size
            ),
            # --- Y-Axis Styling ---
            yaxis=dict(
                showgrid=False,
                linecolor=PRIMARY_RED,
                title_font=dict(size=14), # Increased axis title size
                tickfont=dict(size=12)  # Increased tick label size
            ),
            # --- Margin and Height ---
            margin=dict(l=40, r=20, t=50, b=40), # Adjusted margins for new font sizes
            height=320 # Increased height slightly
        )
        charts.append(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=fig, config={"displayModeBar": False})),
                    style={
                        "backgroundColor": CARD_BACKGROUND, 
                        "border": f"1px solid {PRIMARY_RED}"
                    },
                    className="shadow-lg m-1"
                ), 
                md=4
            )
        )

# --- App Layout ---
app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": BACKGROUND_DARK, "minHeight": "100vh", "padding": "15px"},
    children=[
        html.H2("Speech Dataset Overview", className="text-center my-3", style={"color": PRIMARY_RED, "fontWeight": "bold"}),
        dbc.Row(metric_cards_1, className="mb-3"),
        dbc.Row([alphabet_card] if alphabet_card else [], className="mb-3"),
        dbc.Row(charts),
    ]
)

# --- This is the critical block that was missing ---
# It tells Python to start the web server when the script is executed.
if __name__ == "__main__":
    app.run(debug=True)