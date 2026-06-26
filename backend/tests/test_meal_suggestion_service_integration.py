"""
Integration tests for MealSuggestionService with actual database
"""

import pytest
from json_db import JsonDatabase
from services.food_service import FoodService
from services.meal_suggestion_service import MealSuggestionService
from models.meal_template import MealTemplate, FoodQuery
import os


@pytest.fixture
def db():
    """Create database instance"""
    json_file = os.path.join(os.path.dirname(__file__), '..', 'usda_foods.json')
    if os.path.exists(json_file):
        return JsonDatabase(json_file)
    return None


@pytest.fixture
def food_service(db):
    """Create FoodService"""
    if db:
        return FoodService(db)
    return None


@pytest.fixture
def meal_service(food_service):
    """Create MealSuggestionService"""
    if food_service:
        return MealSuggestionService(food_service)
    return None


class TestMealSuggestionServiceIntegration:
    """Integration tests for MealSuggestionService"""
    
    def test_suggest_meals_with_deficiencies(self, meal_service):
        """Test meal suggestions with actual deficiencies"""
        if not meal_service:
            pytest.skip("Service not available")
        
        deficiencies = [
            {'nutrient': 'iron', 'amount': 5.0, 'target': 18.0},
            {'nutrient': 'protein', 'amount': 30.0, 'target': 100.0}
        ]
        
        suggestions = meal_service.suggest_meals(deficiencies, '')
        
        assert len(suggestions) > 0
        assert all('name' in s for s in suggestions)
        assert all('foods' in s for s in suggestions)
    
    def test_suggest_meals_empty_deficiencies(self, meal_service):
        """Test with empty deficiencies returns empty list"""
        if not meal_service:
            pytest.skip("Service not available")
        
        suggestions = meal_service.suggest_meals([], '')
        assert suggestions == []
    
    def test_suggest_meals_with_allergen_string(self, meal_service):
        """Test meal suggestions with allergen string"""
        if not meal_service:
            pytest.skip("Service not available")
        
        deficiencies = [{'nutrient': 'protein'}]
        
        suggestions = meal_service.suggest_meals(deficiencies, 'peanut')
        
        # Verify no meals contain peanut in food names
        for meal in suggestions:
            for food in meal.get('foods', []):
                assert 'peanut' not in food['name'].lower()
    
    def test_suggest_meals_with_allergen_list(self, meal_service):
        """Test meal suggestions with allergen list"""
        if not meal_service:
            pytest.skip("Service not available")
        
        deficiencies = [{'nutrient': 'protein'}]
        
        suggestions = meal_service.suggest_meals(deficiencies, ['dairy', 'peanut'])
        
        # Should handle list input
        assert isinstance(suggestions, list)
    
    def test_suggest_meals_max_results(self, meal_service):
        """Test max results parameter"""
        if not meal_service:
            pytest.skip("Service not available")
        
        deficiencies = [
            {'nutrient': 'protein'},
            {'nutrient': 'iron'},
            {'nutrient': 'calcium'}
        ]
        
        suggestions = meal_service.suggest_meals(deficiencies, '', max_results=3)
        
        assert len(suggestions) <= 3
    
    def test_parse_allergens_with_list(self, meal_service):
        """Test _parse_allergens with list input"""
        if not meal_service:
            pytest.skip("Service not available")
        
        allergens = meal_service._parse_allergens(['peanut', 'dairy', 'shellfish'])
        
        assert allergens == ['peanut', 'dairy', 'shellfish']
    
    def test_parse_allergens_with_string(self, meal_service):
        """Test _parse_allergens with comma-separated string"""
        if not meal_service:
            pytest.skip("Service not available")
        
        allergens = meal_service._parse_allergens('peanut, dairy, shellfish')
        
        assert allergens == ['peanut', 'dairy', 'shellfish']
    
    def test_parse_allergens_none(self, meal_service):
        """Test _parse_allergens with None"""
        if not meal_service:
            pytest.skip("Service not available")
        
        allergens = meal_service._parse_allergens(None)
        
        assert allergens == []
    
    def test_safe_float_with_none(self, meal_service):
        """Test _safe_float with None value"""
        if not meal_service:
            pytest.skip("Service not available")
        
        result = meal_service._safe_float(None)
        assert result == 0.0
    
    def test_safe_float_with_default(self, meal_service):
        """Test _safe_float with custom default"""
        if not meal_service:
            pytest.skip("Service not available")
        
        result = meal_service._safe_float(None, default=10.0)
        assert result == 10.0
    
    def test_safe_float_with_invalid(self, meal_service):
        """Test _safe_float with invalid value"""
        if not meal_service:
            pytest.skip("Service not available")
        
        result = meal_service._safe_float("invalid")
        assert result == 0.0
    
    def test_safe_float_with_valid(self, meal_service):
        """Test _safe_float with valid number"""
        if not meal_service:
            pytest.skip("Service not available")
        
        result = meal_service._safe_float("123.45")
        assert result == 123.45
    
    def test_add_meal_template(self, meal_service):
        """Test adding a new meal template"""
        if not meal_service:
            pytest.skip("Service not available")
        
        initial_count = len(meal_service.meal_templates)
        
        new_template = MealTemplate(
            template_id=999,
            name='Test Meal',
            category='Test',
            foods=[FoodQuery('test food', 1.0, '100 g')],
            target_nutrients=['protein']
        )
        
        meal_service.add_meal_template(new_template)
        
        assert len(meal_service.meal_templates) == initial_count + 1
    
    def test_get_templates_by_nutrient(self, meal_service):
        """Test getting templates by nutrient"""
        if not meal_service:
            pytest.skip("Service not available")
        
        # Get templates that address iron
        iron_templates = meal_service.get_templates_by_nutrient('iron')
        
        assert len(iron_templates) > 0
        assert all(t.addresses_deficiency('iron') for t in iron_templates)
    
    def test_get_templates_by_nutrient_case_insensitive(self, meal_service):
        """Test getting templates by nutrient is case insensitive"""
        if not meal_service:
            pytest.skip("Service not available")
        
        templates_lower = meal_service.get_templates_by_nutrient('iron')
        templates_upper = meal_service.get_templates_by_nutrient('IRON')
        templates_mixed = meal_service.get_templates_by_nutrient('IrOn')
        
        assert len(templates_lower) == len(templates_upper)
        assert len(templates_lower) == len(templates_mixed)
    
    def test_build_meal_template_not_found(self, meal_service):
        """Test building meal when foods aren't found"""
        if not meal_service:
            pytest.skip("Service not available")
        
        # Create template with nonsense food query
        template = MealTemplate(
            template_id=1,
            name='Impossible Meal',
            category='Test',
            foods=[FoodQuery('xyznonexistentfood12345', 1.0, '100 g')],
            target_nutrients=['protein']
        )
        
        meal = meal_service._build_meal_from_template(template, [])
        
        # Should return None or empty meal
        assert meal is None or len(meal.get('foods', [])) == 0
    
    def test_suggest_meals_with_no_matching_templates(self, meal_service):
        """Test suggestions when no templates match deficiencies"""
        if not meal_service:
            pytest.skip("Service not available")
        
        # Use a nonsense nutrient that no template addresses
        deficiencies = [{'nutrient': 'nonexistentnutrient12345'}]
        
        suggestions = meal_service.suggest_meals(deficiencies, '')
        
        # May return empty or fewer results
        assert isinstance(suggestions, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
