import pandas as pd
import geopandas as gpd

from pathlib import Path
import json

import geojson

from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag

import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.enrich import DashProxy, html

import plotly.express as px

from dash_extensions.javascript import assign

def load_raw() -> dict:
    with open(Path("data") / "_clean_transform.json") as f:
        return json.load(f)

payload = load_raw()
df = pd.DataFrame(payload)

cb_data = pd.read_csv('data/community_board_aggregate.csv')
with open("data/community_boards.geojson") as f: 
    gdf = geojson.load(f)

cb_data["board_num"] = pd.to_numeric(
    cb_data["community_board"].str.extract(r"(\d+)")[0],
    errors="coerce"
)

cb_data["borough"] = (
    cb_data["community_board"]
    .str.extract(r"([A-Z ]+)$")[0]
    .str.strip()
)

borough_codes = {
    "MANHATTAN": 1,
    "BRONX": 2,
    "BROOKLYN": 3,
    "QUEENS": 4,
    "STATEN ISLAND": 5,
}

cb_data["borough_code"] = cb_data["borough"].map(borough_codes)

cb_data["BoroCD"] = (
    cb_data["borough_code"] * 100
    + cb_data["board_num"]
)


count_lookup = cb_data.set_index("BoroCD")["count"].to_dict()


for feature in gdf["features"]:

    borocd = feature["properties"]["BoroCD"]

    feature["properties"]["count"] = count_lookup.get(borocd)


style_handle = assign("""
function(feature) {
    const count = feature.properties.count;

    if (count === null || count === undefined) {
        return {
            fillColor: "#cccccc",
            color: "white",
            weight: 1,
            fillOpacity: 0.3
        };
    }

    let fillColor;

    if (count < 250) {
        fillColor = "#eff3ff";
    } else if (count < 350) {
        fillColor = "#c6dbef";
    } else if (count < 450) {
        fillColor = "#9ecae1";
    } else if (count < 550) {
        fillColor = "#4292c6";
    } else {
        fillColor = "#08519c";
    }

    return {
        fillColor: fillColor,
        color: "white",
        weight: 1,
        fillOpacity: 0.75
    };
}
""")

app = DashProxy()
app.layout = html.Div(children = [
    html.H1('Daily 311 Complaints'),
    html.P('Displaying all types by community board'),
    html.Br(),
    html.Div([
        dl.Map(
            [
                dl.TileLayer(),
                dl.GeoJSON(data=gdf,
                           options={"style": style_handle}),
            ],
            center=(40.71, -74.00),
            zoom=8,
            style={"height": "50vh"},
        ),
    ]),
    html.Br(),
    html.Hr(),
    html.Br(),
    'A Graph by Complaint Type',
    html.Br(),
        dcc.Dropdown(
        id='cat-dropdown',
        options=[{"label": c, "value": c} for c in df["complaint_type"].unique()],
        value=['Noise - Residential'],
        multi=True ),
    html.Div([dag.AgGrid(
        id='data-table',
        rowData=df.to_dict('records'),
        columnDefs=[{"field": i} for i in df.columns]),
        dcc.Graph(figure={}, id='complaint-graph')]
    )
]
)

@callback(
    Output(component_id='complaint-graph', component_property='figure'),
    Input(component_id='cat-dropdown', component_property='value')
)
def update_graph(value_chosen):
    plot_df = df[df['complaint_type'].isin(value_chosen)]

    fig = px.histogram(
        plot_df,
        x='borough',
        y='count',
        histfunc='sum'
    )

    return fig
if __name__ == "__main__":
    app.run()