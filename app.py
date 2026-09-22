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
    html.H2('Daily 311 Complaints',           
            style={
               "textAlign": "center",
               "fontFamily": "Georgia, serif"
           }),
    html.P(['This dashboard looks at 311 complaints by complaint type and by Community Board (CB). ' \
    'It updates every day with new complaints, and it is on a day delay. ' ,
    html.Br(),
    html.Br(),
    'For the map and graphs below it takes a 3 day rolling average by CB and complaint type, and it then ranks every CB by percentile on that complaint type. That percentile ranking is then mapped below. ' \
    'Select a complaint type below to update the map (multiple complaints can be selected at one time), and click a CB to see its rolling average and rank. ' ,
    html.Br(),
    html.Br(),
    'Below the map there are several graphs corresponding to the complaint type(s) you selected. ' \
    'The first is of the community board with the largest change in rolling avg.  in the selected complaint type(s) during the time period covered in the data (eventually this will be 30 days). ' \
    'Below that is a graph that allows you to select a CB and see how the rolling average of complaints has changed over the time represented in the data. ' \
    'Finally, there is a bar chart of the sum of complaints by Borough. '],
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
    html.P('This graph shows the CB with the largest change in the selected complaint type.',
                      style={
               "textAlign": "center",
               "fontFamily": "Georgia, serif"
           }),
    html.Div(
        dcc.Graph(
            figure={},
            id='biggest-shifts'
        )
    ),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.P('Pick any CB from the list to see how the complaint type selected above has changed over the period represented in the data.',
                      style={
               "textAlign": "center",
               "fontFamily": "Georgia, serif"
           }),
    html.Div(
        dcc.Dropdown(
            id='cb-dropdown',
            maxHeight=300,
            options=[{"label": c.title(), "value": c} for c in nta_data["NTA"].unique()],
            value='Jackson Heights'
            ),
            style={"marginLeft": "60px", "marginRight": "60px"}
    ),
    dcc.Graph(
        figure={},
        id='each-cb-graph'
    ),   
    html.Br(),
    html.Hr(),
    html.Br(),
    html.P('This graph shows the sum of the selected complaint type by Borough.',
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
        histfunc='sum',
        labels={
                "borough": "Borough",
                "rolling_avg": "3-Day Rolling Avg."
                }
    )
    fig.update_layout(
    font_family="Georgia, serif",
    font_color="black",
    title_font_family="Georgia"
    )

    return fig

# each cb callback
@app.callback(
    Output('each-cb-graph', 'figure'),
    [Input('cat-dropdown', 'value'),
     Input('cb-dropdown', 'value')]
)
def each_cb_graph(val1,val2):
    df = cb_raw[cb_raw['complaint_type'].isin(val1)]
    df = df.merge(nta_data)
    df = df[df['NTA'] == val2]

    NTA = df.iloc[0]['NTA']

    fig = px.line(df, 
                  x="date", 
                  y="rolling_avg", 
                  color = 'complaint_type',
                  title=f"{val1} in {NTA}",
                  labels={
                     "date": "Date",
                     "rolling_avg": "3-Day Rolling Avg.",
                     "complaint_type": "Complaint Type"
                 }
                  )
    fig.update_layout(
    font_family="Georgia, serif",
    font_color="black",
    title_font_family="Georgia"
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
    df = df.merge(nta_data)
    NTA = df.iloc[0]['NTA']

    fig = px.line(df, 
                  x="date", 
                  y="rolling_avg", 
                  color = 'complaint_type',
                  title=f"{value_chosen} in {NTA}",
                  labels={
                     "date": "Date",
                     "rolling_avg": "3-Day Rolling Avg.",
                     "complaint_type": "Complaint Type"
                 }
                  )
    fig.update_layout(
    font_family="Georgia, serif",
    font_color="black",
    title_font_family="Georgia"
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