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
            "/api/paths"
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


@app.route('/api/edges/<int:edge_id>', methods=['GET', 'PUT', 'DELETE'])
def edge_operations(edge_id):
    edge = Edge.query.get_or_404(edge_id)

    if request.method == 'GET':
        log_operation('GET_EDGE', {'edge_id': edge_id})
        return jsonify(edge.to_dict())

    elif request.method == 'PUT':
        data = request.json
        if not data:
            abort(400, description="No data provided")

        # Si se modifican source_id o target_id, verificar que no exista ya una arista entre esos nodos
        if ('source_id' in data and data['source_id'] != edge.source_id) or (
                'target_id' in data and data['target_id'] != edge.target_id):
            source_id = data.get('source_id', edge.source_id)
            target_id = data.get('target_id', edge.target_id)

            # Verificar si los nodos existen
            source = Node.query.get(source_id)
            target = Node.query.get(target_id)

            if not source or not target:
                abort(404, description="Source or target node not found")

            # Verificar si ya existe una arista entre estos nodos (excepto la actual)
            existing_edge = Edge.query.filter_by(
                source_id=source_id,
                target_id=target_id
            ).filter(
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

    elif request.method == 'DELETE':
        edge_data = edge.to_dict()  # Guardar datos antes de eliminar para el registro

        db.session.delete(edge)
        db.session.commit()

        log_operation('DELETE_EDGE', {
            'edge_id': edge_id,
            'name': edge_data['name'],
            'source_id': edge_data['source_id'],
            'target_id': edge_data['target_id']
        })
        return jsonify({'message': f'Edge {edge_id} deleted successfully'})

@app.route('/api/visitors', methods=['GET'])
def get_all_visitors():
    visitors = Visitor.query.all()
    log_operation('GET_ALL_VISITORS', {'count': len(visitors)})
    return jsonify([visitor.to_dict() for visitor in visitors])


@app.route('/api/visitors', methods=['POST'])
def create_visitor():
    data = request.json
    if not data or 'name' not in data or 'node_name' not in data:
        abort(400, description="Visitor name and initial node name are required")

    # Verificar que el nodo existe buscando por nombre
    node = Node.query.filter_by(name=data['node_name']).first()
    if not node:
        abort(404, description=f"No se encontró el nodo '{data['node_name']}'")

    new_visitor = Visitor(
        name=data['name'],
        current_node_id=node.id
    )

    db.session.add(new_visitor)
    db.session.commit()

    # Registrar ubicación inicial (sin arista)
    movement = VisitorMovement(
        visitor_id=new_visitor.id,
        node_id=new_visitor.current_node_id,
        edge_id=None  # Sin arista para la ubicación inicial
    )

    db.session.add(movement)
    db.session.commit()

    log_operation('CREATE_VISITOR', {
        'visitor_id': new_visitor.id,
        'name': new_visitor.name,
        'node_id': new_visitor.current_node_id,
        'node_name': node.name,
    })
    return jsonify(new_visitor.to_dict()), 201


@app.route('/api/visitors/<int:visitor_id>/move', methods=['POST'])
def move_visitor(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)
    data = request.json

    if not data or 'edge_name' not in data or 'target_node_name' not in data:
        abort(400, description="Se requiere el nombre de la arista y el nombre del nodo destino")

    edge_name = data['edge_name']
    target_node_name = data['target_node_name']

    # Obtener el nodo destino por nombre
    target_node = Node.query.filter_by(name=target_node_name).first()
    if not target_node:
        abort(404, description=f"No se encontró el nodo destino '{target_node_name}'")

    # Buscar la arista que conecta el nodo actual del visitante con el nodo destino
    edge = Edge.query.filter_by(
        source_id=visitor.current_node_id,
        target_id=target_node.id,
        name=edge_name
    ).first()

    if not edge:
        abort(404,
              description=f"No existe una arista llamada '{edge_name}' desde la ubicación actual hacia '{target_node_name}'")

    # Actualizar la ubicación del visitante
    old_node_id = visitor.current_node_id
    visitor.current_node_id = target_node.id
    db.session.commit()

    # Registrar el movimiento
    movement = VisitorMovement(
        visitor_id=visitor.id,
        node_id=target_node.id,
        edge_id=edge.id
    )

    db.session.add(movement)
    db.session.commit()

    log_operation('MOVE_VISITOR', {
        'visitor_id': visitor.id,
        'visitor_name': visitor.name,
        'from_node_id': old_node_id,
        'to_node_id': target_node.id,
        'to_node_name': target_node.name,
        'edge_id': edge.id,
        'edge_name': edge.name
    })

    return jsonify({
        'visitor': visitor.to_dict(),
        'movement': movement.to_dict(),
        'message': f"Visitante '{visitor.name}' movido al nodo '{target_node.name}' por la arista '{edge.name}'"
    }), 200

# Path finding endpoint
@app.route('/api/paths/<int:start_node_id>/<int:end_node_id>', methods=['GET'])
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


@app.route('/api/paths', methods=['POST'])
def find_paths_by_name():
    data = request.json
    if not data or 'start_node_name' not in data or 'end_node_name' not in data:
        abort(400, description="Se requieren los nombres de nodo origen y destino")

    start_node_name = data['start_node_name']
    end_node_name = data['end_node_name']

    # Obtener los nodos por nombre
    start_node = Node.query.filter_by(name=start_node_name).first()
    end_node = Node.query.filter_by(name=end_node_name).first()

    if not start_node:
        abort(404, description=f"Could not find source node '{start_node_name}'")

    if not end_node:
        abort(404, description=f"Could not find target node '{end_node_name}'")

    # Construir el grafo dirigido
    G = nx.DiGraph()

    # Agregar todos los nodos y aristas
    nodes = Node.query.all()
    edges = Edge.query.all()

    for node in nodes:
        G.add_node(node.id, name=node.name)

    for edge in edges:
        G.add_edge(edge.source_id, edge.target_id, id=edge.id, name=edge.name, weight=edge.weight)

    # Encontrar todas las rutas
    paths = find_all_paths(G, start_node.id, end_node.id)

    # Formatear las rutas
    formatted_paths = []
    for path in paths:
        path_nodes = []
        path_edges = []

        for i in range(len(path)):
            node_id = path[i]
            node = Node.query.get(node_id)
            path_nodes.append({'id': node.id, 'name': node.name})

            # Agregar información de arista (excepto para el último nodo)
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
        'start_node_name': start_node_name,
        'end_node_name': end_node_name,
        'paths_found': len(formatted_paths)
    })

    return jsonify(formatted_paths)

