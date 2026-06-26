"""
Integration tests for FoodService with actual database
"""

import pytest
from json_db import JsonDatabase
from services.food_service import FoodService
import os


@pytest.fixture
def db():
    """Create database instance with test data"""
    json_file = os.path.join(os.path.dirname(__file__), '..', 'usda_foods.json')
    if os.path.exists(json_file):
        return JsonDatabase(json_file)
    return None


@pytest.fixture
def service(db):
    """Create FoodService with database"""
    if db:
        return FoodService(db)
    return None


class TestFoodServiceIntegration:
    """Integration tests for FoodService"""
    
    def test_search_foods_with_limit(self, service):
        """Test searching with custom limit"""
        if not service:
            pytest.skip("Database not available")
        
        results = service.search_foods('chicken', limit=5)
        assert len(results) <= 5
    
    def test_search_foods_empty_query(self, service):
        """Test search with empty query returns empty list"""
        if not service:
            pytest.skip("Database not available")
        
        results = service.search_foods('')
        assert results == []
    
    def test_search_foods_short_query(self, service):
        """Test search with single character returns empty"""
        if not service:
            pytest.skip("Database not available")
        
        results = service.search_foods('a')
        assert results == []
    
    def test_get_food_by_id_exists(self, service):
        """Test getting existing food by ID"""
        if not service:
            pytest.skip("Database not available")
        
        # First search for a food to get its ID
        results = service.search_foods('chicken', limit=1)
        if results:
            food_id = results[0]['id']
            food = service.get_food_by_id(food_id)
            assert food is not None
            assert food['id'] == food_id
    
    def test_get_food_by_id_not_exists(self, service):
        """Test getting non-existent food returns None"""
        if not service:
            pytest.skip("Database not available")
        
        food = service.get_food_by_id(999999999)
        assert food is None
    
    def test_get_all_foods(self, service):
        """Test getting all foods with limit"""
        if not service:
            pytest.skip("Database not available")
        
        results = service.get_all_foods(limit=10)
        assert len(results) <= 10
        assert len(results) > 0
    
    def test_filter_by_allergens_removes_matches(self, service):
        """Test allergen filtering removes matching foods"""
        if not service:
            pytest.skip("Database not available")
        
        # Search for peanut-containing foods
        all_foods = service.search_foods('peanut', limit=10)
        
        # Filter out peanut allergen
        filtered = service.filter_by_allergens(all_foods, 'peanut')
        
        # All foods should be filtered out since they contain 'peanut'
        assert len(filtered) == 0
    
    def test_filter_by_allergens_empty_string(self, service):
        """Test filtering with empty allergen string returns all"""
        if not service:
            pytest.skip("Database not available")
        
        foods = service.search_foods('chicken', limit=5)
        filtered = service.filter_by_allergens(foods, '')
        
        assert len(filtered) == len(foods)
    
    def test_filter_by_allergens_multiple(self, service):
        """Test filtering with multiple allergens"""
        if not service:
            pytest.skip("Database not available")
        
        foods = service.search_foods('butter', limit=10)
        filtered = service.filter_by_allergens(foods, 'peanut,almond')
        
        # Check that filtered foods don't contain allergens
        for food in filtered:
            name_lower = food['name'].lower()
            assert 'peanut' not in name_lower
            assert 'almond' not in name_lower
    
    def test_validate_food_data_valid(self, service):
        """Test validating valid food data"""
        if not service:
            pytest.skip("Database not available")
        
        valid_food = {
            'id': 1,
            'name': 'Test Food',
            'calories': 100
        }
        
        assert service.validate_food_data(valid_food) is True
    
    def test_validate_food_data_missing_id(self, service):
        """Test validation fails without id"""
        if not service:
            pytest.skip("Database not available")
        
        invalid_food = {
            'name': 'Test Food',
            'calories': 100
        }
        
        assert service.validate_food_data(invalid_food) is False
    
    def test_validate_food_data_missing_name(self, service):
        """Test validation fails without name"""
        if not service:
            pytest.skip("Database not available")
        
        invalid_food = {
            'id': 1,
            'calories': 100
        }
        
        assert service.validate_food_data(invalid_food) is False
    
    def test_validate_food_data_empty_dict(self, service):
        """Test validation fails with empty dict"""
        if not service:
            pytest.skip("Database not available")
        
        assert service.validate_food_data({}) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
