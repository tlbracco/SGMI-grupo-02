"""Utility: connect to DB, automap tables and print discovered classes.

This script uses env vars (`DATABASE_URL` or `PGHOST`/`PGUSER`/etc.) to
connect. It's a helper to quickly verify that your Supabase schema can be
reflected and that classes are available.

Run:
    python BackEnd\generate_models.py
"""
import os
from sqlalchemy import create_engine
from models import init_models, create_session


def build_db_url():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    # Fallback to individual env vars
    user = os.getenv('PGUSER', '')
    password = os.getenv('PGPASSWORD', '')
    host = os.getenv('PGHOST', 'localhost')
    port = os.getenv('PGPORT', '5432')
    db = os.getenv('PGDATABASE', '')
    if user and password and db:
        return f'postgresql://{user}:{password}@{host}:{port}/{db}'
    raise RuntimeError('No DATABASE_URL or PG* env vars found')


def main():
    url = build_db_url()
    engine = create_engine(url)
    Base = init_models(engine)
    classes = getattr(Base, 'classes', None)
    if not classes:
        print('No classes discovered')
        return
    print('Discovered mapped classes:')
    for name in sorted(classes._decl_class_registry.keys()):
        if name == '_sa_module_registry':
            continue
        print(' -', name)


if __name__ == '__main__':
    main()
