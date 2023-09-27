import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import base64

API_URL = "https://data.cms.gov/data-api/v1/dataset/ea1882e5-27cd-43fe-aaae-eab50bc1b7d7/data?filter[Rndrng_Prvdr_State_Abrvtn]=FL"

@st.cache_data  # Replaced st.cache to resolve the deprecation warning
def load_data():
    """
    Load data from the API
    """
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error('Failed to load data from API')
        return pd.DataFrame()

def app():
    st.title('Medicare Outpatient Hospitals Report')

    # Load the data
    df = load_data()
    
    if df.empty:
        st.write('Failed to load data')
        return
    
    st.sidebar.header('Filters')
    
    # Corrected the column names here
    states = st.sidebar.multiselect('State', df['Rndrng_Prvdr_State_Abrvtn'].unique())
    cities = st.sidebar.multiselect('City', df['Rndrng_Prvdr_City'].unique())
    apc_descs = st.sidebar.multiselect('APC_Desc', df['APC_Desc'].unique())  # Corrected column name
    
    # Apply filters with corrected column names
    if states:
        df = df[df['Rndrng_Prvdr_State_Abrvtn'].isin(states)]
    if cities:
        df = df[df['Rndrng_Prvdr_City'].isin(cities)]
    if apc_descs:
        df = df[df['APC_Desc'].isin(apc_descs)]  # Corrected column name
    
    st.header('Report')
    st.dataframe(df)

    # Export to Excel
    if not df.empty:
        excel_file = BytesIO()
        df.to_excel(excel_file, engine='openpyxl', index=False)
        excel_file.seek(0)
        b64 = base64.b64encode(excel_file.read()).decode()
        link = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="filtered_data.xlsx">Download Excel File</a>'
        st.markdown(link, unsafe_allow_html=True)

if __name__ == "__main__":
    app()
