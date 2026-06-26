"""
Comprehensive tests for json_db.py to increase coverage
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from json_db import JsonDatabase, NUTRIENT_CODE_MAP

# Test Data from db
@pytest.fixture
def sample_food_data():
    """Sample USDA food data"""
    return {
        "fdcId": 123456,
        "description": "Spinach, raw",
        "foodNutrients": [
            {"nutrientId": 208, "amount": 23}, 
            {"nutrientId": 203, "amount": 2.9},  
            {"nutrientId": 303, "amount": 2.7},  
            {"nutrientId": 306, "amount": 558}   
        ],
        "foodPortions": [
            {
                "label": "cup",
                "amount": 1.0,
                "gramWeight": 30.0,
                "modifier": "chopped",
                "portionDescription": "1 cup chopped"
            }
        ]
    }

@pytest.fixture
def sample_food_alternate_format():
    """Sample food with alternate field names"""
    return {
        "fdc_id": 789012,
        "name": "Banana",
        "foodNutrients": [
            {
                "nutrient": {"id": 208, "number": "208"},
                "value": 89
            },
            {
                "nutrient": {"id": 205, "number": "205"},
                "amount": 22.8
            }
        ]
    }

@pytest.fixture
def temp_json_file(sample_food_data):
    """Create temporary JSON file"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump([sample_food_data], f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)

# Initialization Tests
def test_init_with_list_format(temp_json_file):
    """Test initialization with list format JSON"""
    db = JsonDatabase(temp_json_file)
    assert len(db.foods) == 1
    assert db.foods[0]['description'] == "Spinach, raw"

def test_init_with_dict_foods_key(sample_food_data):
    """Test initialization with dict containing 'foods' key"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"foods": [sample_food_data]}, f)
        temp_path = f.name
    
    try:
        db = JsonDatabase(temp_path)
        assert len(db.foods) == 1
    finally:
        os.unlink(temp_path)

def test_init_with_foundation_foods_key(sample_food_data):
    """Test initialization with dict containing 'FoundationFoods' key"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"FoundationFoods": [sample_food_data]}, f)
        temp_path = f.name
    
    try:
        db = JsonDatabase(temp_path)
        assert len(db.foods) == 1
    finally:
        os.unlink(temp_path)

