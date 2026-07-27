import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

dataset = pd.read_csv('data/Missing_Migrants_Global_Figures_cleaned.csv')

dataset[['Latitude', 'Longitude']] = dataset['Coordinates'].str.split(',', expand=True).astype(float)
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



dataset["Region of Incident"] = dataset.apply(
    lambda row: assign_region(row["Latitude"], row["Longitude"]), axis=1
)

# preparing and cleaning working dataset

df = dataset.copy()
top5_cause_of_death = (
    df.groupby('Cause of Death')["Total Number of Dead and Missing"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

# Remove Mixed or Unknown
filtered_causes = [c for c in top5_cause_of_death if c != "Mixed or unknown"]

df_top4_cause_of_death = df[df['Cause of Death'].isin(filtered_causes)]

heat_df = (
    df_top4_cause_of_death.groupby(['Cause of Death', 'Region of Incident', 'Incident Year'])["Total Number of Dead and Missing"]
    .sum()
    .reset_index()
)

# Convert Year to string
heat_df['Incident Year'] = heat_df['Incident Year'].astype(str)


heat_df['Continent'] = heat_df['Region of Incident']
continent_mapping = {
    'Middle East':'Asia',
    'South Asia':'Asia',
    'Southeast Asia':'Asia',
    'Central Asia':'Asia',
    'East Asia':"Asia",

    'West Africa':'Africa',
    'North Africa':'Africa',
    'Sub-Saharan Africa':'Africa',
    
    'South America':"Americas",
    'Central America':"Americas",
    'North America':"Americas",
    'Caribbean':"Americas"
}

heat_df['Continent'] = heat_df['Continent'].replace(continent_mapping)

#Selector Parameter
region_selection = alt.selection_point(fields=['Region of Incident'], empty=True) # if nothing is selected, show all on='click' # user clicks to select 
year_selection = alt.selection_point(fields=['Incident Year'], empty=True)
continents = sorted(heat_df['Continent'].dropna().unique().tolist())

params = []
for cont in continents:
    param_name = cont.replace(' ', '_')
    p = alt.param(
        name=param_name,
        value=True,
        bind=alt.binding_checkbox(name=cont)
    )
    params.append(p)

# Build the filter expression string 
expr_parts = [
    f"((datum.Continent == '{cont}') && {cont.replace(' ', '_')})"
    for cont in continents
]
filter_expr = " || ".join(expr_parts)

#Four Heatmaps
region_order = ['Caribbean', 'Central America', 'Central Asia', 'East Asia', 'Europe',
                'Middle East', 'North Africa', 'North America', 'South America', 'South Asia', 'Southeast Asia',
                'Sub-Saharan Africa', 'West Africa']

heatmap_drowning = alt.Chart(heat_df).transform_filter(alt.datum["Cause of Death"] == "Drowning").transform_filter(filter_expr).transform_filter(year_selection).mark_rect().encode(
        x=alt.X("Incident Year:N", sort="ascending", title="Year", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Region of Incident:N", sort=region_order, title="Subregion"),
        color=alt.Color("Total Number of Dead and Missing:Q",
                        scale=alt.Scale(scheme="tealblues"),
                        title="Deaths"),
        opacity=alt.condition(region_selection, alt.value(1), alt.value(0.1))
    ).properties(width=475, height=300, title=alt.Title('Drowning', font='Times New Roman', fontSize=22)).add_params(region_selection, *params)

heatmap_hazardous_transport = alt.Chart(heat_df).transform_filter(alt.datum["Cause of Death"] == "Vehicle accident / death linked to hazardous transport"
        ).transform_filter(filter_expr).transform_filter(year_selection).mark_rect().encode(
        x=alt.X("Incident Year:N", sort="ascending", title="Year", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Region of Incident:N", sort=region_order, title="Subregion"),
        color=alt.Color("Total Number of Dead and Missing:Q",
                        scale=alt.Scale(scheme="warmgreys"),
                        title="Deaths"),
        opacity=alt.condition(region_selection, alt.value(1), alt.value(0.1))
    ).properties(width=475, height=300, title=alt.Title('Hazardous Transport', font='Times New Roman', fontSize=22)).add_params(region_selection, *params)

heatmap_harsh_conditions = alt.Chart(heat_df).transform_filter(alt.datum["Cause of Death"] == "Harsh environmental conditions / lack of adequate shelter, food, water"
        ).transform_filter(filter_expr).transform_filter(year_selection).mark_rect().encode(
        x=alt.X("Incident Year:N", sort="ascending", title="Year", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Region of Incident:N", sort=region_order, title="Subregion"),
        color=alt.Color("Total Number of Dead and Missing:Q",
                        scale=alt.Scale(scheme="greens"),
                        title="Deaths"),
        opacity=alt.condition(region_selection, alt.value(1), alt.value(0.1))
    ).properties(width=475, height=300,  title=alt.Title('Harsh Environmental Conditions', font='Times New Roman', fontSize=22)).add_params(region_selection, *params)
        
heatmap_violence = alt.Chart(heat_df).transform_filter(alt.datum["Cause of Death"] == "Violence"
        ).transform_filter(filter_expr).transform_filter(year_selection).mark_rect().encode(
        x=alt.X("Incident Year:N", sort="ascending", title="Year", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Region of Incident:N", sort=region_order, title="Subregion"),
        color=alt.Color("Total Number of Dead and Missing:Q",
                        scale=alt.Scale(scheme="reds"),
                        title="Deaths"),
        opacity=alt.condition(region_selection, alt.value(1), alt.value(0.1))
    ).properties(width=475, height=300, title=alt.Title('Violence', font='Times New Roman', fontSize=22)).add_params(region_selection, *params)
        

#Final Heatmap View
top_row = (heatmap_drowning | heatmap_hazardous_transport).resolve_scale(color='independent')
bottom_row = (heatmap_harsh_conditions | heatmap_violence).resolve_scale(color='independent')
heatmap_final = alt.vconcat(top_row, bottom_row
                ).properties(title = alt.Title('Top 4 Reasons for Immigration Deaths and Inicidents',
                            font = 'Times New Roman', fontWeight='bold', fontSize=35, anchor='middle',
                            subtitle = 'These 4 Reasons Cause 80% of Immigration Deaths and Incidents',
                            subtitleFont='Times New Roman', subtitleFontWeight='normal', subtitleFontSize=30, offset=40)
                )

#Multipl-line Chart
line_df = heat_df.groupby(['Cause of Death', 'Incident Year', 'Region of Incident', 'Continent'])['Total Number of Dead and Missing'].sum().reset_index()
line_chart = alt.Chart(line_df).transform_filter(filter_expr).transform_filter(region_selection).mark_line(point=True).encode(
    x = alt.X('Incident Year:O', axis=alt.Axis(labelAngle=0)),
    y = alt.Y('sum(Total Number of Dead and Missing):Q', title = "Number of Dead and Missing"),
    color = alt.Color('Cause of Death:N', scale=alt.Scale(range=['steelblue', 'green', 'black', 'red'])),
    tooltip = ['Incident Year']
).properties(width = 1000).add_params(year_selection, *params)




#Combined View
final_chart = alt.vconcat(heatmap_final, line_chart).resolve_legend(color='independent')

st.altair_chart(final_chart, use_container_width=False)