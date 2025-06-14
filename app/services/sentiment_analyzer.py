from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
import re
import logging
import matplotlib.pyplot as plt
import os
import pandas as pd
import json
from openai import OpenAI
from app.config import Config

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionnaire de mots positifs et négatifs en français
POSITIFS_FR = {
    'bon', 'super', 'excellent', 'génial', 'parfait', 'incroyable', 'merveilleux', 'magnifique', 'extraordinaire',
    'content', 'heureux', 'joyeux', 'ravi', 'enchanté', 'satisfait', 'aimer', 'adorer', 'apprécier',
    'bravo', 'félicitations', 'impressionnant', 'réussi', 'succès', 'victoire', 'gain', 'avantage',
    'facile', 'pratique', 'utile', 'efficace', 'rapide', 'fiable', 'agréable', 'confortable',
    'sécurisé', 'stable', 'solide', 'durable', 'brillant', 'intelligent', 'sympa', 'cool',
    'correctement', 'fonctionne', 'bien', 'réussir', 'fonctionnel', 'fonctionnalité'
}

NEGATIFS_FR = {
    'mauvais', 'horrible', 'terrible', 'affreux', 'nul', 'médiocre', 'pire', 'catastrophique',
    'triste', 'malheureux', 'déçu', 'mécontent', 'frustré', 'énervé', 'fâché', 'en colère',
    'détester', 'haïr', 'déplorer', 'rejeter', 'critiquer', 'condamner', 'reprocher',
    'difficile', 'compliqué', 'pénible', 'ennuyeux', 'inefficace', 'inutile', 'insuffisant',
    'dangereux', 'instable', 'défectueux', 'cassé', 'problème', 'erreur', 'bug', 'panne',
    'échec', 'défaite', 'perte', 'désavantage', 'cher', 'coûteux', 'excessif', 'trop',
    'ne fonctionne pas', 'ne marche pas', 'impossible', 'non fonctionnel', 'pas correctement', 'défaillant',
    'pas bien', 'pas bon', 'pas pratique', 'pas utile', 'pas efficace', 'pas fiable'
}

# Mots servant à la négation en français
NEGATIONS_FR = {'ne', 'pas', 'plus', 'jamais', 'aucun', 'aucune', 'ni', 'sans'}

# S'assurer que les ressources NLTK nécessaires sont téléchargées
def download_nltk_resources():
    """Télécharge les ressources NLTK nécessaires"""
    try:
        resources = ['punkt', 'stopwords']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
                logger.info(f"Ressource NLTK '{resource}' déjà téléchargée.")
            except LookupError:
                logger.info(f"Téléchargement de la ressource NLTK '{resource}'...")
                nltk.download(resource)
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement des ressources NLTK: {e}")


