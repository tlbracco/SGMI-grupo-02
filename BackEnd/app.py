from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import hashlib
import hmac
import psycopg2
import psycopg2.extras

# Backend that validates a user's password (MD5) against a Postgres table
# Table expected: login_details(email TEXT PRIMARY KEY, password_hash TEXT)

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__)
CORS(app)


def get_pg_connection():
    """Create a psycopg2 connection using DATABASE_URL or individual env vars.
    
    Environment variables supported:
      - DATABASE_URL (preferred)
      - PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
    """
    # database_url = os.getenv("DATABASE_URL")
    database_url = "postgresql://postgres:Segundo_Francia_2025@db.hxrdfvfeiddvydvilrsa.supabase.co:5432/postgres"
    if database_url:
        return psycopg2.connect(database_url)

#    params = {
#        'host': os.getenv('PGHOST', 'localhost'),
#        'port': os.getenv('PGPORT', '5432'),
#        'user': os.getenv('PGUSER', ''),
#        'password': os.getenv('PGPASSWORD', ''),
#        'dbname': os.getenv('PGDATABASE', '')
#    }
    # Remove empty values so psycopg2 uses defaults where appropriate
    params = {k: v for k, v in params.items() if v}
    return psycopg2.connect(**params)


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

    try:
        conn = get_pg_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT clave FROM login_details WHERE email = %s', (email,))
        row = cur.fetchone()
    except Exception as e:
        # Log in real app; return generic error here
        return jsonify({'success': False, 'message': 'Database error'}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass

    if not row:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    stored_hash = row['clave'] if isinstance(row, dict) or hasattr(row, 'keys') else row[0]

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


if __name__ == '__main__':
    app.run(debug=True, port=5000)