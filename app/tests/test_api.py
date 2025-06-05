import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_db
from app.services.sentiment_analyzer import SentimentAnalyzer

# Créer une base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Remplacer la dépendance de base de données
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    # Créer les tables de test
    Base.metadata.create_all(bind=engine)
    yield
    # Supprimer les tables après les tests
    Base.metadata.drop_all(bind=engine)


def test_analyze_sentiment(test_db):
    """Test de l'analyse de sentiment pour un seul texte"""
    response = client.post(
        "/api/analyze",
        json={"text": "Je suis très content de cette application !"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "polarity" in data
    assert "subjectivity" in data
    assert data["sentiment"] in ["positif", "négatif", "neutre"]
    assert isinstance(data["polarity"], float)
    assert isinstance(data["subjectivity"], float)


def test_analyze_sentiment_batch(test_db):
    """Test de l'analyse de sentiment par lot"""
    response = client.post(
        "/api/analyze/batch",
        json={
            "texts": [
                "Je suis très content de cette application !",
                "Ce service ne fonctionne pas correctement.",
                "Je ne sais pas quoi penser de ce produit."
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3
    for result in data["results"]:
        assert "sentiment" in result
        assert "polarity" in result
        assert "subjectivity" in result


def test_empty_text():
    """Test avec un texte vide"""
    response = client.post(
        "/api/analyze",
        json={"text": ""}
    )
    assert response.status_code == 422  # Validation error


def test_get_texts(test_db):
    """Test de la récupération des textes"""
    # D'abord ajouter quelques textes
    client.post("/api/analyze", json={"text": "Test text 1"})
    client.post("/api/analyze", json={"text": "Test text 2"})
    
    # Récupérer les textes
    response = client.get("/api/texts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_sentiment_analyzer_class():
    """Test de la classe SentimentAnalyzer"""
    analyzer = SentimentAnalyzer()
    
    # Test du prétraitement
    text = "Ceci est un test avec des URL https://example.com et @mentions #hashtags"
    preprocessed = analyzer.preprocess_text(text)
    assert "https://example.com" not in preprocessed
    assert "@mentions" not in preprocessed
    assert "#hashtags" not in preprocessed
    
    # Test de l'analyse
    result = analyzer.analyze_sentiment("Je suis très content !")
    assert "polarity" in result
    assert "subjectivity" in result
    assert "sentiment" in result
    assert result["sentiment"] == "positif"
    
    result = analyzer.analyze_sentiment("Je suis très déçu !")
    assert result["sentiment"] == "négatif"
    
    result = analyzer.analyze_sentiment("Ceci est un test.")
    assert "polarity" in result
