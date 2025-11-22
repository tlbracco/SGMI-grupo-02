from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import hashlib
import hmac
from sqlalchemy import create_engine
from models import init_models, create_session
from sqlalchemy.exc import IntegrityError

# Backend that validates a user's password (MD5) against a Postgres table
# Table expected: login_details(email TEXT PRIMARY KEY, password_hash TEXT)

BASE_DIR = os.path.dirname(__file__)

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


# Initialize SQLAlchemy engine and automapped models
DB_URL = build_db_url() or "postgresql://postgres:Segundo_Francia_2025@db.hxrdfvfeiddvydvilrsa.supabase.co:5432/postgres"
engine = create_engine(DB_URL)
Base = init_models(engine)
Session = create_session(engine)


@app.route("/api/hello")
def get_hello():
    return jsonify({"message": "ESTO ES UNA PRUEBA"})


@app.route('/login', methods=['POST'])
def login():
    """
    Accepts JSON or form data with fields: `email`, `password`.
    Hashes the provided password using MD5 and compares with the value
    stored in the `login_details` table. If they match, returns the
    main page (`FrontEnd/index.html`) with HTTP 200. Otherwise returns 401.
    """
    # Accept JSON or form-encoded data
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

    # Query using automapped SQLAlchemy class
    try:
        login_cls = None
        # direct name
        if hasattr(Base, 'classes') and hasattr(Base.classes, 'login_details'):
            login_cls = getattr(Base.classes, 'login_details')
        else:
            # try case-insensitive lookup
            for name in dir(Base.classes):
                if name.lower() in ('login_details', 'logindetails', 'login'):
                    login_cls = getattr(Base.classes, name)
                    break

        if login_cls is None:
            return jsonify({'success': False, 'message': 'Server misconfiguration: login class not found'}), 500

        session = Session()
        user = session.query(login_cls).filter(getattr(login_cls, 'email') == email).first()
    except Exception:
        return jsonify({'success': False, 'message': 'Database error'}), 500
    finally:
        try:
            Session.remove()
        except Exception:
            pass

    if not user:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    # Determine which column holds the password hash
    cols = [c.name for c in login_cls.__table__.columns]
    candidates = ['password_hash', 'password', 'clave', 'hash']
    colname = None
    for c in candidates:
        if c in cols:
            colname = c
            break
    if colname is None:
        cols_no_email = [c for c in cols if c != 'email']
        colname = cols_no_email[0] if cols_no_email else cols[0]

    stored_hash = getattr(user, colname)

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


def _get_login_class():
    """Return the automapped login_details class or None."""
    if hasattr(Base, 'classes') and hasattr(Base.classes, 'login_details'):
        return getattr(Base.classes, 'login_details')
    for name in dir(Base.classes):
        if name.lower() in ('login_details', 'logindetails', 'login'):
            return getattr(Base.classes, name)
    return None


def _choose_columns(login_cls):
    cols = [c.name for c in login_cls.__table__.columns]
    email_col = 'email' if 'email' in cols else next((c for c in cols if 'mail' in c.lower()), cols[0])
    hash_candidates = ['password_hash', 'password', 'clave', 'hash']
    hash_col = next((c for c in hash_candidates if c in cols), None)
    if not hash_col:
        hash_col = next((c for c in cols if c != email_col), cols[0])
    return email_col, hash_col


@app.route('/register', methods=['POST'])
def register():
    """Create a new user. Expects JSON: {"email": "...", "password": "..."}
    Stores MD5 hex digest in the configured hash column.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'success': False, 'message': 'Missing email or password'}), 400

    login_cls = _get_login_class()
    if login_cls is None:
        return jsonify({'success': False, 'message': 'Server misconfiguration: login class not found'}), 500

    email_col, hash_col = _choose_columns(login_cls)
    digest = hashlib.md5(password.encode('utf-8')).hexdigest()

    session = Session()
    try:
        obj_kwargs = {email_col: email, hash_col: digest}
        user = login_cls(**obj_kwargs)
        session.add(user)
        session.commit()
        return jsonify({'success': True, 'message': 'User created'}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({'success': False, 'message': 'User already exists'}), 409
    except Exception:
        session.rollback()
        return jsonify({'success': False, 'message': 'Database error'}), 500
    finally:
        try:
            Session.remove()
        except Exception:
            pass


@app.route('/user/<string:email>', methods=['PUT'])
def modify_user(email):
    """Modify user fields. Currently supports changing `password`.
    Expects JSON with fields to update, e.g. {"password": "newpass"}.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400

    login_cls = _get_login_class()
    if login_cls is None:
        return jsonify({'success': False, 'message': 'Server misconfiguration: login class not found'}), 500

    email_col, hash_col = _choose_columns(login_cls)

    session = Session()
    try:
        user = session.query(login_cls).filter(getattr(login_cls, email_col) == email).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        updated = False
        if 'password' in data and isinstance(data['password'], str):
            new_digest = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
            setattr(user, hash_col, new_digest)
            updated = True

        # allow updating non-primary simple fields if provided
        for key, val in data.items():
            if key in (email_col, 'password'):
                continue
            if key in [c.name for c in login_cls.__table__.columns]:
                setattr(user, key, val)
                updated = True

        if updated:
            session.commit()
            return jsonify({'success': True, 'message': 'User updated'}), 200
        else:
            return jsonify({'success': False, 'message': 'No updatable fields provided'}), 400
    except Exception:
        session.rollback()
        return jsonify({'success': False, 'message': 'Database error'}), 500
    finally:
        try:
            Session.remove()
        except Exception:
            pass


@app.route('/user/<string:email>/deactivate', methods=['POST'])
def deactivate_user(email):
    """Deactivate a user. If an `active` or `is_active` column exists, set it to False.
    Otherwise, delete the user row.
    """
    login_cls = _get_login_class()
    if login_cls is None:
        return jsonify({'success': False, 'message': 'Server misconfiguration: login class not found'}), 500

    session = Session()
    try:
        email_col, hash_col = _choose_columns(login_cls)
        user = session.query(login_cls).filter(getattr(login_cls, email_col) == email).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        cols = [c.name for c in login_cls.__table__.columns]
        if 'active' in cols:
            setattr(user, 'active', False)
            session.commit()
            return jsonify({'success': True, 'message': 'User deactivated'}), 200
        if 'is_active' in cols:
            setattr(user, 'is_active', False)
            session.commit()
            return jsonify({'success': True, 'message': 'User deactivated'}), 200

        # fallback: delete row
        session.delete(user)
        session.commit()
        return jsonify({'success': True, 'message': 'User deleted'}), 200
    except Exception:
        session.rollback()
        return jsonify({'success': False, 'message': 'Database error'}), 500
    finally:
        try:
            Session.remove()
        except Exception:
            pass


if __name__ == '__main__':
    app.run(debug=True, port=5000)