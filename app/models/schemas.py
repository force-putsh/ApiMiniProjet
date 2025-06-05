from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TextDataBase(BaseModel):
    """Schéma de base pour les données textuelles"""
    text: str = Field(..., description="Le texte à analyser", min_length=1)
    source: Optional[str] = Field(None, description="La source du texte")


class TextDataCreate(TextDataBase):
    """Schéma pour la création d'une nouvelle donnée textuelle"""
    pass


class TextDataInDB(TextDataBase):
    """Schéma pour une donnée textuelle stockée dans la base de données"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TextDataResponse(TextDataInDB):
    """Schéma pour la réponse d'une donnée textuelle"""
    pass


class SentimentAnalysisBase(BaseModel):
    """Schéma de base pour l'analyse de sentiments"""
    text_id: int = Field(..., description="ID du texte analysé")
    polarity: float = Field(..., description="La polarité du sentiment (-1 à 1)")
    subjectivity: float = Field(..., description="La subjectivité du sentiment (0 à 1)")


class SentimentAnalysisCreate(SentimentAnalysisBase):
    """Schéma pour la création d'une nouvelle analyse de sentiment"""
    pass


class SentimentAnalysisInDB(SentimentAnalysisBase):
    """Schéma pour une analyse de sentiment stockée dans la base de données"""
    id: int
    analyzed_at: datetime

    class Config:
        from_attributes = True


class SentimentAnalysisResponse(SentimentAnalysisInDB):
    """Schéma pour la réponse d'une analyse de sentiment"""
    sentiment: str = Field(..., description="Catégorie de sentiment (positif, négatif, neutre)")


class SentimentRequest(BaseModel):
    """Schéma pour une requête d'analyse de sentiment"""
    text: str = Field(..., description="Le texte à analyser", min_length=1)


class SentimentResponse(BaseModel):
    """Schéma pour la réponse d'une analyse de sentiment simple"""
    text: str
    polarity: float
    subjectivity: float
    sentiment: str
    model: Optional[str] = Field("local", description="Le modèle utilisé pour l'analyse (local ou nom du modèle OpenAI)")


class BatchSentimentRequest(BaseModel):
    """Schéma pour une requête d'analyse de sentiment par lot"""
    texts: List[str] = Field(..., description="Liste des textes à analyser", min_items=1)


class BatchSentimentResponse(BaseModel):
    """Schéma pour la réponse d'une analyse de sentiment par lot"""
    results: List[SentimentResponse]
    visualization_urls: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Schéma pour les réponses d'erreur"""
    detail: str
