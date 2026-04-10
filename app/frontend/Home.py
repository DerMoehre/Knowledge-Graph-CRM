import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

from shared.api_client import get_full_graph

# Config
st.set_page_config(page_title="Graph CRM", layout="wide")

# --- UI Sidebar ---
st.sidebar.title("Overview")

# --- Main Dashboard ---
st.title("Welcome to Graph CRM")
st.info("Use the sidebar to navigate through different sections of the CRM. You can search for people, companies, interactions, and leads. Explore the full graph to see how everything is connected!")

graph_data = get_full_graph()
if graph_data:    
    nodes = {}
    edges = []
    colors = {"Person": "#007bff", "Company": "#ffc107", "Lead": "#dc3545", "Interaction": "#28a745"}

    for item in graph_data:
        source = item["source"]
        target = item["target"]
        relationship = item["relationship"]

        # Add source node
        if source["id"] not in nodes:
            nodes[source["id"]] = Node(
                id=source["id"],
                label=source["name"],
                color=colors.get(source["label"], "#6c757d")
            )
        
        # Add target node
        if target["id"] not in nodes:
            nodes[target["id"]] = Node(
                id=target["id"],
                label=target["name"],
                color=colors.get(target["label"], "#6c757d")
            )
        
        # Add edge
        edges.append(Edge(
            source=source["id"],
            target=target["id"],
            label=relationship
        ))

    config = Config(
        width=1000, 
        height=600, 
        directed=True,
        physics=True, 
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=True,
        node={'labelProperty': 'label', 'color': 'color'},
        edge={'labelProperty': 'label', 'color': '#6c757d'}
    )

    agraph(list(nodes.values()), edges, config)