def test_init_with_empty_dict():
    """Test initialization with empty dict"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({}, f)
        temp_path = f.name
    
    try:
        db = JsonDatabase(temp_path)
        assert len(db.foods) == 0
    finally:
        os.unlink(temp_path)

def test_init_file_not_found():
    """Test initialization with non-existent file"""
    db = JsonDatabase('/nonexistent/path/to/file.json')
    assert len(db.foods) == 0

def test_init_invalid_json():
    """Test initialization with invalid JSON"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write("invalid json content {")
        temp_path = f.name
    
    try:
        db = JsonDatabase(temp_path)
        assert len(db.foods) == 0
    finally:
        os.unlink(temp_path)

def test_init_generic_exception():
    """Test initialization handles generic exceptions"""
    with patch('builtins.open', side_effect=PermissionError("Access denied")):
        db = JsonDatabase('some_file.json')
        assert len(db.foods) == 0


# Extract Nutrient Tests
def test_extract_nutrient_with_nutrient_id(sample_food_data):
    """Test extracting nutrient using nutrientId field"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    result = db._extract_nutrient(sample_food_data, 208)
    assert result == 23.0

def test_extract_nutrient_with_nested_id(sample_food_alternate_format):
    """Test extracting nutrient using nested nutrient.id"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    result = db._extract_nutrient(sample_food_alternate_format, 208)
    assert result == 89.0

def test_extract_nutrient_with_number_field(sample_food_alternate_format):
    """Test extracting nutrient using nutrient.number as string"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    result = db._extract_nutrient(sample_food_alternate_format, 205)
    assert result == 22.8

def test_extract_nutrient_with_value_field(sample_food_alternate_format):
    """Test extracting nutrient using value field instead of amount"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    result = db._extract_nutrient(sample_food_alternate_format, 208)
    assert result == 89.0

def test_extract_nutrient_not_found():
    """Test extracting non-existent nutrient returns 0"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    food = {"foodNutrients": [{"nutrientId": 208, "amount": 23}]}
    result = db._extract_nutrient(food, 999)
    assert result == 0.0

def test_extract_nutrient_null_amount():
    """Test extracting nutrient with null amount"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    food = {"foodNutrients": [{"nutrientId": 208, "amount": None}]}
    result = db._extract_nutrient(food, 208)
    assert result == 0.0

def test_extract_nutrient_invalid_number_field():
    """Test extracting nutrient with invalid number field"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    food = {
        "foodNutrients": [{
            "nutrient": {"number": "invalid"},
            "amount": 100
        }]
    }
    result = db._extract_nutrient(food, 208)
    assert result == 0.0


# Normalize Food Tests
def test_normalize_food_basic(temp_json_file, sample_food_data):
    """Test normalizing food with all fields"""
    db = JsonDatabase(temp_json_file)
    
    normalized = db._normalize_food(sample_food_data)
    
    assert normalized['id'] == 123456
    assert normalized['name'] == "Spinach, raw"
    assert normalized['unit'] == '100 g'
    assert normalized['calories'] == 23.0
    assert normalized['protein'] == 2.9
    assert normalized['iron'] == 2.7
    assert normalized['potassium'] == 558.0
    assert 'servingOptions' in normalized
    assert len(normalized['servingOptions']) >= 4 

def test_normalize_food_alternate_id_fields(sample_food_alternate_format):
    """Test normalizing food with alternate ID field names"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    normalized = db._normalize_food(sample_food_alternate_format)
    
    assert normalized['id'] == 789012
    assert normalized['name'] == "Banana"

def test_normalize_food_missing_id():
    """Test normalizing food with missing ID defaults to 0"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    food = {"description": "Test Food", "foodNutrients": []}
    normalized = db._normalize_food(food)
    
    assert normalized['id'] == 0

def test_normalize_food_missing_description():
    """Test normalizing food with missing description"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    food = {"fdcId": 123, "foodNutrients": []}
    normalized = db._normalize_food(food)
    
    assert normalized['name'] == 'Unknown Food'

def test_normalize_food_with_food_portions(sample_food_data):
    """Test normalizing food includes food portions"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    normalized = db._normalize_food(sample_food_data)
    
    serving_options = normalized['servingOptions']
    assert any('cup' in opt['label'].lower() for opt in serving_options)
    
    cup_option = next(opt for opt in serving_options if 'cup' in opt['label'].lower())
    assert cup_option['gramWeight'] == 30.0
    assert cup_option['gramsPerUnit'] == 30.0

def test_normalize_food_portion_with_non_one_amount():
    """Test normalizing food portion with amount != 1.0"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    food = {
        "fdcId": 123,
        "description": "Test",
        "foodNutrients": [],
        "foodPortions": [{
            "label": "cup",
            "amount": 2.5,
            "gramWeight": 75.0
        }]
    }
    
    normalized = db._normalize_food(food)
    cup_option = next(opt for opt in normalized['servingOptions'] if 'cup' in opt['label'].lower())
    
    assert '2.5' in cup_option['label']
    assert cup_option['gramsPerUnit'] == 30.0 

def test_normalize_food_portion_zero_amount():
    """Test normalizing food portion with zero amount"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    food = {
        "fdcId": 123,
        "description": "Test",
        "foodNutrients": [],
        "foodPortions": [{
            "amount": 0,
            "gramWeight": 100.0
        }]
    }
    
    normalized = db._normalize_food(food)
    assert len(normalized['servingOptions']) >= 4 

# Search Tests
def test_search_single_word(temp_json_file):
    """Test searching with single word"""
    db = JsonDatabase(temp_json_file)
    
    results = db.search('spinach')
    assert len(results) == 1
    assert 'Spinach' in results[0]['name']

def test_search_multiple_words(temp_json_file):
    """Test searching with multiple words"""
    db = JsonDatabase(temp_json_file)
    
    results = db.search('spinach raw')
    assert len(results) == 1

def test_search_case_insensitive(temp_json_file):
    """Test search is case insensitive"""
    db = JsonDatabase(temp_json_file)
    
    results = db.search('SPINACH')
    assert len(results) == 1

def test_search_empty_query(temp_json_file):
    """Test search with empty query returns empty list"""
    db = JsonDatabase(temp_json_file)
    
    results = db.search('')
    assert results == []

def test_search_no_results(temp_json_file):
    """Test search with no matching results"""
    db = JsonDatabase(temp_json_file)
    
    results = db.search('nonexistent food item xyz')
    assert results == []

def test_search_limit(sample_food_data):
    """Test search respects limit parameter"""
    # Create file with multiple foods
    foods = [sample_food_data.copy() for _ in range(10)]
    for i, food in enumerate(foods):
        food['fdcId'] = i
        food['description'] = f"Spinach variety {i}"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(foods, f)
        temp_path = f.name
    
    try:
        db = JsonDatabase(temp_path)
        results = db.search('spinach', limit=5)
        assert len(results) == 5
    finally:
        os.unlink(temp_path)

def test_search_partial_word_match(temp_json_file):
    """Test search matches partial words (substring matching)"""
    db = JsonDatabase(temp_json_file)
    
    results = db.search('spin')
    assert len(results) == 1 

# Get By ID Tests
def test_get_by_id_found(temp_json_file):
    """Test getting food by ID when it exists"""
    db = JsonDatabase(temp_json_file)
    
    food = db.get_by_id(123456)
    assert food is not None
    assert food['name'] == "Spinach, raw"

def test_get_by_id_not_found(temp_json_file):
    """Test getting food by ID when it doesn't exist"""
    db = JsonDatabase(temp_json_file)
    
    food = db.get_by_id(999999)
    assert food is None

