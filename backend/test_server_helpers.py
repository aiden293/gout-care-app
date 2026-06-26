"""
Additional tests for server.py helper functions and SQL paths
"""

import pytest
from unittest.mock import MagicMock, patch
from server import get_db_connection, safe_float, search_foods_sql, app
import mysql.connector

# Helper Function Tests
def test_get_db_connection_success():
    """Test successful database connection"""
    mock_connection = MagicMock()
    
    with patch('mysql.connector.connect', return_value=mock_connection):
        result = get_db_connection()
        assert result == mock_connection

def test_get_db_connection_failure():
    """Test database connection failure"""
    with patch('mysql.connector.connect', side_effect=mysql.connector.Error("Connection failed")):
        result = get_db_connection()
        assert result is None

def test_safe_float_with_valid_number():
    """Test safe_float with valid number"""
    assert safe_float(42) == 42.0
    assert safe_float(3.14) == 3.14
    assert safe_float("123.45") == 123.45

def test_safe_float_with_none():
    """Test safe_float with None returns default"""
    assert safe_float(None) == 0.0
    assert safe_float(None, default=10.0) == 10.0

def test_safe_float_with_invalid_value():
    """Test safe_float with invalid value returns default"""
    assert safe_float("invalid") == 0.0
    assert safe_float("invalid", default=5.0) == 5.0
    assert safe_float([1, 2, 3]) == 0.0

def test_safe_float_with_empty_string():
    """Test safe_float with empty string"""
    assert safe_float("") == 0.0


# SQL Search Tests
def test_search_foods_sql_success():
    """Test SQL food search with successful results"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.is_connected.return_value = True
    
    mock_results = [
        {
            'id': 1,
            'name': 'Chicken breast',
            'unit': '100 g',
            'calories': 165.0,
            'protein': 31.0,
            'carbs': 0.0,
            'fat': 3.6,
            'fiber': None,
            'sugar': None,
            'calcium': 15.0,
            'iron': 1.0,
            'magnesium': 29.0,
            'phosphorus': 228.0,
            'potassium': 256.0,
            'sodium': 74.0,
            'zinc': 1.0,
            'vitaminA': 21.0,
            'vitaminC': 0.0,
            'vitaminD': 0.1,
            'vitaminE': 0.3,
            'vitaminK': 0.0,
            'vitaminB6': 0.6,
            'vitaminB12': 0.3,
            'folate': 4.0,
            'niacin': 13.7
        }
    ]
    
    mock_cursor.fetchall.return_value = mock_results
    
    with patch('server.get_db_connection', return_value=mock_connection):
        results = search_foods_sql('chicken')
        
        assert len(results) == 1
        assert results[0]['name'] == 'Chicken breast'
        assert results[0]['fiber'] == 0.0
        assert results[0]['sugar'] == 0.0
        mock_cursor.execute.assert_called_once()

def test_search_foods_sql_no_connection():
    """Test SQL search when connection fails"""
    with patch('server.get_db_connection', return_value=None):
        results = search_foods_sql('chicken')
        assert results == []

def test_search_foods_sql_query_error():
    """Test SQL search handles query errors"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.is_connected.return_value = True
    mock_cursor.execute.side_effect = mysql.connector.Error("Query error")
    
    with patch('server.get_db_connection', return_value=mock_connection):
        results = search_foods_sql('chicken')
        assert results == []

