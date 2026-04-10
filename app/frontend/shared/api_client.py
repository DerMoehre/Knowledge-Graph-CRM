import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("API_URL", "http://backend:8000")
API_KEY = os.getenv("APP_API_KEY")

def get_person_details(person_id):
    try:
       response = requests.get(
            f"{BACKEND_URL}/people/{person_id}/details", 
            headers={"X-API-Key": API_KEY},
            timeout=5)
       
       if response.status_code == 200:
            return response.json() 
       elif response.status_code == 403:
            st.error("API Key rejected by backend.")
       return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None
    
def get_full_graph():
    try:
        response = requests.get(
            f"{BACKEND_URL}/graph/full",
            headers={"X-API-Key": API_KEY},
            timeout=10)

        if response.status_code == 200:
            return response.json().get("graph", [])
        elif response.status_code == 403:
            st.error("API Key rejected by backend.")
        return []
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return []