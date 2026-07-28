import pandas as pd
import altair as alt
import streamlit as st

from vega_datasets import data

#Title and configuration
st.set_page_config(layout="wide")
st.markdown(
    """
    <h1 style='font-family: Times New Roman; font-size: 45px; text-align: center;'>
        Global Distribution of Immigration Deaths and Incidents
    </h1>
    """,
    unsafe_allow_html=True
)

alt.renderers.enable('html')
alt.data_transformers.enable("vegafusion")

# updating the values in the 'Region of Incident' column to get better alignment based on the coordinates
# of the incident:
def assign_region(lat, lon):
    # Asia subregion
    if 10 <= lat <= 45 and 25 <= lon <= 65:
        return "Middle East"
    elif 5 <= lat <= 35 and 65 <= lon <= 95:
        return "South Asia"
    elif 20 <= lat <= 55 and 95 <= lon <= 140:
        return "East Asia"
    elif -10 <= lat <= 20 and 95 <= lon <= 150:
        return "Southeast Asia"
    
    # Africa subregions
    elif 15 <= lat <= 37 and -23 <= lon <= 40:
        return "North Africa"
    elif 0 <= lat <= 24 and -25 <= lon <= 20:
        return "West Africa"
    # Sub-Saharan Africa: rest below ~15N
    elif -35 <= lat < 15 and -20 <= lon <= 55:
        return "Sub-Saharan Africa"
    elif 35 <= lat <= 70 and -10 <= lon <= 57:
        return "Europe"
    
    # Americas
    elif 10 <= lat <= 30 and -90 <= lon <= -60:
        return "Caribbean"
    elif 7 <= lat <= 20 and -102 <= lon <= -75:
        return "Central America"
    elif -55 <= lat <= 12 and -85 <= lon <= -30:
        return "South America"
    elif 20 <= lat <= 75 and -170 <= lon <= -50:
        return "North America"
    
    # Oceania
    elif -50 <= lat <= 0 and 110 <= lon <= 180:
        return "Oceania"

    else:
        return "Central Asia"

@st.cache_data
def load_data():
    dataset = pd.read_csv("data/Missing_Migrants_Global_Figures_cleaned.csv")

    dataset[['Latitude', 'Longitude']] = (
        dataset['Coordinates']
        .str.split(',', expand=True)
        .astype(float)
    )

    dataset["Region of Incident"] = dataset.apply(
        lambda row: assign_region(row["Latitude"], row["Longitude"]),
        axis=1
    )
    
    name_map = {
    'Syrian Arab Republic': 'Syria',
    'Iran (Islamic Republic of)': 'Iran',
    "Côte d'Ivoire": "Cote d'Ivoire",
    "Democratic Republic of the Congo": "Democratic Republic of Congo",
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'State of Palestine': 'Palestinian Territory, Occupied',
    'Republic of Korea': 'South Korea',
    "Lao People's Democratic Republic": 'Laos',
    'Russian Federation': 'Russia',
    "Democratic People's Republic of Korea": "Korea, Democratic People's Republic of",
    "Taiwan": "Taiwan, Province of China",
    "United Kingdom of Great Britain and Northern Ireland" : 'UK'
    }

    dataset['Country of Origin'] = dataset['Country of Origin'].replace(name_map)
    dataset['Country of Incident'] = dataset['Country of Incident'].replace(name_map)
    
    dataset['Death_Size'] = pd.cut(dataset['Total Number of Dead and Missing'], bins=4, labels=False)

    return dataset


df = load_data()

#Bounds for the zoomed map
bounds = {
    "Please Choose a Region": [1590, 0],
    
    "North Africa": [250, 450],
    "West Africa": [320, 280],
    "Sub-Saharan Africa": [10, 50],
    
    "Middle East": [-200, 500],
    "South Asia": [-500, 425],
    "East Asia": [-1000, 600],
    "Southeast Asia": [-900, 290],
    
    "Europe": [120, 775],
    
    "Caribbean": [1200, 420],
    "Central America": [1300, 400],
    "South America": [1000, 100],
    "North America": [1350, 610],
    
    "Oceania": [-850, -50],
    "Central Asia": [-400, 675]
}

#UI parameters
regions =  sorted(df['Region of Incident'].unique())

years = sorted(df['Incident Year'].unique())
year_slider = alt.binding_range(min=min(years), max=max(years), step=1, name="Year:")


year_select = alt.selection_point(fields=['Incident Year'])

pt_select = alt.selection_point(fields=['Region of Incident'], empty=True)

#World map
world_map = alt.topo_feature(data.world_110m.url, "countries")

bar = alt.Chart(df).mark_bar().encode(
        x=alt.X('Incident Year:O', title='Year', axis=alt.Axis(labelAngle=0, labelLimit=300)),
        y=alt.Y('sum(Total Number of Dead and Missing):Q', title='Deaths'),
        color=alt.condition(year_select, alt.value("steelblue"), alt.value("lightgrey"))
    ).transform_filter(pt_select).add_params(year_select).properties(width = 900, height=250)

# World background
title = alt.TitleParams(
    text=alt.expr("'Global Distribution of Immigration Incidents in ' + toString(year_select)")
)
background = alt.Chart(world_map).transform_filter(alt.datum.id != 10).mark_geoshape(fill="lightgray", stroke="grey"
    ).project(type="equalEarth", scale=1600, center=[20, 20]
    ).properties(width=900, height=600, 
                title = alt.Title("Global Distribution of Immigration Incidents", font ='Times New Roman', 
                                fontSize=40, fontWeight="bold")).project("equalEarth")

# Points on main world map (by region color)
points = alt.Chart(df).mark_circle(opacity=0.6).encode(
        longitude="Longitude:Q",
        latitude="Latitude:Q",
        size = alt.Size('Total Number of Dead and Missing:Q',
                        bin=alt.Bin(maxbins=4),
                        scale=alt.Scale(range=[10, 100]),
                        legend=alt.Legend(title = "Number of Dead and Missing")),
        color=alt.Color("Region of Incident:N", scale=alt.Scale(
                        domain=regions, scheme="set1"),
                        legend=alt.Legend(title='Region of Incident')),
        tooltip=['Incident Year', "Region of Incident", "Total Number of Dead and Missing"]
    ).transform_filter(year_select).project(
                type="equalEarth").add_params(pt_select)

main_viz = ((background + points) & bar)

def make_layout(region):
    
    if region == "Select a region":
        return alt.Chart(pd.DataFrame({"x": []})).mark_point().properties(width=0, height=0)
    # Zoomed base map
    base_zoom = alt.Chart(world_map).mark_geoshape(fill="lightgrey", stroke="black").project(
            type="mercator",
            scale=600,
            translate=bounds.get(region, bounds["Please Choose a Region"])
        ).properties(width=650, height=400)

    pts_zoom = alt.Chart(df).transform_calculate(
                Migration_Route_Status="datum['Migration Route'] == null ? 'Missing' : 'Present'"
            ).mark_circle(opacity=0.7).encode(
                longitude="Longitude:Q",
                latitude="Latitude:Q",
                size = alt.Size('Death_Size:Q',
                                scale=alt.Scale(range=[20, 200]),
                                legend = alt.Legend(title='Number of Dead and Missing')),
                fill=alt.Fill(
                            "Migration_Route_Status:N",
                            legend = alt.Legend(title = 'Migration Route Info'),
                            scale=alt.Scale(
                                    domain=["Missing", "Present"],
                                    range=["red", "green"])),
                tooltip=['Total Number of Dead and Missing:Q', 'Country of Origin', 'Country of Incident', "Migration Route:N"]
            ).transform_filter(
                (alt.datum["Region of Incident"] == region) &
                (alt.datum["Incident Year"] == year_param)
            ).project(
                type="mercator",
                scale=800,
                translate=bounds.get(region, bounds["Please Choose a Region"])
            ).properties(width=650, height=400)
            
    bar_zoom = alt.Chart(df).transform_filter((alt.datum["Region of Incident"] == region) &
                        (alt.datum["Incident Year"] == year_param)).transform_aggregate(
        total_dead="sum(Total Number of Dead and Missing)",
        groupby=["Country of Incident", "Region of Incident"]
    ).transform_window(
        rank="rank(total_dead)",
        sort=[{"field": "total_dead", "order": "descending"}]
    ).mark_bar().encode(
        y=alt.Y("total_dead:Q", title = 'Number of Dead and Missing'),
        x=alt.X(
            "Country of Incident:N",
            sort=alt.SortField(field="total_dead", order="descending"),
            title='Year', axis=alt.Axis(labelAngle=-45, labelLimit=300))
    ).properties(width = 450, height = 400)

    # Full layout: main map on top, bar + zoom side by side
    full_chart =  ((base_zoom + pts_zoom) | bar_zoom).resolve_scale(
        size="independent",
        fill='independent',
        color='independent'
    ).resolve_legend('independent')
    return full_chart


## Streamlit controls

st.altair_chart(main_viz, use_container_width=True)

region_dropdown_options = st.selectbox(
    "Zoom Region:",
    options=['Select a region'] + regions
)
year_param = st.slider(
    "Year:",
    min_value=min(years),
    max_value=max(years),
    value=min(years),
    step=1
)

if region_dropdown_options != "Select a region":
    zoom_chart = make_layout(region_dropdown_options)
    st.altair_chart(zoom_chart, use_container_width=True)
