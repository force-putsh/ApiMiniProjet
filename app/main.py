from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

from app.api import sentiment_analysis
from app.models.database import init_db
from app.config import active_config
from app.services.sentiment_analyzer import download_nltk_resources

# Initialiser l'application FastAPI
app = FastAPI(
    title=active_config.PROJECT_NAME,
    description=active_config.DESCRIPTION,
    version=active_config.VERSION
)

# Monter les fichiers statiques
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurer les templates
templates = Jinja2Templates(directory="app/templates")


# Event de démarrage
@app.on_event("startup")
async def startup_event():
    # Initialiser la base de données
    init_db()
    
    # Télécharger les ressources NLTK nécessaires
    download_nltk_resources()


# Route racine (page d'accueil)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Inclure les routes de l'API
app.include_router(
    sentiment_analysis.router, 
    prefix=active_config.API_PREFIX,
    tags=["sentiment-analysis"]
)


if __name__ == "__main__":
    # Création du répertoire static/images s'il n'existe pas
    os.makedirs("app/static/images", exist_ok=True)
    
    # Démarrer l'application avec uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
