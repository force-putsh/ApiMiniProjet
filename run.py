from app.main import app
import uvicorn

# Si ce fichier est exécuté directement, démarrer le serveur
if __name__ == "__main__":
    print("Démarrage du serveur FastAPI sur http://127.0.0.1:8000")
    print("Accédez à l'interface via votre navigateur")
    print("La documentation API est disponible sur http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
