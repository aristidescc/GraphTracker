import networkx as nx
from backend.models import db, Node, Edge

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

def format_paths(paths):
    """
    Format the paths into a more readable format.

    Parameters:
    - paths: List of paths, where each path is a list of node IDs

    Returns:
    - List of formatted paths
    """
    formatted_paths = []
    # Formatear las rutas
    formatted_paths = []
    for path in paths:
        path_steps = []

        for i in range(len(path)):
            node_id = path[i]
            node = db.session.get(Node, node_id)
            edge = None
            # Agregar información de arista (excepto para el último nodo)
            if i < len(path) - 1:
                next_node_id = path[i + 1]
                edge = db.session.execute(db.select(Edge).filter_by(
                    source_id=node_id,
                    target_id=next_node_id
                )).scalar_one_or_none()

            path_steps.append({
                'node_id': node.id,
                'node_name': node.name,
                'outbound_edge': edge.to_dict() if edge else None,
                'weight': edge.weight if edge else 0
            })

        formatted_paths.append({
            'steps': path_steps,
            'total_weight': sum(step['weight'] for step in path_steps),
        })
    formatted_paths.sort(key=lambda path: path['total_weight'])
    return formatted_paths