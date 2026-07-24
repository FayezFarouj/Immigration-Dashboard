import streamlit as st

pages = {
    "List of Dashboards": [
        st.Page('pages/overview.py', title='Overview'),
        st.Page('pages/view1.py', title='Immigration Incidents by Country of Incident'),
        
    ]
}

pg = st.navigation(pages, position="top")

pg.run()
