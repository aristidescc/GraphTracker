from flask import jsonify, request, abort
from backend.models import db, Node, Edge, Visitor, VisitorMovement, OperationLog, log_operation
from backend.utils import find_all_paths
import networkx as nx
from datetime import datetime
import json

def register_routes(app):
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "status": "online",
            "message": "Graph Management System API is running",
            "endpoints": [
                "/nodes", "/edges", "/visitors", "/logs", "/paths/{start_node_id}/{end_node_id}"
            ]
        })
    
    # Node endpoints
    @app.route('/nodes', methods=['GET'])
    def get_all_nodes():
        nodes = Node.query.all()
        log_operation('GET_ALL_NODES', {'count': len(nodes)})
        return jsonify([node.to_dict() for node in nodes])
    
    @app.route('/nodes/<int:node_id>', methods=['GET'])
    def get_node(node_id):
        node = Node.query.get_or_404(node_id)
        log_operation('GET_NODE', {'node_id': node_id})
        return jsonify(node.to_dict())
    
    @app.route('/nodes', methods=['POST'])
    def create_node():
        data = request.json
        if not data or 'name' not in data:
            abort(400, description="Name is required")
        
        new_node = Node(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(new_node)
        db.session.commit()
        
        log_operation('CREATE_NODE', {'node_id': new_node.id, 'name': new_node.name})
        return jsonify(new_node.to_dict()), 201
    
    @app.route('/nodes/<int:node_id>', methods=['PUT'])
    def update_node(node_id):
        node = Node.query.get_or_404(node_id)
        data = request.json
        
        if not data:
            abort(400, description="No data provided")
        
        if 'name' in data:
            node.name = data['name']
        if 'description' in data:
            node.description = data['description']
        
        db.session.commit()
        
        log_operation('UPDATE_NODE', {'node_id': node.id, 'name': node.name})
        return jsonify(node.to_dict())
    
    @app.route('/nodes/<int:node_id>', methods=['DELETE'])
    def delete_node(node_id):
        node = Node.query.get_or_404(node_id)
        node_name = node.name  # Save name before deletion for logging
        
        db.session.delete(node)
        db.session.commit()
        
        log_operation('DELETE_NODE', {'node_id': node_id, 'name': node_name})
        return jsonify({'message': f'Node {node_id} deleted successfully'})
    
    # Edge endpoints
    @app.route('/edges', methods=['GET'])
    def get_all_edges():
        edges = Edge.query.all()
        log_operation('GET_ALL_EDGES', {'count': len(edges)})
        return jsonify([edge.to_dict() for edge in edges])
    
    @app.route('/edges/<int:edge_id>', methods=['GET'])
    def get_edge(edge_id):
        edge = Edge.query.get_or_404(edge_id)
        log_operation('GET_EDGE', {'edge_id': edge_id})
        return jsonify(edge.to_dict())
    
    @app.route('/edges', methods=['POST'])
    def create_edge():
        data = request.json
        if not data or 'source_id' not in data or 'target_id' not in data or 'name' not in data:
            abort(400, description="Source ID, Target ID, and Name are required")
        
        # Check if nodes exist
        source = Node.query.get(data['source_id'])
        target = Node.query.get(data['target_id'])
        
        if not source or not target:
            abort(404, description="Source or target node not found")
        
        # Check if edge already exists
        existing_edge = Edge.query.filter_by(
            source_id=data['source_id'],
            target_id=data['target_id']
        ).first()
        
        if existing_edge:
            abort(409, description="Edge between these nodes already exists")
        
        new_edge = Edge(
            source_id=data['source_id'],
            target_id=data['target_id'],
            name=data['name'],
            weight=data.get('weight', 1.0)
        )
        
        db.session.add(new_edge)
        db.session.commit()
        
        log_operation('CREATE_EDGE', {
            'edge_id': new_edge.id, 
            'name': new_edge.name,
            'source_id': new_edge.source_id,
            'target_id': new_edge.target_id
        })
        return jsonify(new_edge.to_dict()), 201
    
    @app.route('/edges/<int:edge_id>', methods=['PUT'])
    def update_edge(edge_id):
        edge = Edge.query.get_or_404(edge_id)
        data = request.json
        
        if not data:
            abort(400, description="No data provided")
        
        # If changing source or target, check if that creates a duplicate
        if ('source_id' in data and data['source_id'] != edge.source_id) or \
           ('target_id' in data and data['target_id'] != edge.target_id):
            # Check if new source/target nodes exist
            source_id = data.get('source_id', edge.source_id)
            target_id = data.get('target_id', edge.target_id)
            
            source = Node.query.get(source_id)
            target = Node.query.get(target_id)
            
            if not source or not target:
                abort(404, description="Source or target node not found")
            
            # Check if edge with new source/target already exists (excluding this edge)
            existing_edge = Edge.query.filter(
                Edge.source_id == source_id,
                Edge.target_id == target_id,
                Edge.id != edge_id
            ).first()
            
            if existing_edge:
                abort(409, description="Edge between these nodes already exists")
            
            edge.source_id = source_id
            edge.target_id = target_id
        
        if 'name' in data:
            edge.name = data['name']
        if 'weight' in data:
            edge.weight = data['weight']
        
        db.session.commit()
        
        log_operation('UPDATE_EDGE', {
            'edge_id': edge.id, 
            'name': edge.name,
            'source_id': edge.source_id,
            'target_id': edge.target_id
        })
        return jsonify(edge.to_dict())
    
    @app.route('/edges/<int:edge_id>', methods=['DELETE'])
    def delete_edge(edge_id):
        edge = Edge.query.get_or_404(edge_id)
        edge_data = edge.to_dict()  # Save data before deletion for logging
        
        db.session.delete(edge)
        db.session.commit()
        
        log_operation('DELETE_EDGE', {
            'edge_id': edge_id, 
            'name': edge_data['name'],
            'source_id': edge_data['source_id'],
            'target_id': edge_data['target_id']
        })
        return jsonify({'message': f'Edge {edge_id} deleted successfully'})
    
    # Path finding endpoint
    @app.route('/paths/<int:start_node_id>/<int:end_node_id>', methods=['GET'])
    def find_paths(start_node_id, end_node_id):
        # Check if nodes exist
        start_node = Node.query.get_or_404(start_node_id)
        end_node = Node.query.get_or_404(end_node_id)
        
        # Build a directed graph
        G = nx.DiGraph()
        
        # Add all nodes and edges
        nodes = Node.query.all()
        edges = Edge.query.all()
        
        for node in nodes:
            G.add_node(node.id, name=node.name)
        
        for edge in edges:
            G.add_edge(edge.source_id, edge.target_id, id=edge.id, name=edge.name, weight=edge.weight)
        
        # Find all paths
        paths = find_all_paths(G, start_node_id, end_node_id)
        
        # Format the paths
        formatted_paths = []
        for path in paths:
            path_nodes = []
            path_edges = []
            
            for i in range(len(path)):
                node_id = path[i]
                node = Node.query.get(node_id)
                path_nodes.append({'id': node.id, 'name': node.name})
                
                # Add edge information (except for the last node)
                if i < len(path) - 1:
                    next_node_id = path[i + 1]
                    edge = Edge.query.filter_by(source_id=node_id, target_id=next_node_id).first()
                    if edge:
                        path_edges.append({'id': edge.id, 'name': edge.name})
            
            formatted_paths.append({
                'nodes': path_nodes,
                'edges': path_edges
            })
        
        log_operation('FIND_PATHS', {
            'start_node_id': start_node_id,
            'end_node_id': end_node_id,
            'paths_found': len(formatted_paths)
        })
        
        return jsonify(formatted_paths)
    
    # Visitor endpoints
    @app.route('/visitors', methods=['GET'])
    def get_all_visitors():
        visitors = Visitor.query.all()
        log_operation('GET_ALL_VISITORS', {'count': len(visitors)})
        return jsonify([visitor.to_dict() for visitor in visitors])
    
    @app.route('/visitors/<int:visitor_id>', methods=['GET'])
    def get_visitor(visitor_id):
        visitor = Visitor.query.get_or_404(visitor_id)
        log_operation('GET_VISITOR', {'visitor_id': visitor_id})
        return jsonify(visitor.to_dict())
    
    @app.route('/visitors', methods=['POST'])
    def create_visitor():
        data = request.json
        if not data or 'name' not in data or 'current_node_id' not in data:
            abort(400, description="Name and current_node_id are required")
        
        # Check if node exists
        node = Node.query.get(data['current_node_id'])
        if not node:
            abort(404, description="Node not found")
        
        new_visitor = Visitor(
            name=data['name'],
            current_node_id=data['current_node_id']
        )
        
        db.session.add(new_visitor)
        db.session.commit()
        
        # Log initial placement (without edge)
        movement = VisitorMovement(
            visitor_id=new_visitor.id,
            node_id=new_visitor.current_node_id,
            edge_id=None  # No edge for initial placement
        )
        
        db.session.add(movement)
        db.session.commit()
        
        log_operation('CREATE_VISITOR', {
            'visitor_id': new_visitor.id, 
            'name': new_visitor.name,
            'node_id': new_visitor.current_node_id
        })
        return jsonify(new_visitor.to_dict()), 201
    
    @app.route('/visitors/<int:visitor_id>/move', methods=['POST'])
    def move_visitor(visitor_id):
        visitor = Visitor.query.get_or_404(visitor_id)
        data = request.json
        
        if not data or 'edge_id' not in data:
            abort(400, description="Edge ID is required")
        
        edge = Edge.query.get_or_404(data['edge_id'])
        
        # Verify that visitor is at the source node of the edge
        if visitor.current_node_id != edge.source_id:
            abort(400, description="Visitor is not at the source node of this edge")
        
        # Update visitor's position
        visitor.current_node_id = edge.target_id
        
        # Log movement
        movement = VisitorMovement(
            visitor_id=visitor.id,
            node_id=edge.target_id,
            edge_id=edge.id
        )
        
        db.session.add(movement)
        db.session.commit()
        
        log_operation('MOVE_VISITOR', {
            'visitor_id': visitor.id,
            'edge_id': edge.id,
            'from_node_id': edge.source_id,
            'to_node_id': edge.target_id
        })
        
        return jsonify(visitor.to_dict())
    
    @app.route('/visitors/<int:visitor_id>/history', methods=['GET'])
    def get_visitor_history(visitor_id):
        visitor = Visitor.query.get_or_404(visitor_id)
        movements = VisitorMovement.query.filter_by(visitor_id=visitor_id).order_by(VisitorMovement.timestamp).all()
        
        log_operation('GET_VISITOR_HISTORY', {'visitor_id': visitor_id})
        
        return jsonify([movement.to_dict() for movement in movements])
    
    # Log endpoints
    @app.route('/logs', methods=['GET'])
    def get_logs():
        logs = OperationLog.query.order_by(OperationLog.timestamp.desc()).all()
        
        log_operation('GET_LOGS', {'count': len(logs)})
        
        return jsonify([log.to_dict() for log in logs])
    
    # Error handling
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': str(error.description)
        }), 404
    
    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            'error': 'Conflict',
            'message': str(error.description)
        }), 409
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'error': 'Server Error',
            'message': 'An unexpected error occurred'
        }), 500
