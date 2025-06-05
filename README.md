# API d'Analyse de Sentiments

Ce projet est une API d'analyse de sentiments qui utilise TextBlob, NLTK et OpenAI pour analyser le sentiment des textes, principalement en français.

## Fonctionnalités

- Analyse de sentiment via différentes approches :
  - Analyse locale avec TextBlob et NLTK
  - Analyse avancée avec OpenAI (GPT)
- Support spécial pour le français avec détection de négations
- Visualisations des résultats d'analyse
- Stockage des analyses dans une base de données SQLite

## Installation

1. Clonez le dépôt
2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Configuration (optionnelle) - Modifiez le fichier `.env` :

```
# Base de données SQLite
DATABASE_URL=sqlite:///./sentiment_analysis.db

# Configuration OpenAI
OPENAI_API_KEY=votre-cle-api-openai
OPENAI_MODEL=gpt-3.5-turbo
USE_OPENAI=true  # false par défaut, mettre à true pour activer OpenAI par défaut
USE_OPENAI=true
```

## Utilisation

### Démarrer le serveur

```bash
python run.py
```

Le serveur démarrera à l'adresse http://127.0.0.1:8000

### Documentation de l'API

Une fois le serveur démarré, vous pouvez consulter la documentation interactive de l'API à l'adresse :
http://127.0.0.1:8000/docs

### Exemples d'utilisation

#### Analyse de texte unique

```python
import requests
import json

url = "http://127.0.0.1:8000/api/analyze"
payload = {
    "text": "Ce produit est vraiment excellent !"
}
# Pour utiliser OpenAI : ajoutez "?use_openai=true" à l'URL
response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=4))
```

#### Analyse par lots

```python
import requests
import json

url = "http://127.0.0.1:8000/api/analyze/batch"
payload = {
    "texts": [
        "Ce produit est vraiment excellent !",
        "Le service client est horrible.",
        "Je suis satisfait de la qualité."
    ]
}
# Pour utiliser OpenAI : ajoutez "?use_openai=true" à l'URL
response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=4))
```

## Modèles d'Analyse de Sentiment

### Modèle Local

L'analyse locale utilise une combinaison de :
- TextBlob pour l'analyse de base
- Dictionnaires personnalisés de mots positifs et négatifs en français
- Détection de négations pour améliorer la précision

### Modèle OpenAI

L'analyse OpenAI utilise l'API GPT pour obtenir une analyse plus sophistiquée et contextuelle des sentiments.

Pour utiliser OpenAI :
1. Ajoutez votre clé API dans le fichier `.env`
2. Définissez `USE_OPENAI=true` pour l'activer par défaut, ou utilisez la case à cocher dans l'interface
3. Ajoutez le paramètre `?use_openai=true` lors des appels à l'API

#### Gestion des Erreurs OpenAI
- Si l'API OpenAI n'est pas disponible ou rencontre une erreur, l'analyse basculera automatiquement vers le modèle local
- Tous les problèmes avec l'API sont enregistrés dans les logs pour le débogage
2. Définissez `USE_OPENAI=true` dans le fichier `.env` ou utilisez le paramètre `use_openai=true` dans les requêtes API

## Licence

Ce projet est sous licence MIT.