def test_get_by_id_alternate_field_names(sample_food_alternate_format):
    """Test getting food by ID with alternate field names"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump([sample_food_alternate_format], f)
        temp_path = f.name
    
    try:
        db = JsonDatabase(temp_path)
        food = db.get_by_id(789012)
        assert food is not None
        assert food['name'] == "Banana"
    finally:
        os.unlink(temp_path)

# Get All Tests
def test_get_all_default_limit(sample_food_data):
    """Test getting all foods with default limit"""
    foods = [sample_food_data.copy() for _ in range(60)]
    for i, food in enumerate(foods):
        food['fdcId'] = i
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(foods, f)
        temp_path = f.name
    
    try:
        db = JsonDatabase(temp_path)
        results = db.get_all()
        assert len(results) == 50
    finally:
        os.unlink(temp_path)

def test_get_all_custom_limit(sample_food_data):
    """Test getting all foods with custom limit"""
    foods = [sample_food_data.copy() for _ in range(30)]
    for i, food in enumerate(foods):
        food['fdcId'] = i
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(foods, f)
        temp_path = f.name
    
    try:
        db = JsonDatabase(temp_path)
        results = db.get_all(limit=10)
        assert len(results) == 10
    finally:
        os.unlink(temp_path)

def test_get_all_fewer_than_limit(temp_json_file):
    """Test getting all foods when total is less than limit"""
    db = JsonDatabase(temp_json_file)
    
    results = db.get_all(limit=100)
    assert len(results) == 1


# Nutrient Code Map Test
def test_nutrient_code_map_completeness():
    """Test that all expected nutrients are in the map"""
    expected_nutrients = [
        'calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar',
        'calcium', 'iron', 'magnesium', 'phosphorus', 'potassium',
        'sodium', 'zinc', 'vitaminA', 'vitaminC', 'vitaminD',
        'vitaminE', 'vitaminK', 'vitaminB6', 'vitaminB12',
        'folate', 'niacin'
    ]
    
    for nutrient in expected_nutrients:
        assert nutrient in NUTRIENT_CODE_MAP.values()

def test_normalize_food_includes_all_nutrients(sample_food_data):
    """Test that normalized food includes all nutrients from map"""
    db = JsonDatabase.__new__(JsonDatabase)
    db.foods = []
    
    normalized = db._normalize_food(sample_food_data)
    
    for nutrient in NUTRIENT_CODE_MAP.values():
        assert nutrient in normalized
        assert isinstance(normalized[nutrient], float)

# Standalone test_json_db Function Coverage
def test_standalone_test_json_db_with_missing_file():
    """Test the standalone test_json_db function with missing file"""
    import json_db
    
    with patch('os.path.exists', return_value=False), \
         patch('os.path.dirname', return_value='/fake/path'), \
         patch('os.path.join', return_value='/fake/path/usda_foods.json'), \
         patch('builtins.print') as mock_print:
        
        json_db.test_json_db()
        
        assert mock_print.called

def test_standalone_test_json_db_with_file(temp_json_file):
    """Test the standalone test_json_db function with valid file"""
    import json_db
    
    with patch('os.path.exists', return_value=True), \
         patch('os.path.dirname', return_value=os.path.dirname(temp_json_file)), \
         patch('os.path.join', return_value=temp_json_file), \
         patch('builtins.print') as mock_print:
        
        json_db.test_json_db()
        
        assert mock_print.called
