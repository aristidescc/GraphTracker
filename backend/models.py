from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


class Node(db.Model):
    __tablename__ = 'nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    outgoing_edges = db.relationship('Edge', backref='source', foreign_keys='Edge.source_id', cascade='all, delete-orphan')
    incoming_edges = db.relationship('Edge', backref='target', foreign_keys='Edge.target_id', cascade='all, delete-orphan')
    visitors = db.relationship('Visitor', backref='current_node', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Edge(db.Model):
    __tablename__ = 'edges'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure that combination of source_id and target_id is unique
    __table_args__ = (db.UniqueConstraint('source_id', 'target_id', name='_source_target_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'name': self.name,
            'weight': self.weight,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Visitor(db.Model):
    __tablename__ = 'visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    current_node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    movement_history = db.relationship('VisitorMovement', backref='visitor', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'current_node_id': self.current_node_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class VisitorMovement(db.Model):
    __tablename__ = 'visitor_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    edge_id = db.Column(db.Integer, db.ForeignKey('edges.id'), nullable=True)  # Null for initial placement
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    node = db.relationship('Node')
    edge = db.relationship('Edge')
    
    def to_dict(self):
        return {
            'id': self.id,
            'visitor_id': self.visitor_id,
            'node_id': self.node_id,
            'node_name': self.node.name,
            'edge_id': self.edge_id,
            'edge_name': self.edge.name if self.edge else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'operation_type': self.operation_type,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


def log_operation(operation_type, details):
    """Utility function to log operations"""
    log = OperationLog(
        operation_type=operation_type,
        details=json.dumps(details) if isinstance(details, dict) else str(details)
    )
    db.session.add(log)
    db.session.commit()
    return log
