"""SQLAlchemy ORM models generated from Instalación.v0.1.sql

All tables are mapped as declarative classes with:
- __init__ methods for easy instantiation
- Foreign key relationships
- Proper type hints and constraints
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, LargeBinary, Money, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ============ Enum/Lookup Tables ============

class GradoAcademico(Base):
    __tablename__ = 'grado_academico'
    
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String, nullable=False)
    
    def __init__(self, nombre: str, id: Optional[BigInteger] = None):
        self.id = id
        self.nombre = nombre
    
    personas = relationship('Persona', back_populates='grado_academico_ref')


class RolGrupo(Base):
    __tablename__ = 'rol_grupo'
    
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String, nullable=False)
    
    def __init__(self, nombre: str, id: Optional[BigInteger] = None):
        self.id = id
        self.nombre = nombre
    
    persona_grupos = relationship('PersonaGrupo', back_populates='rol_grupo_ref')


class RolParticipacion(Base):
    __tablename__ = 'rol_participacion'
    
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String, nullable=False)
    
    def __init__(self, nombre: str, id: Optional[BigInteger] = None):
        self.id = id
        self.nombre = nombre
    
    participaciones = relationship('Participacion', back_populates='rol_participacion_ref')


class TipoContrato(Base):
    __tablename__ = 'tipo_contrato'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    
    def __init__(self, nombre: str, id: Optional[Integer] = None):
        self.id = id
        self.nombre = nombre
    
    contratos = relationship('Contrato', back_populates='tipo_contrato_ref')


class TipoErogacion(Base):
    __tablename__ = 'tipo_erogacion'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    
    def __init__(self, nombre: str, id: Optional[Integer] = None):
        self.id = id
        self.nombre = nombre
    
    erogaciones = relationship('Erogacion', back_populates='tipo_erogacion_ref')


# ============ Core Tables ============

class Institucion(Base):
    __tablename__ = 'institucion'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(Text, nullable=False)
    pais = Column(String)
    
    def __init__(self, descripcion: str, pais: Optional[str] = None, id: Optional[Integer] = None):
        self.id = id
        self.descripcion = descripcion
        self.pais = pais
    
    personas = relationship('Persona', back_populates='institucion_ref')
    persona_grupos = relationship('PersonaGrupo', back_populates='institucion_ref', foreign_keys='PersonaGrupo.institucion')
    revistas = relationship('Revista', back_populates='editorial_ref')
    articulos = relationship('Articulo', back_populates='editorial_ref')
    libros = relationship('Libro', back_populates='editorial_ref')
    contratos_adoptante = relationship('Contrato', back_populates='adoptante_ref', foreign_keys='Contrato.adoptante')
    contratos_demandante = relationship('Contrato', back_populates='demandante_ref', foreign_keys='Contrato.demandante')
    participaciones = relationship('Participacion', back_populates='institucion_ref', foreign_keys='Participacion.institucion')
    actividades_docentes = relationship('ActividadDocente', back_populates='institucion_ref')
    distinciones = relationship('Distincion', back_populates='institucion_ref')
    erogaciones = relationship('Erogacion', back_populates='institucion_ref')


class Documentacion(Base):
    __tablename__ = 'documentacion'
    
    id = Column(BigInteger, primary_key=True)
    binario = Column(LargeBinary)
    texto = Column(Text)
    
    def __init__(self, binario: Optional[bytes] = None, texto: Optional[str] = None, id: Optional[BigInteger] = None):
        self.id = id
        self.binario = binario
        self.texto = texto
    
    revistas = relationship('Revista', back_populates='documentacion_ref')
    articulos = relationship('Articulo', back_populates='documentacion_ref')
    libros = relationship('Libro', back_populates='documentacion_ref')


class Grupo(Base):
    __tablename__ = 'grupo'
    
    id = Column(Integer, primary_key=True)
    sigla = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    objetivos = Column(Text, nullable=False)
    organigrama = Column(String)
    consejo_ejecutivo = Column(String)
    unidad_academica = Column(String)
    
    def __init__(self, sigla: str, nombre: str, objetivos: str, organigrama: Optional[str] = None,
                 consejo_ejecutivo: Optional[str] = None, unidad_academica: Optional[str] = None,
                 id: Optional[Integer] = None):
        self.id = id
        self.sigla = sigla
        self.nombre = nombre
        self.objetivos = objetivos
        self.organigrama = organigrama
        self.consejo_ejecutivo = consejo_ejecutivo
        self.unidad_academica = unidad_academica
    
    proyectos = relationship('Proyecto', back_populates='grupo_ref')
    persona_grupos = relationship('PersonaGrupo', back_populates='grupo_ref')
    equipamientos = relationship('Equipamiento', back_populates='grupo_ref')
    bibliografias = relationship('Bibliografia', back_populates='grupo_ref')
    participaciones = relationship('Participacion', back_populates='grupo_ref')
    distinciones = relationship('Distincion', back_populates='grupo_ref', foreign_keys='Distincion.grupo')

class LoginCredentials(Base):
    __tablename__ = 'login_details'
    
    email = Column(String, primary_key=True)
    clave = Column(String, nullable=False)
    persona = Column(Integer, ForeignKey('persona.id'))
    activo = Column(bool, default=True)

    def __init__(self, email: str, clave: str, persona: Optional[int] = None):
        self.email = email
        self.clave = clave
        self.persona = persona
        self.activo = True

    persona_ref = relationship('Persona', back_populates='login_credentials')

class Persona(Base):
    __tablename__ = 'persona'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    horas = Column(String, nullable=False)
    grado_academico = Column(Integer, ForeignKey('grado_academico.id'), nullable=False)
    object_type = Column(String, nullable=False)
    categoria = Column(String)
    incentivo = Column(String)
    dedicacion = Column(String)
    especialidad = Column(String)
    descripcion = Column(String)
    institucion = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    
    def __init__(self, nombre: str, apellido: str, horas: str, grado_academico: int, object_type: str,
                 institucion: int, categoria: Optional[str] = None, incentivo: Optional[str] = None,
                 dedicacion: Optional[str] = None, especialidad: Optional[str] = None,
                 descripcion: Optional[str] = None, id: Optional[Integer] = None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.horas = horas
        self.grado_academico = grado_academico
        self.object_type = object_type
        self.categoria = categoria
        self.incentivo = incentivo
        self.dedicacion = dedicacion
        self.especialidad = especialidad
        self.descripcion = descripcion
        self.institucion = institucion
    
    grado_academico_ref = relationship('GradoAcademico', back_populates='personas')
    institucion_ref = relationship('Institucion', back_populates='personas')
    persona_grupos = relationship('PersonaGrupo', back_populates='persona_ref')
    participacion_personas = relationship('ParticipacionPersona', back_populates='persona_ref')
    actividades_docentes = relationship('ActividadDocente', back_populates='persona_ref')
    distinciones = relationship('Distincion', back_populates='persona_ref', foreign_keys='Distincion.persona')
    login_credentials = relationship('LoginCredentials', back_populates='persona_ref')


class Proyecto(Base):
    __tablename__ = 'proyecto'
    
    id = Column(Integer, primary_key=True)
    grupo = Column(Integer, ForeignKey('grupo.id'), nullable=False)
    tipo = Column(String, nullable=False)
    codigo = Column(String, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    logros = Column(Text)
    dificultades = Column(Text)
    
    def __init__(self, grupo: int, tipo: str, codigo: str, fecha_inicio: date, nombre: str,
                 descripcion: str, fecha_fin: Optional[date] = None, logros: Optional[str] = None,
                 dificultades: Optional[str] = None, id: Optional[Integer] = None):
        self.id = id
        self.grupo = grupo
        self.tipo = tipo
        self.codigo = codigo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.nombre = nombre
        self.descripcion = descripcion
        self.logros = logros
        self.dificultades = dificultades
    
    grupo_ref = relationship('Grupo', back_populates='proyectos')
    proyecto_libros = relationship('ProyectoLibro', back_populates='proyecto_ref')
    proyecto_revistas = relationship('ProyectoRevista', back_populates='proyecto_ref')
    proyecto_articulos = relationship('ProyectoArticulo', back_populates='proyecto_ref')
    distinciones = relationship('Distincion', back_populates='proyecto_ref')


class PersonaGrupo(Base):
    __tablename__ = 'persona_grupo'
    
    id = Column(BigInteger, primary_key=True)
    grupo = Column(Integer, ForeignKey('grupo.id'), nullable=False)
    persona = Column(Integer, ForeignKey('persona.id'), nullable=False)
    institucion = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    rol = Column(BigInteger, ForeignKey('rol_grupo.id'), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    
    def __init__(self, grupo: int, persona: int, institucion: int, rol: int, fecha_inicio: date,
                 fecha_fin: Optional[date] = None, id: Optional[BigInteger] = None):
        self.id = id
        self.grupo = grupo
        self.persona = persona
        self.institucion = institucion
        self.rol = rol
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
    
    grupo_ref = relationship('Grupo', back_populates='persona_grupos')
    persona_ref = relationship('Persona', back_populates='persona_grupos')
    institucion_ref = relationship('Institucion', back_populates='persona_grupos', foreign_keys=[institucion])
    rol_grupo_ref = relationship('RolGrupo', back_populates='persona_grupos')


class Equipamiento(Base):
    __tablename__ = 'equipamiento'
    
    id = Column(BigInteger, primary_key=True)
    denominacion = Column(String, nullable=False)
    fechaIngreso = Column(Date, nullable=False)
    monto = Column(Money, nullable=False)
    descripción = Column(Text)
    grupo = Column(Integer, ForeignKey('grupo.id'), nullable=False)
    actividad = Column(BigInteger)
    proyecto = Column(BigInteger)
    
    def __init__(self, denominacion: str, fechaIngreso: date, monto, grupo: int,
                 descripción: Optional[str] = None, actividad: Optional[BigInteger] = None,
                 proyecto: Optional[BigInteger] = None, id: Optional[BigInteger] = None):
        self.id = id
        self.denominacion = denominacion
        self.fechaIngreso = fechaIngreso
        self.monto = monto
        self.descripción = descripción
        self.grupo = grupo
        self.actividad = actividad
        self.proyecto = proyecto
    
    grupo_ref = relationship('Grupo', back_populates='equipamientos')


class Revista(Base):
    __tablename__ = 'revista'
    
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String, nullable=False)
    issn = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    editorial = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    numero = Column(String)
    documentacion = Column(BigInteger, ForeignKey('documentacion.id'), nullable=False)
    
    def __init__(self, nombre: str, issn: str, fecha: date, editorial: int, documentacion: int,
                 numero: Optional[str] = None, id: Optional[BigInteger] = None):
        self.id = id
        self.nombre = nombre
        self.issn = issn
        self.fecha = fecha
        self.editorial = editorial
        self.numero = numero
        self.documentacion = documentacion
    
    editorial_ref = relationship('Institucion', back_populates='revistas')
    documentacion_ref = relationship('Documentacion', back_populates='revistas')
    proyecto_revistas = relationship('ProyectoRevista', back_populates='revista_ref')


class Articulo(Base):
    __tablename__ = 'articulo'
    
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String, nullable=False)
    issn = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    editorial = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    numero = Column(String)
    pais = Column(String)
    copia = Column(String)
    documentacion = Column(BigInteger, ForeignKey('documentacion.id'), nullable=False)
    
    def __init__(self, nombre: str, issn: str, fecha: date, editorial: int, documentacion: int,
                 numero: Optional[str] = None, pais: Optional[str] = None, copia: Optional[str] = None,
                 id: Optional[BigInteger] = None):
        self.id = id
        self.nombre = nombre
        self.issn = issn
        self.fecha = fecha
        self.editorial = editorial
        self.numero = numero
        self.pais = pais
        self.copia = copia
        self.documentacion = documentacion
    
    editorial_ref = relationship('Institucion', back_populates='articulos')
    documentacion_ref = relationship('Documentacion', back_populates='articulos')
    proyecto_articulos = relationship('ProyectoArticulo', back_populates='articulo_ref')


class Libro(Base):
    __tablename__ = 'libro'
    
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String)
    isbn = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    editorial = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    tomo = Column(String)
    capitulo = Column(String)
    pais = Column(String)
    documentacion = Column(BigInteger, ForeignKey('documentacion.id'), nullable=False)
    
    def __init__(self, isbn: str, fecha: date, editorial: int, documentacion: int, nombre: Optional[str] = None,
                 tomo: Optional[str] = None, capitulo: Optional[str] = None, pais: Optional[str] = None,
                 id: Optional[BigInteger] = None):
        self.id = id
        self.nombre = nombre
        self.isbn = isbn
        self.fecha = fecha
        self.editorial = editorial
        self.tomo = tomo
        self.capitulo = capitulo
        self.pais = pais
        self.documentacion = documentacion
    
    editorial_ref = relationship('Institucion', back_populates='libros')
    documentacion_ref = relationship('Documentacion', back_populates='libros')
    proyecto_libros = relationship('ProyectoLibro', back_populates='libro_ref')


class ProyectoLibro(Base):
    __tablename__ = 'proyecto_libro'
    
    id = Column(BigInteger, primary_key=True)
    proyecto = Column(Integer, ForeignKey('proyecto.id'), nullable=False)
    libro = Column(BigInteger, ForeignKey('libro.id'), nullable=False)
    
    def __init__(self, proyecto: int, libro: int, id: Optional[BigInteger] = None):
        self.id = id
        self.proyecto = proyecto
        self.libro = libro
    
    proyecto_ref = relationship('Proyecto', back_populates='proyecto_libros')
    libro_ref = relationship('Libro', back_populates='proyecto_libros')


class ProyectoRevista(Base):
    __tablename__ = 'proyecto_revista'
    
    id = Column(BigInteger, primary_key=True)
    proyecto = Column(Integer, ForeignKey('proyecto.id'), nullable=False)
    revista = Column(BigInteger, ForeignKey('revista.id'), nullable=False)
    
    def __init__(self, proyecto: int, revista: int, id: Optional[BigInteger] = None):
        self.id = id
        self.proyecto = proyecto
        self.revista = revista
    
    proyecto_ref = relationship('Proyecto', back_populates='proyecto_revistas')
    revista_ref = relationship('Revista', back_populates='proyecto_revistas')


class ProyectoArticulo(Base):
    __tablename__ = 'proyecto_articulo'
    
    id = Column(BigInteger, primary_key=True)
    proyecto = Column(Integer, ForeignKey('proyecto.id'), nullable=False)
    articulo = Column(BigInteger, ForeignKey('articulo.id'), nullable=False)
    
    def __init__(self, proyecto: int, articulo: int, id: Optional[BigInteger] = None):
        self.id = id
        self.proyecto = proyecto
        self.articulo = articulo
    
    proyecto_ref = relationship('Proyecto', back_populates='proyecto_articulos')
    articulo_ref = relationship('Articulo', back_populates='proyecto_articulos')


class Bibliografia(Base):
    __tablename__ = 'bibliografia'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    autores = Column(String, nullable=False)
    editorial = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    grupo = Column(Integer, ForeignKey('grupo.id'), nullable=False)
    
    def __init__(self, titulo: str, autores: str, editorial: str, fecha: date, grupo: int,
                 id: Optional[Integer] = None):
        self.id = id
        self.titulo = titulo
        self.autores = autores
        self.editorial = editorial
        self.fecha = fecha
        self.grupo = grupo
    
    grupo_ref = relationship('Grupo', back_populates='bibliografias')


class Contrato(Base):
    __tablename__ = 'contrato'
    
    id = Column(BigInteger, primary_key=True)
    adoptante = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    demandante = Column(Integer, ForeignKey('institucion.id'))
    tipo = Column(Integer, ForeignKey('tipo_contrato.id'), nullable=False)
    monto = Column(Money, nullable=False)
    denominacion = Column(String, nullable=False)
    descripcion = Column(Text)
    
    def __init__(self, adoptante: int, tipo: int, monto, denominacion: str, demandante: Optional[int] = None,
                 descripcion: Optional[str] = None, id: Optional[BigInteger] = None):
        self.id = id
        self.adoptante = adoptante
        self.demandante = demandante
        self.tipo = tipo
        self.monto = monto
        self.denominacion = denominacion
        self.descripcion = descripcion
    
    adoptante_ref = relationship('Institucion', back_populates='contratos_adoptante', foreign_keys=[adoptante])
    demandante_ref = relationship('Institucion', back_populates='contratos_demandante', foreign_keys=[demandante])
    tipo_contrato_ref = relationship('TipoContrato', back_populates='contratos')


class Participacion(Base):
    __tablename__ = 'participacion'
    
    id = Column(BigInteger, primary_key=True)
    grupo = Column(Integer, ForeignKey('grupo.id'), nullable=False)
    personal = Column(Integer)
    rol = Column(BigInteger, ForeignKey('rol_participacion.id'), nullable=False)
    institucion = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    
    def __init__(self, grupo: int, rol: int, institucion: int, personal: Optional[int] = None,
                 id: Optional[BigInteger] = None):
        self.id = id
        self.grupo = grupo
        self.personal = personal
        self.rol = rol
        self.institucion = institucion
    
    grupo_ref = relationship('Grupo', back_populates='participaciones')
    rol_participacion_ref = relationship('RolParticipacion', back_populates='participaciones')
    institucion_ref = relationship('Institucion', back_populates='participaciones', foreign_keys=[institucion])
    participacion_personas = relationship('ParticipacionPersona', back_populates='participacion_ref')


class ParticipacionPersona(Base):
    __tablename__ = 'participacion_persona'
    
    id = Column(BigInteger, primary_key=True)
    participacion = Column(BigInteger, ForeignKey('participacion.id'), nullable=False)
    persona = Column(Integer, ForeignKey('persona.id'), nullable=False)
    
    def __init__(self, participacion: int, persona: int, id: Optional[BigInteger] = None):
        self.id = id
        self.participacion = participacion
        self.persona = persona
    
    participacion_ref = relationship('Participacion', back_populates='participacion_personas')
    persona_ref = relationship('Persona', back_populates='participacion_personas')


class ActividadDocente(Base):
    __tablename__ = 'actividad_docente'
    
    id = Column(BigInteger, primary_key=True)
    persona = Column(Integer, ForeignKey('persona.id'), nullable=False)
    rol = Column(String, nullable=False)
    institucion = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    
    def __init__(self, persona: int, rol: str, institucion: int, fecha_inicio: date,
                 fecha_fin: Optional[date] = None, id: Optional[BigInteger] = None):
        self.id = id
        self.persona = persona
        self.rol = rol
        self.institucion = institucion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
    
    persona_ref = relationship('Persona', back_populates='actividades_docentes')
    institucion_ref = relationship('Institucion', back_populates='actividades_docentes')


class Distincion(Base):
    __tablename__ = 'distincion'
    
    id = Column(BigInteger, primary_key=True)
    proyecto = Column(Integer, ForeignKey('proyecto.id'), nullable=False)
    persona = Column(Integer, ForeignKey('persona.id'))
    grupo = Column(Integer, ForeignKey('grupo.id'))
    fecha = Column(Date, nullable=False)
    institucion = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    
    def __init__(self, proyecto: int, fecha: date, institucion: int, persona: Optional[int] = None,
                 grupo: Optional[int] = None, id: Optional[BigInteger] = None):
        self.id = id
        self.proyecto = proyecto
        self.persona = persona
        self.grupo = grupo
        self.fecha = fecha
        self.institucion = institucion
    
    proyecto_ref = relationship('Proyecto', back_populates='distinciones')
    persona_ref = relationship('Persona', back_populates='distinciones', foreign_keys=[persona])
    grupo_ref = relationship('Grupo', back_populates='distinciones', foreign_keys=[grupo])
    institucion_ref = relationship('Institucion', back_populates='distinciones')


class Erogacion(Base):
    __tablename__ = 'erogacion'
    
    id = Column(BigInteger, primary_key=True)
    institucion = Column(Integer, ForeignKey('institucion.id'), nullable=False)
    tipo = Column(Integer, ForeignKey('tipo_erogacion.id'), nullable=False)
    fecha = Column(DateTime, nullable=False)
    descripción = Column(Text)
    monto = Column(Money, nullable=False)
    comprobante = Column(LargeBinary, nullable=False)
    
    def __init__(self, institucion: int, tipo: int, fecha: datetime, monto, comprobante: bytes,
                 descripción: Optional[str] = None, id: Optional[BigInteger] = None):
        self.id = id
        self.institucion = institucion
        self.tipo = tipo
        self.fecha = fecha
        self.descripción = descripción
        self.monto = monto
        self.comprobante = comprobante
    
    institucion_ref = relationship('Institucion', back_populates='erogaciones')
    tipo_erogacion_ref = relationship('TipoErogacion', back_populates='erogaciones')