def test_search_foods_sql_closes_connection():
    """Test SQL search closes connection properly"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.is_connected.return_value = True
    mock_cursor.fetchall.return_value = []
    
    with patch('server.get_db_connection', return_value=mock_connection):
        search_foods_sql('test')
        
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()


# Flask Error Handler Tests
@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_500_error_handler_coverage():
    """Test 500 error handler is defined"""
    from server import app
    assert 500 in app.error_handler_spec[None]

def test_search_foods_endpoint_sql_mode(client):
    """Test search endpoint uses SQL when in SQL mode"""
    mock_results = [{'id': 1, 'name': 'Test Food', 'calories': 100}]
    
    with patch('server.USE_JSON_DB', False), \
         patch('server.search_foods_sql', return_value=mock_results):
        
        response = client.get('/api/foods/search/test')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1

# Get All Foods SQL Mode Tests
def test_get_all_foods_sql_success(client):
    """Test get all foods with SQL mode"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.is_connected.return_value = True
    
    mock_results = [
        {
            'id': 1,
            'name': 'Food 1',
            'unit': '100 g',
            'calories': 100,
            'protein': 10,
            'carbs': 20,
            'fat': 5,
            'fiber': None,
            'sugar': None,
            'calcium': None,
            'iron': None,
            'magnesium': None,
            'phosphorus': None,
            'potassium': None,
            'sodium': None,
            'zinc': None,
            'vitaminA': None,
            'vitaminC': None,
            'vitaminD': None,
            'vitaminE': None,
            'vitaminK': None,
            'vitaminB6': None,
            'vitaminB12': None,
            'folate': None,
            'niacin': None
        }
    ]
    
    mock_cursor.fetchall.return_value = mock_results
    
    with patch('server.USE_JSON_DB', False), \
         patch('server.json_db', None), \
         patch('server.get_db_connection', return_value=mock_connection):
        
        response = client.get('/api/foods')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Food 1'
        assert data[0]['fiber'] == 0.0
        assert data[0]['calcium'] == 0.0


