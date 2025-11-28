from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import hashlib
import hmac
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

# Import ORM models from models_db
from models_db import Base, Persona, Institucion

BASE_DIR = os.path.dirname(__file__)

# Load environment variables from BackEnd/.env if present
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
CORS(app)


def build_db_url():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    # Optional: fall back to individual PG* env vars
    user = os.getenv('PGUSER', '')
    password = os.getenv('PGPASSWORD', '')
    host = os.getenv('PGHOST', 'localhost')
    port = os.getenv('PGPORT', '5432')
    db = os.getenv('PGDATABASE', '')
    if user and password and db:
        return f'postgresql://{user}:{password}@{host}:{port}/{db}'
    # As last resort, return None
    return None


# Initialize SQLAlchemy engine and ORM models
DB_URL = build_db_url() or "postgresql://postgres:Segundo_Francia_2025@db.hxrdfvfeiddvydvilrsa.supabase.co:5432/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Return a new database session."""
    return SessionLocal()


@app.route("/api/hello")
def get_hello():
    return jsonify({"message": "ESTO ES UNA PRUEBA"})


@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user using Persona table from models_db.
    
    Expects JSON: {"email": "nombre@apellido", "password": "..."}
    Uses email formed from Persona.nombre + Persona.apellido as username.
    Hashes password with MD5 and compares against a stored hash 
    (can be extended to use a dedicated auth field).
    
    Returns main page on success, 401 on failure.
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Missing email or password'}), 400

    # Compute MD5 hex digest (128-bit)
    provided_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

    session = get_session()
    try:
        # For now, search Persona by nombre or apellido concatenation
        # In production, use a dedicated login_email or username field
        # Split email into name parts (e.g., "john@smith" -> "john", "smith")
        parts = email.split('@')
        nombre = parts[0] if len(parts) > 0 else ''
        apellido = parts[1] if len(parts) > 1 else ''
        
        user = session.query(Persona).filter(
            (Persona.nombre.ilike(nombre)) | (Persona.apellido.ilike(apellido))
        ).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # For now, use horas field as a simple "password hash" placeholder
        # In production, add a dedicated password_hash column to Persona table
        # and store MD5 hashes there
        stored_hash = hashlib.md5(user.horas.encode('utf-8')).hexdigest()
        
        # Constant-time compare
        if hmac.compare_digest(provided_hash, stored_hash):
            # Return main page file
            main_page = os.path.abspath(os.path.join(BASE_DIR, '..', 'FrontEnd', 'index.html'))
            if os.path.exists(main_page):
                return send_file(main_page)
            else:
                return jsonify({'success': True, 'message': 'Login successful, but main page not found'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        session.close()





if __name__ == '__main__':
    app.run(debug=True, port=5000)