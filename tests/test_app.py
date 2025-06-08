import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.batch.scraper import TotoScraper
from app.batch.predictor import TotoPredictor

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'toto' in response.data

def test_scraper_initialization():
    scraper = TotoScraper()
    assert scraper.retry_count == 3
    assert scraper.retry_delay == 10

def test_predictor_initialization():
    predictor = TotoPredictor()
    assert predictor.home_advantage == 5
    assert predictor.recent_matches_weight == 0.4

def test_dummy_match_generation():
    scraper = TotoScraper()
    matches = scraper._generate_dummy_matches()
    assert len(matches) == 13
    assert all('home_team' in match and 'away_team' in match for match in matches)

def test_team_score_calculation():
    predictor = TotoPredictor()
    
    dummy_stats = {
        'recent_matches': [
            {'result': 'W', 'goals_for': 2, 'goals_against': 1},
            {'result': 'W', 'goals_for': 3, 'goals_against': 0},
            {'result': 'D', 'goals_for': 1, 'goals_against': 1},
            {'result': 'L', 'goals_for': 0, 'goals_against': 2},
            {'result': 'W', 'goals_for': 2, 'goals_against': 0}
        ],
        'ranking': 5,
        'home_stats': {'wins': 6, 'draws': 2, 'losses': 2},
        'away_stats': {'wins': 3, 'draws': 3, 'losses': 4}
    }
    
    home_score = predictor._calculate_team_score(dummy_stats, is_home=True)
    away_score = predictor._calculate_team_score(dummy_stats, is_home=False)
    
    assert home_score > away_score
    assert home_score > 50
    assert away_score > 0

def test_prediction_logic():
    predictor = TotoPredictor()
    
    toto_info = {
        'matches': [
            {'match_number': 1, 'home_team': '浦和レッズ', 'away_team': '鹿島アントラーズ'}
        ]
    }
    
    team_data = {
        '浦和レッズ': {
            'recent_matches': [{'result': 'W', 'goals_for': 2, 'goals_against': 1}] * 5,
            'ranking': 3,
            'home_stats': {'wins': 8, 'draws': 2, 'losses': 0}
        },
        '鹿島アントラーズ': {
            'recent_matches': [{'result': 'L', 'goals_for': 0, 'goals_against': 2}] * 5,
            'ranking': 15,
            'away_stats': {'wins': 2, 'draws': 3, 'losses': 5}
        }
    }
    
    predictions = predictor.predict_matches(toto_info, team_data)
    
    assert len(predictions) == 1
    assert predictions[0]['prediction'] in ['1', '0', '2']
    assert 'home_team' in predictions[0]
    assert 'away_team' in predictions[0]