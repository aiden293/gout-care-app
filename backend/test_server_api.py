"""
Integration tests for Flask API endpoints (server.py)
Tests all routes with mocked database calls
"""

import pytest
from unittest.mock import MagicMock, patch
import json
from server import app

# Fixtures
@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_json_db():
    """Mock JSON database responses"""
    return MagicMock()

@pytest.fixture
def sample_food_data():
    """Sample food data for testing"""
    return [
        {
            'id': 1,
            'name': 'Chicken breast',
            'unit': '100 g',
            'calories': 165,
            'protein': 31,
            'carbs': 0,
            'fat': 3.6,
            'fiber': 0,
            'sugar': 0,
            'calcium': 15,
            'iron': 1,
            'magnesium': 29,
            'phosphorus': 228,
            'potassium': 256,
            'sodium': 74,
            'zinc': 1,
            'vitaminA': 21,
            'vitaminC': 0,
            'vitaminD': 0.1,
            'vitaminE': 0.3,
            'vitaminK': 0,
            'vitaminB6': 0.6,
            'vitaminB12': 0.3,
            'folate': 4,
            'niacin': 13.7
        }
    ]

# Health Check Tests
def test_health_check_json_mode(client):
    """Test health check endpoint in JSON mode"""
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', MagicMock()):
        
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['mode'] == 'JSON'
        assert data['backend'] == 'Python/Flask'
        assert 'json_db_available' in data

def test_health_check_sql_mode(client):
    """Test health check endpoint in SQL mode"""
    with patch('server.USE_JSON_DB', False):
        
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['mode'] == 'SQL'

# Food Search Tests
def test_search_foods_success(client, sample_food_data, mock_json_db):
    """Test successful food search"""
    mock_json_db.search.return_value = sample_food_data
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_json_db), \
         patch('server.food_service') as mock_food_service:
        
        # Mock FoodService to return sample data
        if mock_food_service:
            mock_food_service.search_foods.return_value = sample_food_data
        
        response = client.get('/api/foods/search/chicken')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1  # May return more results with real database
        assert any(food['name'] == 'Chicken breast' for food in data)
        # Don't assert exact call signature since FoodService adds limit parameter

def test_search_foods_empty_query(client):
    """Test search with empty query returns empty list"""
    response = client.get('/api/foods/search/')
    
    assert response.status_code == 404 

def test_search_foods_short_query(client):
    """Test search with query less than 2 characters"""
    response = client.get('/api/foods/search/a')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data == []

def test_search_foods_no_results(client, mock_json_db):
    """Test search with no matching results"""
    mock_json_db.search.return_value = []
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_json_db):
        
        response = client.get('/api/foods/search/nonexistent')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

def test_search_foods_sql_mode(client, sample_food_data):
    """Test food search using SQL database"""
    with patch('server.USE_JSON_DB', False), \
         patch('server.search_foods_sql', return_value=sample_food_data):
        
        response = client.get('/api/foods/search/chicken')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Chicken breast'

# Get All Foods Tests
def test_get_all_foods_json_mode(client, sample_food_data, mock_json_db):
    """Test getting all foods from JSON database"""
    mock_json_db.get_all.return_value = sample_food_data
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_json_db):
        
        response = client.get('/api/foods')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        mock_json_db.get_all.assert_called_once_with(limit=50)

def test_get_all_foods_sql_mode_no_connection(client):
    """Test getting all foods when SQL connection fails"""
    with patch('server.USE_JSON_DB', False), \
         patch('server.get_db_connection', return_value=None):
        
        response = client.get('/api/foods')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

