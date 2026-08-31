import streamlit as st
import pandas as pd
import altair as alt

from vega_datasets import data


st.set_page_config(layout="wide")

with st.expander("How to explore this dashboard", expanded=False):
    st.markdown("""
        <div style="background-color: #D0FFD0;
            border-left: 5px solid #4CAF50;
            padding: 12px 18px;
            margin-top: 25px;
            margin-bottom: 30px;
            font-family: Georgia, serif;
            font-size: 18px;
            font-weight: 700;
            color: #333;
        ">
        
    **Select a year from the dropdown**
    → Update the world map and the donut chart.

    **Click a country on the donut chart**
    → Highlight its trend in the line chart for comparison with other countries.

    **Click a country on the map**
    → Highlight its trend in the line chart for comparison with other countries.

    **Hover over countries, donut segments, or line points**
    → View detailed information and exact values.
        </div>
    """, unsafe_allow_html=True)

dataset = pd.read_csv('data/Missing_Migrants_Global_Figures_cleaned.csv')
    
country_ids = pd.read_csv('https://raw.githubusercontent.com/kemiolamudzengi/dsci-320-datasets/main/country-ids-and-continents.csv')
relevant_country_names = country_ids["Country"]
    
df = dataset.copy()
df = df[['Country of Origin', 'Total Number of Dead and Missing', 'Incident Year']]
    
# Split by comma
df['Country of Origin'] = df['Country of Origin'].str.split(',')

# Explode into separate rows
df = df.explode('Country of Origin')

# Strip whitespace
df['Country of Origin'] = df['Country of Origin'].str.strip()

# Standarize country names to match the relevant_country_names
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
} 

df['Country of Origin'] = df['Country of Origin'].replace(name_map)
    
country_agg = df.groupby(['Country of Origin', 'Incident Year'], as_index=False
).agg({'Total Number of Dead and Missing': 'sum'})
    
    
choropleth_dataset  = (country_agg).rename(
    columns={'Country of Origin': 'Country'}).merge(country_ids) # Now each row has: Country, Incident Year, sum, ID

choropleth_dataset = choropleth_dataset.groupby(["Country", "Incident Year"], as_index=False).agg({
    "Total Number of Dead and Missing": "sum",   # or max, min, median
    "ID": "first"})         # keep the country ID for joining

def categorize(number):
    if (number > 1000):
        return 60
    elif (number > 500):
        return 50
    elif (number > 200):
        return 40
    elif (number > 100):
        return 30
    elif (number > 50):
        return 20
    else:
        return 10
        
choropleth_dataset['Category'] = choropleth_dataset['Total Number of Dead and Missing'].apply(categorize)
choropleth_dataset["Category"] = choropleth_dataset["Category"].astype(str)

# WORLD MAP
world_map_2 = alt.topo_feature(data.world_110m.url, 'countries')

# selector

country_select = alt.selection_point(fields=["Country"], empty=False)

# background
background_2 = alt.Chart(world_map_2).transform_filter(alt.datum.id != 10).mark_geoshape(
    fill="lightgray", stroke="black")

# choropleth function
def make_choropleth(year):
    df = choropleth_dataset[choropleth_dataset["Incident Year"] == year]

    df_top5 = df.groupby("Country", as_index=False)["Total Number of Dead and Missing"].sum(
        ).sort_values("Total Number of Dead and Missing", ascending=False).head(5)
    
    
    choropleth = alt.Chart(world_map_2).transform_filter(alt.datum.id != 10).transform_lookup(
            lookup="id",
            from_=alt.LookupData(
                df,
                key="ID",
                fields=["Country", "Incident Year", "Total Number of Dead and Missing"],
            )).mark_geoshape(stroke="black").encode(
            tooltip=[
                "Country:N",
                "Incident Year:Q",
                "Total Number of Dead and Missing:Q",],
            color=alt.Color(
                "Total Number of Dead and Missing:Q",
                scale=alt.Scale(scheme="oranges", domainMin=0),
                title = "Total Number of Dead and Missing",
                legend=alt.Legend(orient='top', padding = 0)),
                strokeWidth=alt.condition(country_select, alt.value(3), alt.value(0.5)),
        ).add_params(country_select)
        
    line_chart = alt.Chart(choropleth_dataset).transform_filter(country_select).mark_line(point=True).encode(
        x="Incident Year:O",
        y="Total Number of Dead and Missing:Q",
        color=alt.Color("Country:N", title="Selected Countries", legend=alt.Legend(orient='right', padding=5)),
        tooltip = ["Incident Year:O", 'Country:N', "Total Number of Dead and Missing:Q" ]
    ).transform_filter(country_select
    ).properties(height=300, width=350,
                title=alt.Title("Trend of Selected Countries Over Years",
                        font ='Times New Roman', fontSize=24, fontWeight="bold",
                        subtitle="Select countries by clicking on the map or the donut chart",
                        subtitleFont='Times New Roman', subtitleFontWeight='normal', subtitleFontSize=18)
                )
    
    donut = alt.Chart(df_top5).transform_calculate(
        Year=f'"{int(year)}"'
        ).mark_arc(innerRadius=60, outerRadius=130).encode(
        theta="Total Number of Dead and Missing",
        fill=alt.Fill("Country:N", title = "Top 5 Countries",legend=alt.Legend(orient='right', padding=40)),
        tooltip=[
            alt.Tooltip("Country:N", title="Country"),
            alt.Tooltip('Year:Q', title='Year'),
            alt.Tooltip("Total Number of Dead and Missing:Q", title="Deaths"),
        ]).properties(
            height=250, width=220,  title = alt.Title("Top 5 Countries by # of Dead & Missing in " + str(selected_year),
                                        font ='Times New Roman', fontSize=22, fontWeight="bold")
        ).add_params(country_select)
        
    map_layer = (background_2 + choropleth).project(
        "equalEarth", scale=220, translate=[400, 380]
        ).properties(width=950,height=900)
    
    map_chart = alt.hconcat(map_layer, alt.vconcat(donut, line_chart).resolve_legend(color='independent', fill='independent')).resolve_scale(color='independent', fill='independent')
    
    return map_chart

years = sorted(choropleth_dataset["Incident Year"].unique())

selected_year = st.selectbox(
    "Year:",
    options=years,
    index=0
)

map_chart = make_choropleth(selected_year)

st.markdown(
    f"""
    <h1 style='font-family: Times New Roman; font-size: 40px; text-align: center;'>
        Distribution of Dead and Missing Immigrants by Country of Origin in {selected_year}
    </h1>
    
    <h2 style='font-family: Times New Roman; font-size:24px; text-align: center;
    color: #D32F2F;'>
        Open "How to explore" to discover how to interact with this dashboard
    </h2>
    
    """,
    unsafe_allow_html=True
) 

st.altair_chart(map_chart, use_container_width=False)

