"""
Unit tests for Food model
"""

import pytest
from models.food import Food, ServingOption


class TestServingOption:
    """Test ServingOption class"""
    
    def test_serving_option_creation(self):
        """Test creating a serving option"""
        serving = ServingOption(
            label='cup',
            unit='cup',
            grams_per_unit=240,
            gram_weight=240
        )
        assert serving.label == 'cup'
        assert serving.grams_per_unit == 240
    
    def test_serving_option_to_dict(self):
        """Test converting serving option to dictionary"""
        serving = ServingOption(
            label='oz',
            unit='oz',
            grams_per_unit=28.35,
            gram_weight=28.35
        )
        result = serving.to_dict()
        assert result['label'] == 'oz'
        assert result['gramsPerUnit'] == 28.35


class TestFood:
    """Test Food model class"""
    
    def test_food_creation(self):
        """Test creating a food instance"""
        food = Food(
            food_id=123,
            name='Chicken Breast',
            calories=165,
            protein=31.0,
            carbs=0.0,
            fat=3.6
        )
        assert food.food_id == 123
        assert food.name == 'Chicken Breast'
        assert food.protein == 31.0
    
    def test_get_nutrient(self):
        """Test getting nutrient by name"""
        food = Food(
            food_id=1,
            name='Test Food',
            protein=10.0,
            vitamin_c=50.0
        )
        assert food.get_nutrient('protein') == 10.0
        assert food.get_nutrient('vitamin_c') == 50.0
        assert food.get_nutrient('iron') == 0.0
    
    def test_get_all_nutrients(self):
        """Test getting all nutrients as dictionary"""
        food = Food(
            food_id=1,
            name='Test Food',
            calories=100,
            protein=5.0,
            carbs=20.0
        )
        nutrients = food.get_all_nutrients()
        assert nutrients['calories'] == 100
        assert nutrients['protein'] == 5.0
        assert nutrients['carbs'] == 20.0
        assert 'iron' in nutrients
    
    def test_scale_nutrients(self):
        """Test scaling nutrients by multiplier"""
        food = Food(
            food_id=1,
            name='Test Food',
            calories=100,
            protein=10.0,
            fat=5.0
        )
        scaled = food.scale_nutrients(2.0)
        assert scaled['calories'] == 200
        assert scaled['protein'] == 20.0
        assert scaled['fat'] == 10.0
    
    def test_contains_allergen(self):
        """Test allergen detection"""
        food = Food(
            food_id=1,
            name='Peanut Butter'
        )
        assert food.contains_allergen('peanut') is True
        assert food.contains_allergen('PEANUT') is True
        assert food.contains_allergen('tree nut') is False
    
    def test_to_dict(self):
        """Test converting food to dictionary"""
        food = Food(
            food_id=123,
            name='Test Food',
            calories=150,
            protein=10.0
        )
        result = food.to_dict()
        assert result['id'] == 123
        assert result['name'] == 'Test Food'
        assert result['calories'] == 150
        assert 'servingOptions' in result
    
    def test_food_with_serving_options(self):
        """Test food with serving options"""
        serving = ServingOption('cup', 'cup', 240, 240)
        food = Food(
            food_id=1,
            name='Milk',
            serving_options=[serving]
        )
        assert len(food.serving_options) == 1
        assert food.serving_options[0].label == 'cup'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
