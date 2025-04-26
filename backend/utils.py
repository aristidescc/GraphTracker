import networkx as nx

def find_all_paths(graph, start_node, end_node, cutoff=10):
    """
    Find all simple paths from start_node to end_node in the graph.
    
    Parameters:
    - graph: NetworkX DiGraph
    - start_node: Starting node ID
    - end_node: Ending node ID
    - cutoff: Maximum path length to consider (to prevent infinite paths in cyclic graphs)
    
    Returns:
    - List of paths, where each path is a list of node IDs
    """
    try:
        # Use NetworkX's built-in function to find all simple paths
        paths = list(nx.all_simple_paths(graph, start_node, end_node, cutoff=cutoff))
        return paths
    except nx.NetworkXNoPath:
        # No path exists
        return []
    except nx.NodeNotFound:
        # One of the nodes doesn't exist
        return []
