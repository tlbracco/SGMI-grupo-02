"""Controlador de Participacion - API endpoints for managing participations/collaborations.

Uses SQLAlchemy ORM models from models_db to handle CRUD operations
on Participacion, ParticipacionPersona, and related entities.
"""

import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, jsonify

# Import ORM models
from models_db import (
    Base, Participacion, ParticipacionPersona, Grupo, Institucion,
    Persona, RolParticipacion
)

# Create blueprint for participation management routes
participacion_bp = Blueprint('participacion', __name__, url_prefix='/api/participacion')

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


# ============ PARTICIPACION CRUD ENDPOINTS ============

@participacion_bp.route('', methods=['GET'])
def list_participaciones():
    """List all participations."""
    session = get_session()
    try:
        # Optional filters
        grupo_id = request.args.get('grupo_id', type=int)
        institucion_id = request.args.get('institucion_id', type=int)
        
        query = session.query(Participacion)
        
        if grupo_id:
            query = query.filter(Participacion.grupo == grupo_id)
        if institucion_id:
            query = query.filter(Participacion.institucion == institucion_id)
        
        participaciones = query.all()
        
        result = []
        for p in participaciones:
            result.append({
                'id': p.id,
                'grupo_id': p.grupo,
                'institucion_id': p.institucion,
                'rol_id': p.rol,
                'fecha_inicio': p.fecha_inicio.isoformat() if p.fecha_inicio else None,
                'fecha_fin': p.fecha_fin.isoformat() if p.fecha_fin else None,
                'descripcion': p.descripcion
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@participacion_bp.route('', methods=['POST'])
def create_participacion():
    """Create a new participation."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    required = ['grupo', 'institucion', 'rol']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'success': False, 'message': f'Missing fields: {missing}'}), 400
    
    session = get_session()
    try:
        # Verify references
        grupo = session.query(Grupo).filter(Grupo.id == data['grupo']).first()
        if not grupo:
            return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        institucion = session.query(Institucion).filter(Institucion.id == data['institucion']).first()
        if not institucion:
            return jsonify({'success': False, 'message': 'Institucion not found'}), 404
        
        rol = session.query(RolParticipacion).filter(RolParticipacion.id == data['rol']).first()
        if not rol:
            return jsonify({'success': False, 'message': 'RolParticipacion not found'}), 404
        
        participacion = Participacion(
            grupo=data['grupo'],
            institucion=data['institucion'],
            rol=data['rol'],
            fecha_inicio=date.fromisoformat(data['fecha_inicio']) if data.get('fecha_inicio') else None,
            fecha_fin=date.fromisoformat(data['fecha_fin']) if data.get('fecha_fin') else None,
            descripcion=data.get('descripcion')
        )
        session.add(participacion)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Participacion created',
            'id': participacion.id
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


@participacion_bp.route('/<int:participacion_id>', methods=['GET'])
def get_participacion(participacion_id):
    """Get details of a specific participation."""
    session = get_session()
    try:
        participacion = session.query(Participacion).filter(
            Participacion.id == participacion_id
        ).first()
        
        if not participacion:
            return jsonify({'success': False, 'message': 'Participacion not found'}), 404
        
        return jsonify({
            'id': participacion.id,
            'grupo_id': participacion.grupo,
            'institucion_id': participacion.institucion,
            'rol_id': participacion.rol,
            'fecha_inicio': participacion.fecha_inicio.isoformat() if participacion.fecha_inicio else None,
            'fecha_fin': participacion.fecha_fin.isoformat() if participacion.fecha_fin else None,
            'descripcion': participacion.descripcion
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@participacion_bp.route('/<int:participacion_id>', methods=['PUT'])
def update_participacion(participacion_id):
    """Update a participation."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    session = get_session()
    try:
        participacion = session.query(Participacion).filter(
            Participacion.id == participacion_id
        ).first()
        
        if not participacion:
            return jsonify({'success': False, 'message': 'Participacion not found'}), 404
        
        # Verify references if being updated
        if 'grupo' in data:
            grupo = session.query(Grupo).filter(Grupo.id == data['grupo']).first()
            if not grupo:
                return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        if 'institucion' in data:
            institucion = session.query(Institucion).filter(Institucion.id == data['institucion']).first()
            if not institucion:
                return jsonify({'success': False, 'message': 'Institucion not found'}), 404
        
        if 'rol' in data:
            rol = session.query(RolParticipacion).filter(RolParticipacion.id == data['rol']).first()
            if not rol:
                return jsonify({'success': False, 'message': 'RolParticipacion not found'}), 404
        
        # Update allowed fields
        allowed_fields = {
            'grupo': int,
            'institucion': int,
            'rol': int,
            'fecha_inicio': lambda x: date.fromisoformat(x) if x else None,
            'fecha_fin': lambda x: date.fromisoformat(x) if x else None,
            'descripcion': str
        }
        
        for field, field_type in allowed_fields.items():
            if field in data:
                if field in ['fecha_inicio', 'fecha_fin']:
                    setattr(participacion, field, field_type(data[field]))
                else:
                    setattr(participacion, field, data[field])
        
        session.commit()
        return jsonify({'success': True, 'message': 'Participacion updated'}), 200
    except ValueError as ve:
        session.rollback()
        return jsonify({'success': False, 'message': f'Invalid value: {str(ve)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@participacion_bp.route('/<int:participacion_id>', methods=['DELETE'])
def delete_participacion(participacion_id):
    """Delete a participation."""
    session = get_session()
    try:
        participacion = session.query(Participacion).filter(
            Participacion.id == participacion_id
        ).first()
        
        if not participacion:
            return jsonify({'success': False, 'message': 'Participacion not found'}), 404
        
        session.delete(participacion)
        session.commit()
        return jsonify({'success': True, 'message': 'Participacion deleted'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


# ============ PARTICIPACION FILTERING ENDPOINTS ============

@participacion_bp.route('/grupo/<int:grupo_id>', methods=['GET'])
def get_participaciones_by_grupo(grupo_id):
    """Get all participations for a specific grupo."""
    session = get_session()
    try:
        # Verify grupo exists
        grupo = session.query(Grupo).filter(Grupo.id == grupo_id).first()
        if not grupo:
            return jsonify({'success': False, 'message': 'Grupo not found'}), 404
        
        participaciones = session.query(Participacion).filter(
            Participacion.grupo == grupo_id
        ).all()
        
        result = []
        for p in participaciones:
            result.append({
                'id': p.id,
                'institucion_id': p.institucion,
                'rol_id': p.rol,
                'fecha_inicio': p.fecha_inicio.isoformat() if p.fecha_inicio else None,
                'fecha_fin': p.fecha_fin.isoformat() if p.fecha_fin else None,
                'descripcion': p.descripcion
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@participacion_bp.route('/institucion/<int:institucion_id>', methods=['GET'])
def get_participaciones_by_institucion(institucion_id):
    """Get all participations for a specific institucion."""
    session = get_session()
    try:
        # Verify institucion exists
        institucion = session.query(Institucion).filter(Institucion.id == institucion_id).first()
        if not institucion:
            return jsonify({'success': False, 'message': 'Institucion not found'}), 404
        
        participaciones = session.query(Participacion).filter(
            Participacion.institucion == institucion_id
        ).all()
        
        result = []
        for p in participaciones:
            result.append({
                'id': p.id,
                'grupo_id': p.grupo,
                'rol_id': p.rol,
                'fecha_inicio': p.fecha_inicio.isoformat() if p.fecha_inicio else None,
                'fecha_fin': p.fecha_fin.isoformat() if p.fecha_fin else None,
                'descripcion': p.descripcion
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


# ============ PARTICIPACION PERSONAS ENDPOINTS ============

@participacion_bp.route('/<int:participacion_id>/personas', methods=['GET'])
def get_participacion_personas(participacion_id):
    """Get all personas involved in a participation."""
    session = get_session()
    try:
        # Verify participacion exists
        participacion = session.query(Participacion).filter(
            Participacion.id == participacion_id
        ).first()
        
        if not participacion:
            return jsonify({'success': False, 'message': 'Participacion not found'}), 404
        
        pp_list = session.query(ParticipacionPersona).filter(
            ParticipacionPersona.participacion == participacion_id
        ).all()
        
        result = []
        for pp in pp_list:
            result.append({
                'id': pp.id,
                'persona_id': pp.persona,
                'participacion_id': pp.participacion
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@participacion_bp.route('/<int:participacion_id>/personas', methods=['POST'])
def add_persona_to_participacion(participacion_id):
    """Add a persona to a participation."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    if 'persona' not in data:
        return jsonify({'success': False, 'message': 'Missing field: persona'}), 400
    
    session = get_session()
    try:
        # Verify participacion exists
        participacion = session.query(Participacion).filter(
            Participacion.id == participacion_id
        ).first()
        
        if not participacion:
            return jsonify({'success': False, 'message': 'Participacion not found'}), 404
        
        # Verify persona exists
        persona = session.query(Persona).filter(Persona.id == data['persona']).first()
        if not persona:
            return jsonify({'success': False, 'message': 'Persona not found'}), 404
        
        pp = ParticipacionPersona(
            participacion=participacion_id,
            persona=data['persona']
        )
        session.add(pp)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona added to participacion',
            'id': pp.id
        }), 201
    except IntegrityError:
        session.rollback()
        return jsonify({'success': False, 'message': 'Integrity error'}), 409
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@participacion_bp.route('/<int:participacion_id>/personas/<int:pp_id>', methods=['DELETE'])
def remove_persona_from_participacion(participacion_id, pp_id):
    """Remove a persona from a participation."""
    session = get_session()
    try:
        pp = session.query(ParticipacionPersona).filter(
            ParticipacionPersona.id == pp_id,
            ParticipacionPersona.participacion == participacion_id
        ).first()
        
        if not pp:
            return jsonify({'success': False, 'message': 'ParticipacionPersona not found'}), 404
        
        session.delete(pp)
        session.commit()
        return jsonify({'success': True, 'message': 'Persona removed from participacion'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


# ============ ROL PARTICIPACION MANAGEMENT ============

@participacion_bp.route('/roles', methods=['GET'])
def list_rol_participacion():
    """List all available participation roles."""
    session = get_session()
    try:
        roles = session.query(RolParticipacion).all()
        
        result = []
        for r in roles:
            result.append({
                'id': r.id,
                'nombre': r.nombre
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@participacion_bp.route('/roles', methods=['POST'])
def create_rol_participacion():
    """Create a new participation role."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    if 'nombre' not in data:
        return jsonify({'success': False, 'message': 'Missing field: nombre'}), 400
    
    session = get_session()
    try:
        rol = RolParticipacion(nombre=data['nombre'])
        session.add(rol)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'RolParticipacion created',
            'id': rol.id
        }), 201
    except IntegrityError:
        session.rollback()
        return jsonify({'success': False, 'message': 'Integrity error'}), 409
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()
