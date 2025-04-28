from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import json
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, String, Integer, Float, Text, DateTime

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


class Node(db.Model):
    __tablename__ = 'nodes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    outgoing_edges: Mapped[List["Edge"]] = relationship('Edge', back_populates='source', foreign_keys='Edge.source_id', cascade='all, delete-orphan')
    incoming_edges: Mapped[List["Edge"]] = relationship('Edge', back_populates='target', foreign_keys='Edge.target_id', cascade='all, delete-orphan')
    visitors: Mapped[List["Visitor"]] = relationship('Visitor', back_populates='current_node', cascade='all, delete-orphan')

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey('nodes.id'), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey('nodes.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source: Mapped["Node"] = relationship('Node', foreign_keys=[source_id], back_populates='outgoing_edges')
    target: Mapped["Node"] = relationship('Node', foreign_keys=[target_id], back_populates='incoming_edges')

    # Ensure that combination of source_id and target_id is unique
    __table_args__ = (UniqueConstraint('source_id', 'target_id', name='_source_target_uc'),)

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    current_node_id: Mapped[int] = mapped_column(Integer, ForeignKey('nodes.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    current_node: Mapped["Node"] = relationship('Node', back_populates='visitors')
    movement_history: Mapped[List["VisitorMovement"]] = relationship('VisitorMovement', back_populates='visitor', cascade='all, delete-orphan')

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_id: Mapped[int] = mapped_column(Integer, ForeignKey('visitors.id'), nullable=False)
    node_id: Mapped[int] = mapped_column(Integer, ForeignKey('nodes.id'), nullable=False)
    edge_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('edges.id'), nullable=True)  # Null for initial placement
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(pytz.UTC))

    # Relationships
    visitor: Mapped["Visitor"] = relationship('Visitor', back_populates='movement_history')
    node: Mapped["Node"] = relationship('Node')
    edge: Mapped[Optional["Edge"]] = relationship('Edge')

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