@app.route('/api/visitors/<int:visitor_id>/history', methods=['GET'])
def get_visitor_history(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)
    movements = VisitorMovement.query.filter_by(visitor_id=visitor_id).order_by(VisitorMovement.timestamp).all()

    log_operation('GET_VISITOR_HISTORY', {'visitor_id': visitor_id})

    return jsonify([movement.to_dict() for movement in movements])

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


@app.route('/nodes/<int:node_id>/edit', methods=['GET', 'POST'])
def edit_node(node_id):
    node = Node.query.get_or_404(node_id)
    if request.method == 'POST':
        name = request.form.get('name')


        if name:
            node.name = name
            node.description = request.form.get('description')
            db.session.commit()
            log_operation('EDIT_NODE', {'node_id': node.id, 'name': node.name, 'description': node.description })
            return redirect(url_for('nodes_page'))

    return render_template('edit_node.html', node=node)


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


@app.route('/edges/<int:edge_id>/edit', methods=['GET', 'POST'])
def edit_edge(edge_id):
    nodes = Node.query.all()
    edge = Edge.query.get_or_404(edge_id)
    if request.method == 'POST':
        source_id = request.form.get('source_id', type=int)
        target_id = request.form.get('target_id', type=int)
        name = request.form.get('name')
        weight = request.form.get('weight', type=float, default=1.0)

        if source_id and target_id and name:
            # Check if edge already exists
            existing_edge = Edge.query.filter_by(source_id=source_id, target_id=target_id).first()
            if existing_edge and existing_edge.id != edge_id:
                return render_template('edit_edge.html', nodes=nodes, edge=edge, error="Edge already exists between these nodes")
            edge.name = name
            edge.source_id = source_id
            edge.target_id = target_id
            edge.weight = weight
            db.session.commit()
            log_operation('EDIT_EDGE', {
                'edge_id': edge.id,
                'name': edge.name,
                'source_id': edge.source_id,
                'target_id': edge.target_id
            })
            return redirect(url_for('edges_page'))

    return render_template('edit_edge.html', nodes=nodes, edge=edge)
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
    app.run(host='0.0.0.0', port=5001, debug=True)