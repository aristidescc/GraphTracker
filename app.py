import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import requests
import json
from datetime import datetime

# Constants
# Use the IP address that's visible from both services
API_URL = "http://172.31.128.39:8000"

# Page configuration
st.set_page_config(
    page_title="Graph Management System",
    page_icon="🔄",
    layout="wide"
)

# Show a header
st.title("Graph Management System")
st.write("A system for managing directed graphs, tracking visitors, and finding paths")

# Test API connection
st.header("API Connection Test")
try:
    response = requests.get(f"{API_URL}/")
    if response.status_code == 200:
        st.success(f"Successfully connected to API: {response.json()}")
    else:
        st.error(f"Failed to connect to API: {response.status_code}")
except Exception as e:
    st.error(f"Error connecting to API: {str(e)}")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["Graph Management", "Visitor Tracking", "Path Finding", "Logs"])

# Functions to interact with the API
def get_nodes():
    try:
        response = requests.get(f"{API_URL}/nodes")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch nodes: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_edges():
    try:
        response = requests.get(f"{API_URL}/edges")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch edges: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_visitors():
    try:
        response = requests.get(f"{API_URL}/visitors")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch visitors: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_visitor_history(visitor_id):
    try:
        response = requests.get(f"{API_URL}/visitors/{visitor_id}/history")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch visitor history: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_logs():
    try:
        response = requests.get(f"{API_URL}/logs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch logs: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def find_paths(start_node_id, end_node_id):
    try:
        response = requests.get(f"{API_URL}/paths/{start_node_id}/{end_node_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to find paths: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def create_node(name, description=None):
    try:
        data = {"name": name, "description": description}
        response = requests.post(f"{API_URL}/nodes", json=data)
        if response.status_code == 201:
            st.success("Node created successfully!")
            return response.json()
        else:
            st.error(f"Failed to create node: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def update_node(node_id, name, description=None):
    try:
        data = {"name": name, "description": description}
        response = requests.put(f"{API_URL}/nodes/{node_id}", json=data)
        if response.status_code == 200:
            st.success("Node updated successfully!")
            return response.json()
        else:
            st.error(f"Failed to update node: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def delete_node(node_id):
    try:
        response = requests.delete(f"{API_URL}/nodes/{node_id}")
        if response.status_code == 200:
            st.success("Node deleted successfully!")
            return True
        else:
            st.error(f"Failed to delete node: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def create_edge(source_id, target_id, name, weight=1.0):
    try:
        data = {"source_id": source_id, "target_id": target_id, "name": name, "weight": weight}
        response = requests.post(f"{API_URL}/edges", json=data)
        if response.status_code == 201:
            st.success("Edge created successfully!")
            return response.json()
        else:
            st.error(f"Failed to create edge: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def update_edge(edge_id, source_id, target_id, name, weight=1.0):
    try:
        data = {"source_id": source_id, "target_id": target_id, "name": name, "weight": weight}
        response = requests.put(f"{API_URL}/edges/{edge_id}", json=data)
        if response.status_code == 200:
            st.success("Edge updated successfully!")
            return response.json()
        else:
            st.error(f"Failed to update edge: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def delete_edge(edge_id):
    try:
        response = requests.delete(f"{API_URL}/edges/{edge_id}")
        if response.status_code == 200:
            st.success("Edge deleted successfully!")
            return True
        else:
            st.error(f"Failed to delete edge: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def create_visitor(name, current_node_id):
    try:
        data = {"name": name, "current_node_id": current_node_id}
        response = requests.post(f"{API_URL}/visitors", json=data)
        if response.status_code == 201:
            st.success("Visitor created successfully!")
            return response.json()
        else:
            st.error(f"Failed to create visitor: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def move_visitor(visitor_id, edge_id):
    try:
        data = {"edge_id": edge_id}
        response = requests.post(f"{API_URL}/visitors/{visitor_id}/move", json=data)
        if response.status_code == 200:
            st.success("Visitor moved successfully!")
            return response.json()
        else:
            st.error(f"Failed to move visitor: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def visualize_graph(nodes, edges):
    if not nodes or not edges:
        st.warning("No nodes or edges to visualize")
        return
    
    G = nx.DiGraph()
    
    # Add nodes
    for node in nodes:
        G.add_node(node["id"], name=node["name"])
    
    # Add edges
    for edge in edges:
        G.add_edge(edge["source_id"], edge["target_id"], name=edge["name"], weight=edge["weight"])
    
    # Create figure and draw graph
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # Consistent layout
    
    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightblue", alpha=0.8, ax=ax)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color="gray", arrows=True, arrowsize=20, ax=ax)
    
    # Draw node labels
    node_labels = {node["id"]: node["name"] for node in nodes}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, ax=ax)
    
    # Draw edge labels
    edge_labels = {(edge["source_id"], edge["target_id"]): edge["name"] for edge in edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
    
    # Remove axis
    ax.set_axis_off()
    
    # Show plot
    st.pyplot(fig)
    
    return G

# Graph Management Page
if page == "Graph Management":
    st.title("Graph Management")
    
    # Fetch data
    nodes = get_nodes()
    edges = get_edges()
    
    # Display graph visualization
    st.header("Graph Visualization")
    G = visualize_graph(nodes, edges)
    
    # Tabs for node and edge management
    tab1, tab2 = st.tabs(["Nodes", "Edges"])
    
    with tab1:
        st.header("Node Management")
        
        # Show existing nodes
        if nodes:
            st.subheader("Existing Nodes")
            nodes_df = pd.DataFrame(nodes)
            st.dataframe(nodes_df)
        
        # Create new node
        st.subheader("Create New Node")
        with st.form("create_node_form"):
            name = st.text_input("Node Name")
            description = st.text_area("Description (optional)")
            submit_button = st.form_submit_button("Create Node")
            
            if submit_button and name:
                create_node(name, description)
                st.rerun()
        
        # Update or delete node
        st.subheader("Update or Delete Node")
        if nodes:
            node_to_update = st.selectbox(
                "Select Node to Update/Delete",
                options=[node["id"] for node in nodes],
                format_func=lambda x: next((node["name"] for node in nodes if node["id"] == x), "")
            )
            
            selected_node = next((node for node in nodes if node["id"] == node_to_update), None)
            if selected_node:
                with st.form("update_node_form"):
                    update_name = st.text_input("Update Name", value=selected_node["name"])
                    update_description = st.text_area("Update Description", value=selected_node.get("description", ""))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button("Update Node")
                    with col2:
                        delete_button = st.form_submit_button("Delete Node", type="secondary")
                    
                    if update_button and update_name:
                        update_node(node_to_update, update_name, update_description)
                        st.rerun()
                    if delete_button:
                        if delete_node(node_to_update):
                            st.rerun()
    
    with tab2:
        st.header("Edge Management")
        
        # Show existing edges
        if edges:
            st.subheader("Existing Edges")
            
            # Add node names to edges for better display
            edges_with_names = []
            for edge in edges:
                source_name = next((node["name"] for node in nodes if node["id"] == edge["source_id"]), "Unknown")
                target_name = next((node["name"] for node in nodes if node["id"] == edge["target_id"]), "Unknown")
                edge_with_names = edge.copy()
                edge_with_names["source_name"] = source_name
                edge_with_names["target_name"] = target_name
                edges_with_names.append(edge_with_names)
            
            edges_df = pd.DataFrame(edges_with_names)
            st.dataframe(edges_df)
        
        # Create new edge
        st.subheader("Create New Edge")
        if len(nodes) >= 2:  # Need at least 2 nodes to create an edge
            with st.form("create_edge_form"):
                source_node = st.selectbox(
                    "Source Node",
                    options=[node["id"] for node in nodes],
                    format_func=lambda x: next((node["name"] for node in nodes if node["id"] == x), "")
                )
                target_node = st.selectbox(
                    "Target Node",
                    options=[node["id"] for node in nodes],
                    format_func=lambda x: next((node["name"] for node in nodes if node["id"] == x), "")
                )
                edge_name = st.text_input("Edge Name")
                weight = st.number_input("Weight", min_value=0.1, value=1.0, step=0.1)
                
                submit_button = st.form_submit_button("Create Edge")
                
                if submit_button and edge_name and source_node != target_node:
                    create_edge(source_node, target_node, edge_name, weight)
                    st.rerun()
                elif submit_button and source_node == target_node:
                    st.error("Source and target nodes must be different")
        else:
            st.warning("You need at least 2 nodes to create an edge")
        
        # Update or delete edge
        st.subheader("Update or Delete Edge")
        if edges:
            edge_to_update = st.selectbox(
                "Select Edge to Update/Delete",
                options=[edge["id"] for edge in edges],
                format_func=lambda x: next((f"{edge['name']} ({next((node['name'] for node in nodes if node['id'] == edge['source_id']), '')}->{next((node['name'] for node in nodes if node['id'] == edge['target_id']), '')})" for edge in edges if edge["id"] == x), "")
            )
            
            selected_edge = next((edge for edge in edges if edge["id"] == edge_to_update), None)
            if selected_edge:
                with st.form("update_edge_form"):
                    update_source = st.selectbox(
                        "Update Source Node",
                        options=[node["id"] for node in nodes],
                        index=[i for i, node in enumerate(nodes) if node["id"] == selected_edge["source_id"]][0],
                        format_func=lambda x: next((node["name"] for node in nodes if node["id"] == x), "")
                    )
                    update_target = st.selectbox(
                        "Update Target Node",
                        options=[node["id"] for node in nodes],
                        index=[i for i, node in enumerate(nodes) if node["id"] == selected_edge["target_id"]][0],
                        format_func=lambda x: next((node["name"] for node in nodes if node["id"] == x), "")
                    )
                    update_name = st.text_input("Update Name", value=selected_edge["name"])
                    update_weight = st.number_input("Update Weight", min_value=0.1, value=selected_edge["weight"], step=0.1)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button("Update Edge")
                    with col2:
                        delete_button = st.form_submit_button("Delete Edge", type="secondary")
                    
                    if update_button and update_name and update_source != update_target:
                        update_edge(edge_to_update, update_source, update_target, update_name, update_weight)
                        st.rerun()
                    elif update_button and update_source == update_target:
                        st.error("Source and target nodes must be different")
                    if delete_button:
                        if delete_edge(edge_to_update):
                            st.rerun()

# Visitor Tracking Page
elif page == "Visitor Tracking":
    st.title("Visitor Tracking")
    
    # Fetch data
    nodes = get_nodes()
    edges = get_edges()
    visitors = get_visitors()
    
    # Display graph visualization
    st.header("Graph Visualization")
    G = visualize_graph(nodes, edges)
    
    # Create new visitor
    st.header("Create New Visitor")
    if nodes:
        with st.form("create_visitor_form"):
            visitor_name = st.text_input("Visitor Name")
            starting_node = st.selectbox(
                "Starting Node",
                options=[node["id"] for node in nodes],
                format_func=lambda x: next((node["name"] for node in nodes if node["id"] == x), "")
            )
            
            submit_button = st.form_submit_button("Create Visitor")
            
            if submit_button and visitor_name:
                create_visitor(visitor_name, starting_node)
                st.rerun()
    else:
        st.warning("You need to create nodes first")
    
    # Visitor movement
    st.header("Visitor Movement")
    if visitors and edges:
        visitor_to_move = st.selectbox(
            "Select Visitor",
            options=[visitor["id"] for visitor in visitors],
            format_func=lambda x: next((visitor["name"] for visitor in visitors if visitor["id"] == x), "")
        )
        
        selected_visitor = next((visitor for visitor in visitors if visitor["id"] == visitor_to_move), None)
        if selected_visitor:
            st.info(f"Current location: {next((node['name'] for node in nodes if node['id'] == selected_visitor['current_node_id']), 'Unknown')}")
            
            # Get available edges from current node
            available_edges = [
                edge for edge in edges 
                if edge["source_id"] == selected_visitor["current_node_id"]
            ]
            
            if available_edges:
                edge_to_travel = st.selectbox(
                    "Select Edge to Travel",
                    options=[edge["id"] for edge in available_edges],
                    format_func=lambda x: next((f"{edge['name']} → {next((node['name'] for node in nodes if node['id'] == edge['target_id']), '')}" for edge in available_edges if edge["id"] == x), "")
                )
                
                if st.button("Move Visitor"):
                    move_result = move_visitor(visitor_to_move, edge_to_travel)
                    if move_result:
                        st.rerun()
            else:
                st.warning("No available edges to travel from current node")
            
            # Show visitor history
            st.subheader("Visitor Movement History")
            history = get_visitor_history(visitor_to_move)
            if history:
                history_df = pd.DataFrame(history)
                # Convert timestamp to readable format
                history_df["timestamp"] = pd.to_datetime(history_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                st.dataframe(history_df)
            else:
                st.info("No movement history yet")
    else:
        st.warning("You need to create visitors and edges first")

# Path Finding Page
elif page == "Path Finding":
    st.title("Path Finding")
    
    # Fetch data
    nodes = get_nodes()
    edges = get_edges()
    
    # Display graph visualization
    st.header("Graph Visualization")
    G = visualize_graph(nodes, edges)
    
    # Path finding form
    st.header("Find Paths")
    if len(nodes) >= 2:  # Need at least 2 nodes to find paths
        col1, col2 = st.columns(2)
        with col1:
            start_node = st.selectbox(
                "Start Node",
                options=[node["id"] for node in nodes],
                format_func=lambda x: next((node["name"] for node in nodes if node["id"] == x), "")
            )
        with col2:
            end_node = st.selectbox(
                "End Node",
                options=[node["id"] for node in nodes],
                format_func=lambda x: next((node["name"] for node in nodes if node["id"] == x), "")
            )
        
        if st.button("Find Paths"):
            if start_node != end_node:
                paths = find_paths(start_node, end_node)
                if paths:
                    st.success(f"Found {len(paths)} path(s)")
                    
                    for i, path in enumerate(paths, 1):
                        st.subheader(f"Path {i}")
                        path_str = " → ".join([node_info["name"] for node_info in path["nodes"]])
                        st.write(path_str)
                        
                        # Display edges in the path
                        st.write("Edges to travel:")
                        for edge in path["edges"]:
                            st.write(f"- {edge['name']}")
                else:
                    st.warning("No paths found between these nodes")
            else:
                st.error("Start and end nodes must be different")
    else:
        st.warning("You need at least 2 nodes to find paths")

# Logs Page
elif page == "Logs":
    st.title("Operation Logs")
    
    # Fetch logs
    logs = get_logs()
    
    # Display logs
    if logs:
        # Convert to dataframe for better display
        logs_df = pd.DataFrame(logs)
        # Convert timestamp to readable format
        logs_df["timestamp"] = pd.to_datetime(logs_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Add filters
        st.header("Filter Logs")
        operation_types = ["All"] + sorted(list(set(logs_df["operation_type"])))
        selected_type = st.selectbox("Filter by Operation Type", options=operation_types)
        
        # Apply filters
        filtered_logs = logs_df
        if selected_type != "All":
            filtered_logs = logs_df[logs_df["operation_type"] == selected_type]
        
        # Display filtered logs
        st.header("Logs")
        st.dataframe(filtered_logs.sort_values(by="timestamp", ascending=False))
    else:
        st.info("No operation logs found")
