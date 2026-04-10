import streamlit as st
import pandas as pd

from shared.api_client import get_person_details

# Config
st.set_page_config(page_title="Graph CRM", layout="wide")

# --- UI Sidebar ---
st.sidebar.title("🔍 Search")
person_id = st.sidebar.text_input("Person ID", placeholder="Enter UUID...")

# --- Main Dashboard ---
if not person_id:
    st.title("Welcome to Graph CRM")
    st.info("Enter a Person ID in the sidebar to view their full profile and network.")
else:
    data = get_person_details(person_id)
    
    if data:
        st.title(f"👤 {data['name']}")
        
        # Displaying the Company info
        comp = data.get('company')
        if comp:
            st.info(f"🏢 **{comp['name']}** ({comp['industry']})")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Details")
            st.write(f"**Title:** {data.get('job_title')}")
            st.write(f"**Email:** {data.get('email')}")
            
            st.subheader("🗓️ Last Interactions")
            for inter in data.get('interactions', []):
                st.write(f"**{inter['date'][:10]} ({inter['type']}):** {inter['notes']}")

        with col2:
            st.subheader("💰 Active Leads")
            leads = data.get('leads', [])
            if leads:
                df_leads = pd.DataFrame(leads)
                st.table(df_leads)
            else:
                st.write("No leads found for this contact.")

    else:
        st.error("Could not find a person with that ID. Please check the backend connection.")