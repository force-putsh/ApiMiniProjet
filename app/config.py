import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class Config:
    """Configuration de base pour l'application"""
    # Configuration générale
    PROJECT_NAME = "Analyse de Sentiments API"
    VERSION = "1.0.0"
    DESCRIPTION = "API d'analyse de sentiments utilisant TextBlob et NLTK"
    
    # Configuration de la base de données
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentiment_analysis.db")
    
    # Configuration de l'API
    API_PREFIX = "/api"
    
    # Répertoire de données
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement"""
    DEBUG = True


class TestingConfig(Config):
    """Configuration pour l'environnement de test"""
    TESTING = True
    DATABASE_URL = "sqlite:///./test_sentiment_analysis.db"


class ProductionConfig(Config):
    """Configuration pour l'environnement de production"""
    DEBUG = False


# Dictionnaire des configurations disponibles
config_by_name = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig
}

# Configuration active (par défaut : développement)
active_config = config_by_name[os.getenv("FLASK_ENV", "dev")]