class SentimentAnalyzer:
    """Service pour analyser les sentiments dans les textes"""
    
    def __init__(self):
        # S'assurer que les ressources NLTK sont disponibles
        download_nltk_resources()
        try:
            self.stopwords = set(stopwords.words('french') + stopwords.words('english'))
        except:
            logger.warning("Impossibilité de charger les stopwords, utilisation d'un ensemble vide")
            self.stopwords = set()
    
    def preprocess_text(self, text):
        """Prétraite le texte avant l'analyse"""
        if not text:
            return ""
        
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer les URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Supprimer les mentions et hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Supprimer les caractères non alphanumériques
        text = re.sub(r'[^\w\s]', '', text)
        
        # Supprimer les chiffres
        text = re.sub(r'\d+', '', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text):
        """Supprime les mots vides du texte"""
        if not text:
            return ""
        
        words = text.split()
        filtered_words = [word for word in words if word not in self.stopwords]
        return ' '.join(filtered_words)
    
    def analyze_sentiment_fr(self, text):
        """Analyse le sentiment en français en tenant compte des négations"""
        if not text:
            return 0
            
        # Tokenisation basique
        words = text.lower().split()
        
        # Détection de séquences de mots incluant les négations
        phrases = []
        for i in range(len(words)):
            # Ajouter des phrases de 2 à 4 mots à partir de la position actuelle
            for j in range(2, min(5, len(words) - i + 1)):
                phrases.append(" ".join(words[i:i+j]))
        
        # Compter les mots positifs et négatifs
        positifs = sum(1 for word in words if word in POSITIFS_FR)
        negatifs = sum(1 for word in words if word in NEGATIFS_FR)
        
        # Vérifier les phrases négatives spécifiques
        for phrase in phrases:
            if phrase in NEGATIFS_FR:
                negatifs += 1
        
        # Détecter les expressions négatives (ex: "ne fonctionne pas")
        has_negation = any(neg in words for neg in NEGATIONS_FR)
        if has_negation:
            # Chercher des mots positifs qui pourraient être inversés par la négation
            negated_positives = sum(1 for word in words if word in POSITIFS_FR)
            if negated_positives > 0:
                # Convertir les mots positifs en négatifs s'ils sont niés
                positifs -= negated_positives
                negatifs += negated_positives
                
        # Calculer un score basé sur les mots français
        if positifs > 0 or negatifs > 0:
            return (positifs - negatifs) / (positifs + negatifs)
        return 0
        
    def analyze_sentiment_openai(self, text):
        """Analyse le sentiment du texte en utilisant l'API OpenAI"""
        if not Config.OPENAI_API_KEY:
            logger.warning("Clé API OpenAI manquante")
            return None
        
        try:
            # Créer un client OpenAI
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            
            # Construire le prompt pour l'analyse de sentiment
            prompt = [
                {"role": "system", "content": "Vous êtes un expert en analyse de sentiment. Analysez le sentiment du texte et répondez uniquement avec un objet JSON contenant 'sentiment' (positif, négatif ou neutre) et 'polarity' (valeur entre -1 et 1)."},
                {"role": "user", "content": f"Texte à analyser: {text}"}
            ]
            
            # Appeler l'API OpenAI
            response = client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=prompt,
                temperature=0,
                max_tokens=100
            )
            
            # Extraire la réponse
            content = response.choices[0].message.content
            
            # Convertir la réponse JSON en dictionnaire Python
            try:
                result = json.loads(content)
                # Standardiser les valeurs
                sentiment = result.get('sentiment', 'neutre').lower()
                polarity = float(result.get('polarity', 0))
                
                # Estimer la subjectivité en fonction de la polarité
                subjectivity = abs(polarity) * 0.8
                
                return {
                    "polarity": polarity,
                    "subjectivity": subjectivity,
                    "sentiment": sentiment,
                    "model": Config.OPENAI_MODEL
                }
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage de la réponse JSON: {content}")
                return None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse avec OpenAI: {e}")
            return None

    def analyze_sentiment(self, text, use_openai=None):
        """Analyse le sentiment du texte en combinant TextBlob et une approche basée sur les mots clés"""
        # Déterminer si on utilise OpenAI
        if use_openai is None:
            use_openai = Config.USE_OPENAI
        
        # Si OpenAI est activé, tenter l'analyse avec OpenAI d'abord
        if use_openai:
            openai_result = self.analyze_sentiment_openai(text)
            if openai_result:
                return openai_result
        
        # Prétraitement du texte mais conserve le texte original pour l'analyse des négations
        original_text = text.lower()
        preprocessed_text = self.preprocess_text(text)
        clean_text = self.remove_stopwords(preprocessed_text)
        
        # Si le texte est vide après prétraitement, retourner des valeurs neutres
        if not clean_text:
            return {"polarity": 0.0, "subjectivity": 0.0, "sentiment": "neutre", "model": "local"}
        
        # Analyse avec TextBlob (principalement pour l'anglais)
        blob = TextBlob(clean_text)
        polarity_en = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Analyse avec notre approche pour le français
        polarity_fr = self.analyze_sentiment_fr(original_text)
        
        # Détection spécifique de négations
        has_negation_words = any(neg in original_text.split() for neg in NEGATIONS_FR)
        # Vérification explicite des expressions comme "ne fonctionne pas"
        explicit_negative = "ne fonctionne pas" in original_text or "pas correctement" in original_text
        
        # Pondération: donner plus d'importance à l'analyse française et aux négations détectées
        if explicit_negative or (has_negation_words and polarity_fr <= 0):
            polarity = -0.5  # Force un sentiment négatif pour les négations explicites
        else:
            # Combiner les scores (avec plus de poids pour l'approche française)
            polarity = (polarity_en + 3 * polarity_fr) / 4
        
        # Définir le sentiment en fonction de la polarité avec des seuils adaptés
        if polarity > 0.05:
            sentiment = "positif"
        elif polarity < -0.03:  # Seuil réduit pour détecter plus facilement les sentiments négatifs
            sentiment = "négatif"
        else:
            sentiment = "neutre"
        
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentiment": sentiment,
            "model": "local"
        }
    
    def create_sentiment_visualization(self, texts, output_dir="app/static/images"):
        """Crée des visualisations de l'analyse de sentiment"""
        if not texts:
            logger.warning("Aucun texte fourni pour la visualisation")
            return None
        
        # Analyser tous les textes
        results = [self.analyze_sentiment(text) for text in texts]
        
        # Créer un DataFrame pour faciliter la manipulation des données
        df = pd.DataFrame({
            'polarity': [r['polarity'] for r in results],
            'subjectivity': [r['subjectivity'] for r in results],
            'sentiment': [r['sentiment'] for r in results]
        })
        
        # S'assurer que le répertoire de sortie existe
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Distribution des polarités
        plt.figure(figsize=(10, 6))
        plt.hist(df['polarity'], bins=20, color='skyblue', edgecolor='black')
        plt.title('Distribution des polarités')
        plt.xlabel('Polarité')
        plt.ylabel('Fréquence')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, 'polarity_distribution.png'))
        
        # 2. Distribution des subjectivités
        plt.figure(figsize=(10, 6))
        plt.hist(df['subjectivity'], bins=20, color='lightgreen', edgecolor='black')
        plt.title('Distribution des subjectivités')
        plt.xlabel('Subjectivité')
        plt.ylabel('Fréquence')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, 'subjectivity_distribution.png'))
        
        # 3. Graphique de dispersion polarité vs subjectivité
        plt.figure(figsize=(10, 6))
        colors = {'positif': 'green', 'neutre': 'blue', 'négatif': 'red'}
        for sentiment in df['sentiment'].unique():
            subset = df[df['sentiment'] == sentiment]
            plt.scatter(
                subset['polarity'],
                subset['subjectivity'],
                c=colors.get(sentiment, 'gray'),
                label=sentiment,
                alpha=0.6
            )
        plt.title('Polarité vs Subjectivité')
        plt.xlabel('Polarité')
        plt.ylabel('Subjectivité')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, 'polarity_vs_subjectivity.png'))
        
        # 4. Camembert des sentiments
        sentiment_counts = df['sentiment'].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(
            sentiment_counts,
            labels=sentiment_counts.index,
            autopct='%1.1f%%',
            colors=['green', 'blue', 'red'],
            startangle=90
        )
        plt.title('Répartition des sentiments')
        plt.savefig(os.path.join(output_dir, 'sentiment_pie.png'))
        
        plt.close('all')
        
        return {
            'polarity_distribution': os.path.join(output_dir, 'polarity_distribution.png'),
            'subjectivity_distribution': os.path.join(output_dir, 'subjectivity_distribution.png'),
            'polarity_vs_subjectivity': os.path.join(output_dir, 'polarity_vs_subjectivity.png'),
            'sentiment_pie': os.path.join(output_dir, 'sentiment_pie.png')
        }
