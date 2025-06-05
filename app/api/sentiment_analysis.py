from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.schemas import (
    TextDataCreate, TextDataResponse,
    SentimentRequest, SentimentResponse,
    BatchSentimentRequest, BatchSentimentResponse
)
from app.services.repositories import TextDataRepository, SentimentAnalysisRepository
from app.services.sentiment_analyzer_new import SentimentAnalyzer

router = APIRouter()
sentiment_analyzer = SentimentAnalyzer()


@router.post("/analyze", response_model=SentimentResponse)
def analyze_sentiment(request: SentimentRequest, use_openai: bool = False, db: Session = Depends(get_db)):
    """
    Analyse le sentiment d'un texte fourni.
    
    - **text**: Le texte à analyser
    - **use_openai**: (Optionnel) Utiliser l'API OpenAI pour l'analyse (défaut: False)
    
    Renvoie les résultats de l'analyse de sentiment incluant la polarité et la subjectivité.
    """
    # Analyser le sentiment
    sentiment_result = sentiment_analyzer.analyze_sentiment(request.text, use_openai=use_openai)
    
    # Enregistrer le texte dans la base de données
    text_data = TextDataRepository.create(db, TextDataCreate(text=request.text))
    
    # Créer la réponse
    response = SentimentResponse(
        text=request.text,
        polarity=sentiment_result["polarity"],
        subjectivity=sentiment_result["subjectivity"],
        sentiment=sentiment_result["sentiment"],
        model=sentiment_result.get("model", "local")
    )
    
    return response


@router.post("/analyze/batch", response_model=BatchSentimentResponse)
def analyze_sentiment_batch(request: BatchSentimentRequest, use_openai: bool = False, db: Session = Depends(get_db)):
    """
    Analyse le sentiment d'un lot de textes.
    
    - **texts**: Liste de textes à analyser
    - **use_openai**: (Optionnel) Utiliser l'API OpenAI pour l'analyse (défaut: False)
    
    Renvoie les résultats de l'analyse pour chaque texte et des visualisations.
    """
    # Analyser les sentiments
    sentiment_results = []
    
    for text in request.texts:
        sentiment_result = sentiment_analyzer.analyze_sentiment(text, use_openai=use_openai)
        
        # Enregistrer le texte dans la base de données
        text_data = TextDataRepository.create(db, TextDataCreate(text=text))
        
        # Créer la réponse pour ce texte
        result = SentimentResponse(
            text=text,
            polarity=sentiment_result["polarity"],
            subjectivity=sentiment_result["subjectivity"],
            sentiment=sentiment_result["sentiment"],
            model=sentiment_result.get("model", "local")
        )
        
        sentiment_results.append(result)
    
    # Créer des visualisations
    visualization_urls = sentiment_analyzer.create_sentiment_visualization([text for text in request.texts])
    
    # Créer la réponse complète
    response = BatchSentimentResponse(
        results=sentiment_results,
        visualization_urls=visualization_urls
    )
    
    return response


@router.get("/texts", response_model=List[TextDataResponse])
def get_texts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Récupère tous les textes stockés dans la base de données.
    
    - **skip**: Nombre d'entrées à sauter (pagination)
    - **limit**: Nombre maximum d'entrées à renvoyer (pagination)
    
    Renvoie une liste de textes avec leurs métadonnées.
    """
    texts = TextDataRepository.get_all(db, skip=skip, limit=limit)
    return texts
