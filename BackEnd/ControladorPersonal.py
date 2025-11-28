"""Controlador de Personal - API endpoints for managing personal (staff/researchers).

Uses SQLAlchemy ORM models from models_db to handle CRUD operations
on Persona, ActividadDocente, and related entities.
"""

import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, jsonify

# Import ORM models
from models_db import (
    Base, Persona, ActividadDocente, Institucion,
    GradoAcademico, LoginCredentials
)

# Create blueprint for personal management routes
personal_bp = Blueprint('personal', __name__, url_prefix='/api/personal')

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


# ============ PERSONA CRUD ENDPOINTS ============

@personal_bp.route('', methods=['GET'])
def list_personas():
    """List all personas with optional filtering."""
    session = get_session()
    try:
        # Optional filters
        object_type = request.args.get('object_type')
        
        query = session.query(Persona)
        if object_type:
            query = query.filter(Persona.object_type == object_type)
        
        personas = query.all()
        
        result = []
        for p in personas:
            result.append({
                'id': p.id,
                'nombre': p.nombre,
                'apellido': p.apellido,
                'horas': p.horas,
                'object_type': p.object_type,
                'categoria': p.categoria,
                'especialidad': p.especialidad,
                'institucion_id': p.institucion
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@personal_bp.route('', methods=['POST'])
def create_persona():
    """Create a new persona (Investigador, Profesional, Soporte, Visitante, Becario)."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    required = ['nombre', 'apellido', 'horas', 'object_type', 'grado_academico', 'institucion', 'email']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'success': False, 'message': f'Missing fields: {missing}'}), 400
    
    session = get_session()
    try:
        persona = Persona(
            nombre=data['nombre'],
            apellido=data['apellido'],
            horas=data['horas'],       
            object_type=data['object_type'],
            grado_academico=data['grado_academico'],
            institucion=data['institucion'],
            categoria=data.get('categoria'),
            incentivo=data.get('incentivo'),
            dedicacion=data.get('dedicacion'),
            especialidad=data.get('especialidad'),
            descripcion=data.get('descripcion')
        )
        session.add(persona)
        session.flush()  # Flush to get the persona.id without committing
        
        # Create LoginCredentials for the new persona
        login_credentials = LoginCredentials(
            email=data['email'],
            clave=data.get('clave', ''),  # Optional: password/clave
            persona=persona.id
        )
        session.add(login_credentials)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona created',
            'id': persona.id,
            'email': data['email']
        }), 201
    except IntegrityError:
        session.rollback()
        return jsonify({'success': False, 'message': 'Integrity error'}), 409
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@personal_bp.route('/<int:persona_id>', methods=['GET'])
def get_persona(persona_id):
    """Get details of a specific persona."""
    session = get_session()
    try:
        persona = session.query(Persona).filter(Persona.id == persona_id).first()
        if not persona:
            return jsonify({'success': False, 'message': 'Persona not found'}), 404
        
        return jsonify({
            'id': persona.id,
            'nombre': persona.nombre,
            'apellido': persona.apellido,
            'horas': persona.horas,
            'object_type': persona.object_type,
            'categoria': persona.categoria,
            'incentivo': persona.incentivo,
            'dedicacion': persona.dedicacion,
            'especialidad': persona.especialidad,
            'descripcion': persona.descripcion,
            'grado_academico_id': persona.grado_academico,
            'institucion_id': persona.institucion
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@personal_bp.route('/<int:persona_id>', methods=['PUT'])
def update_persona(persona_id):
    """Update a persona's fields."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    session = get_session()
    try:
        persona = session.query(Persona).filter(Persona.id == persona_id).first()
        if not persona:
            return jsonify({'success': False, 'message': 'Persona not found'}), 404
        
        # Update allowed fields
        allowed_fields = ['nombre', 'apellido', 'horas', 'categoria', 'incentivo',
                         'dedicacion', 'especialidad', 'descripcion']
        for field in allowed_fields:
            if field in data:
                setattr(persona, field, data[field])
        
        session.commit()
        return jsonify({'success': True, 'message': 'Persona updated'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


# ============ ACTIVIDAD DOCENTE ENDPOINTS ============

@personal_bp.route('/<int:persona_id>/actividades-docentes', methods=['GET'])
def get_actividades_docentes(persona_id):
    """Get all teaching activities for a persona."""
    session = get_session()
    try:
        actividades = session.query(ActividadDocente).filter(
            ActividadDocente.persona == persona_id
        ).all()
        
        result = []
        for act in actividades:
            result.append({
                'id': act.id,
                'rol': act.rol,
                'institucion_id': act.institucion,
                'fecha_inicio': act.fecha_inicio.isoformat(),
                'fecha_fin': act.fecha_fin.isoformat() if act.fecha_fin else None
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@personal_bp.route('/<int:persona_id>/actividades-docentes', methods=['POST'])
def create_actividad_docente(persona_id):
    """Create a new teaching activity for a persona."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    
    required = ['rol', 'institucion', 'fecha_inicio']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'success': False, 'message': f'Missing fields: {missing}'}), 400
    
    session = get_session()
    try:
        actividad = ActividadDocente(
            persona=persona_id,
            rol=data['rol'],
            institucion=data['institucion'],
            fecha_inicio=date.fromisoformat(data['fecha_inicio']),
            fecha_fin=date.fromisoformat(data['fecha_fin']) if data.get('fecha_fin') else None
        )
        session.add(actividad)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Teaching activity created',
            'id': actividad.id
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@personal_bp.route('/<int:persona_id>/actividades-docentes/<int:act_id>', methods=['DELETE'])
def delete_actividad_docente(persona_id, act_id):
    """Delete a teaching activity."""
    session = get_session()
    try:
        actividad = session.query(ActividadDocente).filter(
            ActividadDocente.id == act_id,
            ActividadDocente.persona == persona_id
        ).first()
        
        if not actividad:
            return jsonify({'success': False, 'message': 'Activity not found'}), 404
        
        session.delete(actividad)
        session.commit()
        return jsonify({'success': True, 'message': 'Teaching activity deleted'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


@personal_bp.route('/<int:persona_id>/deactivate', methods=['PUT'])
def deactivate_persona(persona_id):
    """Deactivate a persona by setting their LoginCredentials.activo to False."""
    session = get_session()
    try:
        # Find the persona
        persona = session.query(Persona).filter(Persona.id == persona_id).first()
        if not persona:
            return jsonify({'success': False, 'message': 'Persona not found'}), 404
        
        # Find and deactivate their login credentials
        login_creds = session.query(LoginCredentials).filter(
            LoginCredentials.persona == persona_id
        ).first()
        
        if not login_creds:
            return jsonify({'success': False, 'message': 'LoginCredentials not found for this persona'}), 404
        
        login_creds.activo = False
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona deactivated successfully',
            'persona_id': persona_id,
            'email': login_creds.email,
            'activo': login_creds.activo
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()


