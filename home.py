import streamlit as st

pages = {
    "List of Dashboards": [
        st.Page('pages/overview.py', title='Overview'),
        st.Page('pages/view1.py', title='Immigration Incidents by Country of Incident'),
        st.Page('pages/view2.py', title='Immigration Incdients by Country of Origin'),
        
    ]
}

pg = st.navigation(pages, position="top")

pg.run()