# Suggest Meals SQL Mode Tests
def test_suggest_meals_sql_mode(client):
    """Test suggest meals using SQL mode for food search"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.is_connected.return_value = True
    
    mock_food = {
        'id': 1,
        'name': 'Spinach',
        'unit': '100 g',
        'calories': 23,
        'protein': 2.9,
        'carbs': 3.6,
        'fat': 0.4,
        'fiber': 2.2,
        'sugar': 0.4,
        'calcium': 99,
        'iron': 2.7,
        'magnesium': 79,
        'phosphorus': 49,
        'potassium': 558,
        'sodium': 79,
        'zinc': 0.5,
        'vitaminA': 469,
        'vitaminC': 28,
        'vitaminD': 0,
        'vitaminE': 2,
        'vitaminK': 483,
        'vitaminB6': 0.2,
        'vitaminB12': 0,
        'folate': 194,
        'niacin': 0.7
    }
    
    mock_cursor.fetchall.return_value = [mock_food]
    
    request_data = {
        'deficiencies': [
            {'nutrient': 'iron'},
            {'nutrient': 'vitaminK'}
        ],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', False), \
         patch('server.json_db', None), \
         patch('server.get_db_connection', return_value=mock_connection):
        
        response = client.post('/api/suggest-meals',
                              json=request_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


# Multiple Allergens Test
def test_suggest_meals_multiple_allergens(client):
    """Test meal suggestions with multiple allergens"""
    mock_db = MagicMock()
    mock_db.search.return_value = [
        {
            'id': 1,
            'name': 'Chicken breast',
            'calories': 165,
            'protein': 31,
            'iron': 1,
            'unit': '100 g'
        }
    ]
    
    request_data = {
        'deficiencies': [{'nutrient': 'protein'}],
        'allergies': 'peanut,shellfish,dairy'
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_db):
        
        response = client.post('/api/suggest-meals',
                              json=request_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


# Edge Cases for Suggest Meals
def test_suggest_meals_no_foods_found(client):
    """Test suggest meals when no foods are found in database"""
    mock_db = MagicMock()
    mock_db.search.return_value = []
    
    request_data = {
        'deficiencies': [{'nutrient': 'protein'}],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_db):
        
        response = client.post('/api/suggest-meals',
                              json=request_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

def test_suggest_meals_returns_top_8(client):
    """Test suggest meals returns max 8 results"""
    mock_db = MagicMock()
    mock_db.search.return_value = [
        {
            'id': i,
            'name': f'Food {i}',
            'calories': 100,
            'protein': 10,
            'iron': 5,
            'vitaminA': 100,
            'vitaminC': 50,
            'calcium': 80,
            'unit': '100 g'
        }
        for i in range(50)
    ]
    
    request_data = {
        'deficiencies': [
            {'nutrient': 'protein'},
            {'nutrient': 'iron'},
            {'nutrient': 'calcium'}
        ],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_db):
        
        response = client.post('/api/suggest-meals',
                              json=request_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) <= 8


# Safe Float in Suggest Meals Context
def test_suggest_meals_handles_none_nutrients(client):
    """Test suggest meals handles None nutrient values"""
    mock_db = MagicMock()
    mock_db.search.return_value = [
        {
            'id': 1,
            'name': 'Food with nulls',
            'calories': None,
            'protein': 10,
            'iron': None,
            'unit': '100 g'
        }
    ]
    
    request_data = {
        'deficiencies': [{'nutrient': 'protein'}],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_db):
        
        response = client.post('/api/suggest-meals',
                              json=request_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        if data:
            for meal in data:
                if 'totalNutrients' in meal:
                    assert isinstance(meal['totalNutrients']['calories'], (int, float))


# Module Initialization Coverage
def test_module_constants_defined():
    """Test that module constants are properly defined"""
    from server import PORT, USE_JSON_DB, MYSQL_CONFIG, MEAL_TEMPLATES
    
    assert isinstance(PORT, int)
    assert isinstance(USE_JSON_DB, bool)
    assert isinstance(MYSQL_CONFIG, dict)
    assert isinstance(MEAL_TEMPLATES, list)
    assert len(MEAL_TEMPLATES) > 0

def test_meal_templates_structure():
    """Test meal templates have correct structure"""
    from server import MEAL_TEMPLATES
    from models.meal_template import MealTemplate
    
    for template in MEAL_TEMPLATES:
        # Templates are now MealTemplate objects, convert to dict for testing
        if isinstance(template, MealTemplate):
            template_dict = template.to_dict()
        else:
            template_dict = template
            
        assert 'id' in template_dict
        assert 'name' in template_dict
        assert 'category' in template_dict
        assert 'foods' in template_dict
        assert 'nutrients' in template_dict
        assert isinstance(template_dict['foods'], list)
        assert isinstance(template_dict['nutrients'], list)

def test_search_foods_json_function():
    """Test search_foods_json helper function"""
    from server import search_foods_json
    
    mock_db = MagicMock()
    mock_db.search.return_value = [{'id': 1, 'name': 'Test'}]
    
    with patch('server.json_db', mock_db):
        result = search_foods_json('test')
        assert len(result) == 1
        mock_db.search.assert_called_once_with('test')

def test_search_foods_json_no_db():
    """Test search_foods_json when db is None"""
    from server import search_foods_json
    
    with patch('server.json_db', None):
        result = search_foods_json('test')
        assert result == []


# Additional Coverage for Missing Lines
def test_suggest_meals_food_with_missing_nutrients(client):
    """Test suggest meals when food has missing nutrient keys"""
    mock_db = MagicMock()
    mock_db.search.return_value = [
        {
            'id': 1,
            'name': 'Incomplete food data',
            'protein': 10,
            'unit': '100 g'
        }
    ]
    
    request_data = {
        'deficiencies': [{'nutrient': 'protein'}],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_db):
        
        response = client.post('/api/suggest-meals',
                              json=request_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        if data and data[0].get('foods'):
            assert 'nutrients' in data[0]['foods'][0]

def test_suggest_meals_all_nutrients_computed(client):
    """Test that suggest meals computes all 22 nutrients"""
    mock_db = MagicMock()
    mock_db.search.return_value = [
        {
            'id': 1,
            'name': 'Complete food',
            'unit': '100 g',
            'calories': 100, 'protein': 10, 'carbs': 20, 'fat': 5,
            'fiber': 3, 'sugar': 2, 'calcium': 50, 'iron': 2,
            'magnesium': 30, 'phosphorus': 40, 'potassium': 200,
            'sodium': 100, 'zinc': 1, 'vitaminA': 500, 'vitaminC': 60,
            'vitaminD': 5, 'vitaminE': 10, 'vitaminK': 80,
            'vitaminB6': 1.5, 'vitaminB12': 2.5, 'folate': 100, 'niacin': 15
        }
    ]
    
    request_data = {
        'deficiencies': [{'nutrient': 'protein'}],
        'allergies': ''
    }
    
    with patch('server.USE_JSON_DB', True), \
         patch('server.json_db', mock_db):
        
        response = client.post('/api/suggest-meals',
                              json=request_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        if data:
            nutrients = data[0]['totalNutrients']
            expected_nutrients = [
                'calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar',
                'calcium', 'iron', 'magnesium', 'phosphorus', 'potassium',
                'sodium', 'zinc', 'vitaminA', 'vitaminC', 'vitaminD',
                'vitaminE', 'vitaminK', 'vitaminB6', 'vitaminB12',
                'folate', 'niacin'
            ]
            for nutrient in expected_nutrients:
                assert nutrient in nutrients
