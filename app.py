import pandas as pd

import geojson

import copy

from dash import html, dcc, callback, Output, Input
import dash_leaflet as dl
from dash_extensions.enrich import DashProxy, html
from dash_extensions.javascript import assign

import plotly.express as px

# Functions
def rank(df):
    date = df['date'].max()
    one_row = df[df['date'] == date]
    one_row['rank'] = round(one_row.groupby('complaint_type')['rolling_avg'].rank(pct=True),2) 
    return one_row


# load data
with open("data/community_boards.geojson") as f: 
    gdf = geojson.load(f)
df = pd.read_csv('data/borough_df.csv')
cb_raw = pd.read_csv('data/cb_df.csv')
cb_data = rank(cb_raw)
nta_data = pd.read_csv('data/nta_data.csv')

# add count and nta names to the geojson
count_lookup = cb_data.set_index(["BoroCD", "complaint_type"])["rolling_avg"].to_dict()
rank_lookup = cb_data.set_index(["BoroCD", "complaint_type"])["rank"].to_dict()
nta_lookup = nta_data.set_index("BoroCD")["NTA"].to_dict()

for feature in gdf["features"]:

    borocd = feature["properties"]["BoroCD"]
    selected_complaint_type = "Noise - Residential"

    feature["properties"]["rolling_avg"] = count_lookup.get((borocd,selected_complaint_type))
    feature["properties"]["rank"] = rank_lookup.get((borocd,selected_complaint_type))
    feature["properties"]["NTA"] = nta_lookup.get(borocd)

# add color, improve color scale later
style_handle = assign("""
function(feature) {
    const pct = feature.properties.rank ?? 0;

    let fillColor;

    if (pct <= 0) {
        fillColor = "#ffffcc";
    } else if (pct <= 0.5) {
        fillColor = "#ffeda0";
    } else if (pct <= 0.75) {
        fillColor = "#fed976";
    } else if (pct <= 0.9) {
        fillColor = "#feb24c";
    } else if (pct <= 0.95) {
        fillColor = "#fd8d3c";
    } else if (pct <= 0.99) {
        fillColor = "#e31a1c";
    } else {
        fillColor = "#b10026";
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
    const count = feature.properties.rolling_avg ?? 0;
    const rank = feature.properties.rank ?? 0;

    layer.bindPopup(
        "<b>Community Board:</b> " + board +
        "<br><b>3 Day Rolling Avg. :</b> " + count +
        "<br><b>Rank:</b> " + rank
    );
}
""")

#app
app = DashProxy()
app.layout = html.Div(children = [
    html.H2('Daily 311 Complaints'),
    html.P('This dashboard looks at 311 complaints by community board. ' \
    'It updates every day with new complaints and takes a rolling average by complaint type. ' \
    'It also ranks each community board by complaint type. Select a complaint type below to update the map (multiple can be selected), and click a community board to see its rolling average and rank.' \
    'Below the map you can see a graph of complaint type by borough.',
           style={
               "textAlign": "center",
               "fontFamily": "Georgia, serif"
           }),
    html.Br(),
    html.Div(
        dcc.Dropdown(
                id='cat-dropdown',
                maxHeight=300,
                options=[{"label": c.title(), "value": c} for c in df["complaint_type"].unique()],
                value=['Noise - Residential'],
                multi=True ),
                style={"marginLeft": "60px", "marginRight": "60px"}
    ),
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
    html.Div(
        dcc.Graph(
            figure={},
            id='biggest-shifts'
        )
    ),
    html.P('Complaint type by Borough',
                      style={
               "textAlign": "center",
               "fontFamily": "Georgia, serif"
           }),
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
        y='rolling_avg',
        histfunc='sum'
    )

    return fig

#big shifts callback
@callback(
        Output('biggest-shifts', 'figure'),
        Input('cat-dropdown', 'value')
)
def shift_graph(value_chosen):
    df = cb_raw[cb_raw['complaint_type'].isin(value_chosen)]

    id_max = df.groupby('community_board')['rolling_avg'].idxmax()
    max_df = df.loc[id_max][['community_board','rolling_avg']]
    max_df.rename(columns={'rolling_avg':'cb_max'},inplace=True)

    id_min = df.groupby('community_board')['rolling_avg'].idxmin()
    min_df = df.loc[id_min][['community_board','rolling_avg']]
    min_df.rename(columns={'rolling_avg':'cb_min'},inplace=True)

    joined = max_df.merge(min_df)
    joined['shift'] = joined['cb_max'] - joined['cb_min']

    highest_df = joined.loc[joined['shift'].abs().idxmax()]
    biggest_cb = highest_df['community_board']
    df = df[df['community_board'] == biggest_cb]

    fig = px.line(df, x="date", y="rolling_avg", title=f"{value_chosen} in {biggest_cb}")

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
        .groupby('BoroCD')['rolling_avg']
        .sum()
        .to_dict()
    )

    rank_lookup = (
        filtered
        .groupby('BoroCD')['rank']
        .mean()
        .to_dict()
    )


    map_data = copy.deepcopy(gdf)

    for feature in map_data["features"]:
        borocd = feature["properties"]["BoroCD"]
        feature["properties"]["rank"] = rank_lookup.get(borocd, 0)
        feature["properties"]["rolling_avg"] = count_lookup.get(borocd, 0)

    return map_data
if __name__ == "__main__":
    app.run()