from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

from app.config import active_config

# Création de la base de données
engine = create_engine(active_config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TextData(Base):
    """Modèle pour les données textuelles à analyser"""
    __tablename__ = "text_data"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SentimentAnalysis(Base):
    """Modèle pour les résultats de l'analyse de sentiments"""
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    text_id = Column(Integer, nullable=False)
    polarity = Column(Float, nullable=False)  # Valeur entre -1 (négatif) et 1 (positif)
    subjectivity = Column(Float, nullable=False)  # Valeur entre 0 (objectif) et 1 (subjectif)
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)


# Création des tables dans la base de données
def init_db():
    Base.metadata.create_all(bind=engine)


# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
