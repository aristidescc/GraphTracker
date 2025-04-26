from flask import Flask, jsonify, request, abort, render_template, redirect, url_for
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow imports
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from backend.models import db, Node, Edge, Visitor, VisitorMovement, OperationLog, log_operation, init_db
from backend.utils import find_all_paths
import networkx as nx
from datetime import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Database configuration - using SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///graph.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# API Routes
@app.route('/api/', methods=['GET'])
def api_index():
    return jsonify({
        "status": "online",
        "message": "Graph Management System API is running",
        "endpoints": [
            "/api/nodes", "/api/edges", "/api/visitors", "/api/logs", 
            "/api/paths/{start_node_id}/{end_node_id}"
        ]
    })

@app.route('/api/nodes', methods=['GET'])
def get_all_nodes():
    nodes = Node.query.all()
    log_operation('GET_ALL_NODES', {'count': len(nodes)})
    return jsonify([node.to_dict() for node in nodes])

@app.route('/api/nodes', methods=['POST'])
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

@app.route('/api/nodes/<int:node_id>', methods=['GET', 'PUT', 'DELETE'])
def node_operations(node_id):
    node = Node.query.get_or_404(node_id)
    
    if request.method == 'GET':
        log_operation('GET_NODE', {'node_id': node_id})
        return jsonify(node.to_dict())
    
    elif request.method == 'PUT':
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
    
    elif request.method == 'DELETE':
        node_name = node.name
        db.session.delete(node)
        db.session.commit()
        log_operation('DELETE_NODE', {'node_id': node_id, 'name': node_name})
        return jsonify({'message': f'Node {node_id} deleted successfully'})

@app.route('/api/edges', methods=['GET'])
def get_all_edges():
    edges = Edge.query.all()
    log_operation('GET_ALL_EDGES', {'count': len(edges)})
    return jsonify([edge.to_dict() for edge in edges])

@app.route('/api/edges', methods=['POST'])
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

@app.route('/api/visitors', methods=['GET'])
def get_all_visitors():
    visitors = Visitor.query.all()
    log_operation('GET_ALL_VISITORS', {'count': len(visitors)})
    return jsonify([visitor.to_dict() for visitor in visitors])

@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = OperationLog.query.order_by(OperationLog.timestamp.desc()).all()
    log_operation('GET_LOGS', {'count': len(logs)})
    return jsonify([log.to_dict() for log in logs])

# Web interface routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nodes')
def nodes_page():
    nodes = Node.query.all()
    return render_template('nodes.html', nodes=nodes)

@app.route('/nodes/new', methods=['GET', 'POST'])
def new_node():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if name:
            new_node = Node(name=name, description=description)
            db.session.add(new_node)
            db.session.commit()
            log_operation('CREATE_NODE', {'node_id': new_node.id, 'name': new_node.name})
            return redirect(url_for('nodes_page'))
    
    return render_template('new_node.html')

@app.route('/edges')
def edges_page():
    edges = Edge.query.all()
    return render_template('edges.html', edges=edges)

@app.route('/edges/new', methods=['GET', 'POST'])
def new_edge():
    nodes = Node.query.all()
    
    if request.method == 'POST':
        source_id = request.form.get('source_id', type=int)
        target_id = request.form.get('target_id', type=int)
        name = request.form.get('name')
        weight = request.form.get('weight', type=float, default=1.0)
        
        if source_id and target_id and name:
            # Check if edge already exists
            existing_edge = Edge.query.filter_by(source_id=source_id, target_id=target_id).first()
            if existing_edge:
                return render_template('new_edge.html', nodes=nodes, error="Edge already exists between these nodes")
            
            new_edge = Edge(source_id=source_id, target_id=target_id, name=name, weight=weight)
            db.session.add(new_edge)
            db.session.commit()
            log_operation('CREATE_EDGE', {
                'edge_id': new_edge.id, 
                'name': new_edge.name,
                'source_id': new_edge.source_id,
                'target_id': new_edge.target_id
            })
            return redirect(url_for('edges_page'))
    
    return render_template('new_edge.html', nodes=nodes)

@app.route('/visitors')
def visitors_page():
    visitors = Visitor.query.all()
    return render_template('visitors.html', visitors=visitors)

@app.route('/logs')
def logs_page():
    logs = OperationLog.query.order_by(OperationLog.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

# Error handlers
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)