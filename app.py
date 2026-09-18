import pandas as pd

import geojson

import copy

from dash import html, dcc, callback, Output, Input
import dash_leaflet as dl
from dash_extensions.enrich import DashProxy, html
from dash_extensions.javascript import assign

import plotly.express as px


# load data
with open("data/community_boards.geojson") as f: 
    gdf = geojson.load(f)
df = pd.read_csv('data/borough_df.csv')
cb_data = pd.read_csv('data/cb_df.csv')
nta_data = pd.read_csv('data/nta_data.csv')

# add count and nta names to the geojson
count_lookup = cb_data.set_index("BoroCD")["count"].to_dict()
nta_lookup = nta_data.set_index("BoroCD")["NTA"].to_dict()

for feature in gdf["features"]:

    borocd = feature["properties"]["BoroCD"]

    feature["properties"]["count"] = count_lookup.get(borocd)
    feature["properties"]["NTA"] = nta_lookup.get(borocd)

# add color, improve color scale later
style_handle = assign("""
function(feature) {
    const count = feature.properties.count ?? 0;

    let fillColor;

    if (count <= 0) {
        fillColor = "#f7fbff";
    } else if (count <= 10) {
        fillColor = "#deebf7";
    } else if (count <= 25) {
        fillColor = "#c6dbef";
    } else if (count <= 50) {
        fillColor = "#9ecae1";
    } else if (count <= 100) {
        fillColor = "#6baed6";
    } else if (count <= 200) {
        fillColor = "#3182bd";
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

# make popup on click
popup_handle = assign("""
function(feature, layer) {
    const board = feature.properties.NTA;
    const count = feature.properties.count ?? 0;

    layer.bindPopup(
        "<b>Community Board:</b> " + board +
        "<br><b>Complaints:</b> " + count
    );
}
""")

#app
app = DashProxy()
app.layout = html.Div(children = [
    html.H2('Daily 311 Complaints'),
    html.P('Counts updated daily. Select a complaint type to see the count mapped by community board and graphed by borough.'),
    html.Br(),
    dcc.Dropdown(
            id='cat-dropdown',
            options=[{"label": c, "value": c} for c in df["complaint_type"].unique()],
            value=['Noise - Residential'],
            multi=True ),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.Div([
    dl.Map(
        [
            dl.TileLayer(),
            dl.GeoJSON(
                id='complaint-map',
                data=gdf,
                options={"style": style_handle,"onEachFeature": popup_handle}
            ),
        ],
    center=(40.71, -74.00),
    zoom=10,
    style={"height": "50vh"},
)
    ]),
    html.Br(),
    html.Hr(),
    html.Br(),
    'Graph by Complaint Type',
    html.Br(),
    html.Div([
    dcc.Graph(
        figure={},
        id='complaint-graph'
    )
])
]
)

# borough graph callback
@callback(
    Output('complaint-graph', 'figure'),
    Input('cat-dropdown', 'value')
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

#map callback
@callback(
    Output('complaint-map', 'data'),
    Input('cat-dropdown', 'value')
)
def update_map(value_chosen):

    filtered = cb_data[
        cb_data['complaint_type'].isin(value_chosen)
    ]

    count_lookup = (
        filtered
        .groupby('BoroCD')['count']
        .sum()
        .to_dict()
    )

    map_data = copy.deepcopy(gdf)

    for feature in map_data["features"]:
        borocd = feature["properties"]["BoroCD"]
        feature["properties"]["count"] = count_lookup.get(borocd, 0)

    print(
        [(f["properties"]["BoroCD"], f["properties"]["count"])
         for f in map_data["features"][:5]]
    )

    return map_data
if __name__ == "__main__":
    app.run()