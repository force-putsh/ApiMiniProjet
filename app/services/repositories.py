from sqlalchemy.orm import Session
from app.models.database import TextData, SentimentAnalysis
from app.models.schemas import TextDataCreate, SentimentAnalysisCreate
from typing import List, Optional
import logging

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextDataRepository:
    """Repository pour gérer les opérations sur TextData"""

    @staticmethod
    def create(db: Session, text_data: TextDataCreate) -> TextData:
        """Crée une nouvelle entrée TextData"""
        db_text = TextData(text=text_data.text, source=text_data.source)
        db.add(db_text)
        db.commit()
        db.refresh(db_text)
        return db_text

    @staticmethod
    def get_by_id(db: Session, text_id: int) -> Optional[TextData]:
        """Récupère un TextData par son ID"""
        return db.query(TextData).filter(TextData.id == text_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[TextData]:
        """Récupère tous les TextData avec pagination"""
        return db.query(TextData).offset(skip).limit(limit).all()

    @staticmethod
    def delete(db: Session, text_id: int) -> bool:
        """Supprime un TextData par son ID"""
        db_text = db.query(TextData).filter(TextData.id == text_id).first()
        if db_text:
            db.delete(db_text)
            db.commit()
            return True
        return False


class SentimentAnalysisRepository:
    """Repository pour gérer les opérations sur SentimentAnalysis"""

    @staticmethod
    def create(db: Session, analysis: SentimentAnalysisCreate) -> SentimentAnalysis:
        """Crée une nouvelle entrée SentimentAnalysis"""
        db_analysis = SentimentAnalysis(
            text_id=analysis.text_id,
            polarity=analysis.polarity,
            subjectivity=analysis.subjectivity
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis

    @staticmethod
    def get_by_id(db: Session, analysis_id: int) -> Optional[SentimentAnalysis]:
        """Récupère un SentimentAnalysis par son ID"""
        return db.query(SentimentAnalysis).filter(SentimentAnalysis.id == analysis_id).first()

    @staticmethod
    def get_by_text_id(db: Session, text_id: int) -> List[SentimentAnalysis]:
        """Récupère tous les SentimentAnalysis liés à un TextData"""
        return db.query(SentimentAnalysis).filter(SentimentAnalysis.text_id == text_id).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[SentimentAnalysis]:
        """Récupère tous les SentimentAnalysis avec pagination"""
        return db.query(SentimentAnalysis).offset(skip).limit(limit).all()

    @staticmethod
    def delete(db: Session, analysis_id: int) -> bool:
        """Supprime un SentimentAnalysis par son ID"""
        db_analysis = db.query(SentimentAnalysis).filter(SentimentAnalysis.id == analysis_id).first()
        if db_analysis:
            db.delete(db_analysis)
            db.commit()
            return True
        return False
