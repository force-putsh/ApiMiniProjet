import unittest
from unittest.mock import patch, MagicMock
from app.services.sentiment_analyzer_new import SentimentAnalyzer
from app.config import Config

class TestOpenAIIntegration(unittest.TestCase):
    """Tests pour l'intégration OpenAI"""
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer()
        self.test_text = "Je suis très content de cette application!"
    
    def test_local_sentiment_analysis(self):
        """Test de l'analyse de sentiment locale"""
        result = self.analyzer.analyze_sentiment(self.test_text, use_openai=False)
        
        self.assertIsNotNone(result)
        self.assertIn('polarity', result)
        self.assertIn('subjectivity', result)
        self.assertIn('sentiment', result)
        self.assertEqual(result['model'], 'local')
        
        # Vérifier que le sentiment est correctement détecté
        self.assertEqual(result['sentiment'], 'positif')
        
    @patch('app.services.sentiment_analyzer_new.OpenAI')
    def test_openai_sentiment_analysis(self, mock_openai):
        """Test de l'analyse de sentiment via OpenAI avec mock"""
        # Configuration du mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"sentiment": "positif", "polarity": 0.8}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test avec OpenAI activé
        result = self.analyzer.analyze_sentiment(self.test_text, use_openai=True)
        
        # Vérifier que le mock a été appelé correctement
        mock_client.chat.completions.create.assert_called_once()
        
        # Vérifier les résultats
        self.assertIsNotNone(result)
        self.assertEqual(result['sentiment'], 'positif')
        self.assertAlmostEqual(result['polarity'], 0.8)
        self.assertEqual(result['model'], Config.OPENAI_MODEL)
        
    def test_openai_fallback_to_local(self):
        """Test que l'analyse retombe sur la méthode locale si OpenAI échoue"""
        # Test avec une clé API non valide
        with patch.object(Config, 'OPENAI_API_KEY', ''):
            result = self.analyzer.analyze_sentiment(self.test_text, use_openai=True)
            
            # Vérifier que l'analyse a été effectuée localement
            self.assertIsNotNone(result)
            self.assertEqual(result['model'], 'local')
            
if __name__ == '__main__':
    unittest.main()
