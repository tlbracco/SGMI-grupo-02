"""Controlador de Inventario - API endpoints for managing equipment/inventory.

Uses SQLAlchemy ORM models from models_db to handle CRUD operations
on Equipamiento (equipment/inventory) and related entities.
"""

import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, jsonify

# Import ORM models
from models_db import (
    Base, Equipamiento, Grupo, Proyecto, ActividadDocente, Bibliografia
)

# Create blueprint for inventory management routes
inventario_bp = Blueprint('inventario', __name__, url_prefix='/api/inventario')

# Initialize database connection
def build_db_url():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    user = os.getenv('PGUSER', '')
    password = os.getenv('PGPASSWORD', '')
    host = os.getenv('PGHOST', 'localhost')
    port = os.getenv('PGPORT', '5432')
    db = os.getenv('PGDATABASE', '')
    if user and password and db:
        return f'postgresql://{user}:{password}@{host}:{port}/{db}'
    return None


DB_URL = build_db_url() or "postgresql://postgres:Segundo_Francia_2025@db.hxrdfvfeiddvydvilrsa.supabase.co:5432/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Return a new database session."""
    return SessionLocal()


# ============ EQUIPAMIENTO CRUD ENDPOINTS ============

@inventario_bp.route('', methods=['GET'])
def list_equipamiento():
    """List all equipment items (equipamiento)."""
    session = get_session()
    try:
        # Optional filters
        grupo_id = request.args.get('grupo_id', type=int)
        proyecto_id = request.args.get('proyecto_id', type=int)
        actividad_id = request.args.get('actividad_id', type=int)
        
        query = session.query(Equipamiento)
        
        if grupo_id:
            query = query.filter(Equipamiento.grupo == grupo_id)
        if proyecto_id:
            query = query.filter(Equipamiento.proyecto == proyecto_id)
        if actividad_id:
            query = query.filter(Equipamiento.actividad == actividad_id)
        
        equipamiento_list = query.all()
        
        result = []
        for eq in equipamiento_list:
            result.append({
                'id': eq.id,
                'denominacion': eq.denominacion,
                'fecha_ingreso': eq.fechaIngreso.isoformat(),
                'monto': float(eq.monto),
                'descripcion': eq.descripción,
                'grupo_id': eq.grupo,
                'proyecto_id': eq.proyecto,
                'actividad_id': eq.actividad
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('', methods=['POST'])
def create_equipamiento():
    """Create a new equipment item (equipamiento)."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    required = ['denominacion', 'fecha_ingreso', 'monto', 'grupo']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'success': False, 'message': f'Missing fields: {missing}'}), 400
    
    session = get_session()
    try:
        # Verify grupo exists
        grupo = session.query(Grupo).filter(Grupo.id == data['grupo']).first()
        if not grupo:
            return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        # Verify proyecto if provided
        if data.get('proyecto'):
            proyecto = session.query(Proyecto).filter(Proyecto.id == data['proyecto']).first()
            if not proyecto:
                return jsonify({'success': False, 'message': 'Proyecto not found'}), 404
        
        # Verify actividad if provided
        if data.get('actividad'):
            actividad = session.query(ActividadDocente).filter(
                ActividadDocente.id == data['actividad']
            ).first()
            if not actividad:
                return jsonify({'success': False, 'message': 'Actividad not found'}), 404
        
        equipamiento = Equipamiento(
            denominacion=data['denominacion'],
            fechaIngreso=date.fromisoformat(data['fecha_ingreso']),
            monto=data['monto'],
            grupo=data['grupo'],
            descripción=data.get('descripcion'),
            proyecto=data.get('proyecto'),
            actividad=data.get('actividad')
        )
        session.add(equipamiento)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipamiento created',
            'id': equipamiento.id
        }), 201
    except IntegrityError:
        session.rollback()
        return jsonify({'success': False, 'message': 'Integrity error'}), 409
    except ValueError as ve:
        session.rollback()
        return jsonify({'success': False, 'message': f'Invalid value: {str(ve)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/<int:equipamiento_id>', methods=['GET'])
def get_equipamiento(equipamiento_id):
    """Get details of a specific equipment item."""
    session = get_session()
    try:
        equipamiento = session.query(Equipamiento).filter(
            Equipamiento.id == equipamiento_id
        ).first()
        
        if not equipamiento:
            return jsonify({'success': False, 'message': 'Equipamiento not found'}), 404
        
        return jsonify({
            'id': equipamiento.id,
            'denominacion': equipamiento.denominacion,
            'fecha_ingreso': equipamiento.fechaIngreso.isoformat(),
            'monto': float(equipamiento.monto),
            'descripcion': equipamiento.descripción,
            'grupo_id': equipamiento.grupo,
            'proyecto_id': equipamiento.proyecto,
            'actividad_id': equipamiento.actividad
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/<int:equipamiento_id>', methods=['PUT'])
def update_equipamiento(equipamiento_id):
    """Update an equipment item's details."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    session = get_session()
    try:
        equipamiento = session.query(Equipamiento).filter(
            Equipamiento.id == equipamiento_id
        ).first()
        
        if not equipamiento:
            return jsonify({'success': False, 'message': 'Equipamiento not found'}), 404
        
        # Verify references if being updated
        if 'grupo' in data:
            grupo = session.query(Grupo).filter(Grupo.id == data['grupo']).first()
            if not grupo:
                return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        if 'proyecto' in data and data['proyecto']:
            proyecto = session.query(Proyecto).filter(Proyecto.id == data['proyecto']).first()
            if not proyecto:
                return jsonify({'success': False, 'message': 'Proyecto not found'}), 404
        
        if 'actividad' in data and data['actividad']:
            actividad = session.query(ActividadDocente).filter(
                ActividadDocente.id == data['actividad']
            ).first()
            if not actividad:
                return jsonify({'success': False, 'message': 'Actividad not found'}), 404
        
        # Update allowed fields
        allowed_fields = {
            'denominacion': str,
            'fecha_ingreso': lambda x: date.fromisoformat(x),
            'monto': float,
            'descripcion': str,
            'grupo': int,
            'proyecto': int,
            'actividad': int
        }
        
        for field, field_type in allowed_fields.items():
            if field in data:
                if field == 'fecha_ingreso':
                    setattr(equipamiento, 'fechaIngreso', field_type(data[field]))
                elif field == 'descripcion':
                    setattr(equipamiento, 'descripción', data[field])
                else:
                    setattr(equipamiento, field, data[field])
        
        session.commit()
        return jsonify({'success': True, 'message': 'Equipamiento updated'}), 200
    except ValueError as ve:
        session.rollback()
        return jsonify({'success': False, 'message': f'Invalid value: {str(ve)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/<int:equipamiento_id>', methods=['DELETE'])
def delete_equipamiento(equipamiento_id):
    """Delete an equipment item."""
    session = get_session()
    try:
        equipamiento = session.query(Equipamiento).filter(
            Equipamiento.id == equipamiento_id
        ).first()
        
        if not equipamiento:
            return jsonify({'success': False, 'message': 'Equipamiento not found'}), 404
        
        session.delete(equipamiento)
        session.commit()
        return jsonify({'success': True, 'message': 'Equipamiento deleted'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


# ============ EQUIPAMIENTO FILTERING ENDPOINTS ============

@inventario_bp.route('/grupo/<int:grupo_id>', methods=['GET'])
def get_equipamiento_by_grupo(grupo_id):
    """Get all equipment items for a specific grupo."""
    session = get_session()
    try:
        # Verify grupo exists
        grupo = session.query(Grupo).filter(Grupo.id == grupo_id).first()
        if not grupo:
            return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        equipamiento_list = session.query(Equipamiento).filter(
            Equipamiento.grupo == grupo_id
        ).all()
        
        result = []
        for eq in equipamiento_list:
            result.append({
                'id': eq.id,
                'denominacion': eq.denominacion,
                'fecha_ingreso': eq.fechaIngreso.isoformat(),
                'monto': float(eq.monto),
                'descripcion': eq.descripción,
                'proyecto_id': eq.proyecto,
                'actividad_id': eq.actividad
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
def get_equipamiento_by_proyecto(proyecto_id):
    """Get all equipment items for a specific proyecto."""
    session = get_session()
    try:
        # Verify proyecto exists
        proyecto = session.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
        if not proyecto:
            return jsonify({'success': False, 'message': 'Proyecto not found'}), 404
        
        equipamiento_list = session.query(Equipamiento).filter(
            Equipamiento.proyecto == proyecto_id
        ).all()
        
        result = []
        for eq in equipamiento_list:
            result.append({
                'id': eq.id,
                'denominacion': eq.denominacion,
                'fecha_ingreso': eq.fechaIngreso.isoformat(),
                'monto': float(eq.monto),
                'descripcion': eq.descripción,
                'grupo_id': eq.grupo,
                'actividad_id': eq.actividad
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/estadisticas/grupo/<int:grupo_id>', methods=['GET'])
def get_equipamiento_stats_grupo(grupo_id):
    """Get equipment statistics for a specific grupo."""
    session = get_session()
    try:
        # Verify grupo exists
        grupo = session.query(Grupo).filter(Grupo.id == grupo_id).first()
        if not grupo:
            return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        equipamiento_list = session.query(Equipamiento).filter(
            Equipamiento.grupo == grupo_id
        ).all()
        
        total_items = len(equipamiento_list)
        total_value = sum(float(eq.monto) for eq in equipamiento_list)
        
        return jsonify({
            'grupo_id': grupo_id,
            'total_items': total_items,
            'total_value': total_value,
            'average_value': total_value / total_items if total_items > 0 else 0
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


# ============ BIBLIOGRAFIA CRUD ENDPOINTS ============

@inventario_bp.route('/bibliografia', methods=['GET'])
def list_bibliografia():
    """List all bibliography entries."""
    session = get_session()
    try:
        # Optional filters
        grupo_id = request.args.get('grupo_id', type=int)
        
        query = session.query(Bibliografia)
        
        if grupo_id:
            query = query.filter(Bibliografia.grupo == grupo_id)
        
        bibliografia_list = query.all()
        
        result = []
        for bib in bibliografia_list:
            result.append({
                'id': bib.id,
                'referencia': bib.referencia,
                'descripcion': bib.descripcion,
                'grupo_id': bib.grupo
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/bibliografia', methods=['POST'])
def create_bibliografia():
    """Create a new bibliography entry."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    required = ['referencia', 'grupo']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'success': False, 'message': f'Missing fields: {missing}'}), 400
    
    session = get_session()
    try:
        # Verify grupo exists
        grupo = session.query(Grupo).filter(Grupo.id == data['grupo']).first()
        if not grupo:
            return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        bibliografia = Bibliografia(
            referencia=data['referencia'],
            descripcion=data.get('descripcion'),
            grupo=data['grupo']
        )
        session.add(bibliografia)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bibliografia created',
            'id': bibliografia.id
        }), 201
    except IntegrityError:
        session.rollback()
        return jsonify({'success': False, 'message': 'Integrity error'}), 409
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/bibliografia/<int:bibliografia_id>', methods=['GET'])
def get_bibliografia(bibliografia_id):
    """Get details of a specific bibliography entry."""
    session = get_session()
    try:
        bibliografia = session.query(Bibliografia).filter(
            Bibliografia.id == bibliografia_id
        ).first()
        
        if not bibliografia:
            return jsonify({'success': False, 'message': 'Bibliografia not found'}), 404
        
        return jsonify({
            'id': bibliografia.id,
            'referencia': bibliografia.referencia,
            'descripcion': bibliografia.descripcion,
            'grupo_id': bibliografia.grupo
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/bibliografia/<int:bibliografia_id>', methods=['PUT'])
def update_bibliografia(bibliografia_id):
    """Update a bibliography entry."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    session = get_session()
    try:
        bibliografia = session.query(Bibliografia).filter(
            Bibliografia.id == bibliografia_id
        ).first()
        
        if not bibliografia:
            return jsonify({'success': False, 'message': 'Bibliografia not found'}), 404
        
        # Verify grupo if being updated
        if 'grupo' in data:
            grupo = session.query(Grupo).filter(Grupo.id == data['grupo']).first()
            if not grupo:
                return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        # Update allowed fields
        allowed_fields = ['referencia', 'descripcion', 'grupo']
        for field in allowed_fields:
            if field in data:
                setattr(bibliografia, field, data[field])
        
        session.commit()
        return jsonify({'success': True, 'message': 'Bibliografia updated'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/bibliografia/<int:bibliografia_id>', methods=['DELETE'])
def delete_bibliografia(bibliografia_id):
    """Delete a bibliography entry."""
    session = get_session()
    try:
        bibliografia = session.query(Bibliografia).filter(
            Bibliografia.id == bibliografia_id
        ).first()
        
        if not bibliografia:
            return jsonify({'success': False, 'message': 'Bibliografia not found'}), 404
        
        session.delete(bibliografia)
        session.commit()
        return jsonify({'success': True, 'message': 'Bibliografia deleted'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@inventario_bp.route('/bibliografia/grupo/<int:grupo_id>', methods=['GET'])
def get_bibliografia_by_grupo(grupo_id):
    """Get all bibliography entries for a specific grupo."""
    session = get_session()
    try:
        # Verify grupo exists
        grupo = session.query(Grupo).filter(Grupo.id == grupo_id).first()
        if not grupo:
            return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        bibliografia_list = session.query(Bibliografia).filter(
            Bibliografia.grupo == grupo_id
        ).all()
        
        result = []
        for bib in bibliografia_list:
            result.append({
                'id': bib.id,
                'referencia': bib.referencia,
                'descripcion': bib.descripcion
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()
