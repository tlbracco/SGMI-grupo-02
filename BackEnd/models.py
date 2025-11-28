"""Runtime model loader using SQLAlchemy's automap.

Call `init_models(engine)` with a SQLAlchemy `Engine` connected to your
Supabase/Postgres database. It will reflect the database schema and return
the prepared `Base` where mapped classes are available under `Base.classes`.

Example:
    from sqlalchemy import create_engine
    from BackEnd.models import init_models

    engine = create_engine(os.environ['DATABASE_URL'])
    Base = init_models(engine)
    # Access user model (if table name is login_details):
    LoginCredentials = Base.classes.login_details

"""
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker


def init_models(engine):
    """Reflect DB and prepare automapped classes.

    Returns the prepared Base (automap_base()) whose mapped classes are in
    `Base.classes` and can be used with a Session bound to `engine`.
    """
    Base = automap_base()
    # reflect the tables
    Base.prepare(engine, reflect=True)
    return Base


def create_session(engine):
    """Create a scoped session bound to `engine`."""
    SessionFactory = sessionmaker(bind=engine)
    return scoped_session(SessionFactory)