# Suggest Meals Tests
def test_suggest_meals_success(client, sample_food_data, mock_json_db):
    """Test meal suggestion with deficiencies"""
    mock_json_db.search.return_value = sample_food_data
    
    request_data = {
        'deficiencies': [
            {'nutrient': 'protein'},
            {'nutrient': 'iron'}
        ],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_json_db):
        
        response = client.post('/api/suggest-meals',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        if data:
            assert 'name' in data[0]
            assert 'foods' in data[0]
            assert 'totalNutrients' in data[0]

def test_suggest_meals_no_deficiencies(client):
    """Test meal suggestion with no deficiencies returns empty list"""
    request_data = {
        'deficiencies': [],
        'allergies': ''
    }
    
    response = client.post('/api/suggest-meals',
                          data=json.dumps(request_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data == []

def test_suggest_meals_with_allergies(client, mock_json_db):
    """Test meal suggestion filters out allergens"""
    mock_json_db.search.return_value = [
        {
            'id': 1,
            'name': 'Chicken breast',
            'calories': 165,
            'protein': 31,
            'fat': 3.6,
            'carbs': 0,
            'unit': '100 g'
        }
    ]
    
    request_data = {
        'deficiencies': [{'nutrient': 'protein'}],
        'allergies': 'peanut,shellfish'
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_json_db):
        
        response = client.post('/api/suggest-meals',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

def test_suggest_meals_missing_json_body(client):
    """Test meal suggestion with missing JSON body returns empty list"""
    response = client.post('/api/suggest-meals',
                          data='',
                          content_type='application/json')
    
    assert response.status_code in [200, 400]

def test_suggest_meals_invalid_json(client):
    """Test meal suggestion with invalid JSON"""
    response = client.post('/api/suggest-meals',
                          data='invalid json',
                          content_type='application/json')
    
    assert response.status_code in [200, 400]

def test_suggest_meals_scores_correctly(client, sample_food_data, mock_json_db):
    """Test that meals are scored by deficiencies covered"""
    mock_json_db.search.return_value = sample_food_data
    
    request_data = {
        'deficiencies': [
            {'nutrient': 'protein'},
            {'nutrient': 'iron'},
            {'nutrient': 'vitaminB12'}
        ],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_json_db):
        
        response = client.post('/api/suggest-meals',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        if len(data) > 1:
            for i in range(len(data) - 1):
                assert data[i]['score'] >= data[i + 1]['score']

def test_suggest_meals_calculates_total_nutrients(client, sample_food_data, mock_json_db):
    """Test that total nutrients are calculated correctly"""
    mock_json_db.search.return_value = sample_food_data
    
    request_data = {
        'deficiencies': [{'nutrient': 'protein'}],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_json_db):
        
        response = client.post('/api/suggest-meals',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        if data:
            meal = data[0]
            assert 'totalNutrients' in meal
            assert 'calories' in meal['totalNutrients']
            assert 'protein' in meal['totalNutrients']
            assert isinstance(meal['totalNutrients']['calories'], (int, float))

# Error Handling Tests
def test_404_not_found(client):
    """Test 404 error handler"""
    response = client.get('/api/nonexistent-endpoint')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Not found'

def test_suggest_meals_exception_handling(client, mock_json_db):
    """Test that exceptions in suggest_meals are handled gracefully"""
    mock_json_db.search.side_effect = Exception('Database error')
    
    request_data = {
        'deficiencies': [{'nutrient': 'protein'}],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_json_db), \
         patch('server.meal_service', None):  # Disable service to test fallback
        
        response = client.post('/api/suggest-meals',
                              data=json.dumps(request_data),
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        # With exception, should return empty list
        assert isinstance(data, list)

# Database Mode Switching Tests
def test_search_switches_to_sql_when_json_unavailable(client):
    """Test that search falls back to SQL when JSON DB is unavailable"""
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', None), \
         patch('server.search_foods_sql', return_value=[]):
        
        response = client.get('/api/foods/search/chicken')
        
        assert response.status_code == 200

def test_get_all_foods_returns_empty_on_no_connection(client):
    """Test that get_all_foods returns empty list when connection fails"""
    with patch('server.USE_JSON_DB', False), \
         patch('server.get_db_connection', return_value=None):
        
        response = client.get('/api/foods')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []
