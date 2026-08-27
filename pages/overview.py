import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
<div style="
    font-family: Georgia, serif;
    font-size: 45px;
    font-weight: bold;
    text-align: center;
">
    Immigration Dashboards Project: A Visual Exploration of Global Immigration Incidents and Deaths
    
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    background-color: #fff0f0;
    border-left: 5px solid #D32F2F;
    padding: 12px 18px;
    margin-top: 25px;
    margin-bottom: 30px;
    font-family: Arial, sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #D32F2F;
">
    ⚠️ Please use the dropdown menu in the top-left corner to explore the different dashboards.
</div>
""", unsafe_allow_html=True)

st.markdown("""

<div style="
    font-family: Georgia, serif;
    font-size: 20px;
    font-weight: 700;
">

This project consists of three geospatial dashboards that work together to reveal how migration
incidents evolve across time, geography, and routes. 

The **first dashboard** helps expolre the geographic distribution of incidents and how their 
distrubtion has changed over time. The **second dashboard** shows the countries of origin of victims, highlighting
patterns in social and immigration injustices. The **third dahsboard** focues on causes of death, it compares 
the common causes of immigration incidents across continents and smaller geographic regions, and shows those 
patterns has changed over time through and interactive heatmap and line chart. Together, these views form a cohesive narrative that helps users 
interpret complex data through multiple perspectives.

In building the visualizations, design principles such as Gestalt grouping, 
separability, discriminability, and channel accuracy were applied to keep the views clear and accessible. 
Consistent encodings were used to help users track patterns across charts without 
cognitive overload. These choices were important because one of the core goals of this project
was to reduce information  gaps that often exist in discussions about immigration. By transforming raw incident 
records into  interpretable visual narratives, we aim to make the data more transparent, highlight areas where
reporting is incomplete, and encourage further research into regions or routes that show persistent risk.

Overall, the three dashboards are meant to support better decision-making. Immigrants and advocacy groups can 
use the insights to understand high-risk areas, researchers can identify patterns that warrant deeper investigation, 
and policy makers can better allocate resources and attention. While the dataset is imperfect, presenting it through 
clear and thoughtful design offers a starting point for more informed dialogue and safer migration pathways.

</div>
""", unsafe_allow_html=True)

