"""
Unit tests for MealTemplate model
"""

import pytest
from models.meal_template import MealTemplate, FoodQuery, MEAL_TEMPLATES


class TestFoodQuery:
    """Test FoodQuery dataclass"""
    
    def test_food_query_creation(self):
        """Test creating a food query"""
        query = FoodQuery('chicken breast', 1.5, '100 g')
        assert query.query == 'chicken breast'
        assert query.multiplier == 1.5
        assert query.unit == '100 g'


class TestMealTemplate:
    """Test MealTemplate class"""
    
    def test_template_creation(self):
        """Test creating a meal template"""
        template = MealTemplate(
            template_id=1,
            name='Test Meal',
            category='Lunch',
            foods=[FoodQuery('chicken', 1.0, '100 g')],
            target_nutrients=['protein', 'iron']
        )
        assert template.name == 'Test Meal'
        assert len(template.foods) == 1
        assert len(template.target_nutrients) == 2
    
    def test_matches_allergen(self):
        """Test allergen matching"""
        template = MealTemplate(
            template_id=1,
            name='Peanut Butter Sandwich',
            category='Lunch',
            foods=[FoodQuery('peanut butter', 1.0, '100 g')],
            target_nutrients=['protein']
        )
        assert template.matches_allergen(['peanut']) is True
        assert template.matches_allergen(['tree nut']) is False
        assert template.matches_allergen([]) is False
    
    def test_addresses_deficiency(self):
        """Test checking if template addresses deficiency"""
        template = MealTemplate(
            template_id=1,
            name='Spinach Salad',
            category='Salad',
            foods=[],
            target_nutrients=['iron', 'vitaminA', 'vitaminK']
        )
        assert template.addresses_deficiency('iron') is True
        assert template.addresses_deficiency('IRON') is True  # Case insensitive
        assert template.addresses_deficiency('calcium') is False
    
    def test_count_covered_deficiencies(self):
        """Test counting covered deficiencies"""
        template = MealTemplate(
            template_id=1,
            name='Test Meal',
            category='Lunch',
            foods=[],
            target_nutrients=['protein', 'iron', 'vitaminC']
        )
        
        # Template addresses 2 out of 4 deficiencies
        deficiencies = ['protein', 'iron', 'calcium', 'vitaminD']
        count = template.count_covered_deficiencies(deficiencies)
        assert count == 2
    
    def test_count_covered_deficiencies_none(self):
        """Test count when no deficiencies covered"""
        template = MealTemplate(
            template_id=1,
            name='Test Meal',
            category='Lunch',
            foods=[],
            target_nutrients=['protein']
        )
        deficiencies = ['calcium', 'iron']
        count = template.count_covered_deficiencies(deficiencies)
        assert count == 0
    
    def test_to_dict(self):
        """Test converting template to dictionary"""
        template = MealTemplate(
            template_id=5,
            name='Greek Yogurt Bowl',
            category='Breakfast',
            foods=[
                FoodQuery('yogurt', 2.0, '100 g'),
                FoodQuery('berries', 1.0, '100 g')
            ],
            target_nutrients=['protein', 'calcium']
        )
        result = template.to_dict()
        assert result['id'] == 5
        assert result['name'] == 'Greek Yogurt Bowl'
        assert len(result['foods']) == 2
        assert len(result['nutrients']) == 2


class TestMealTemplates:
    """Test predefined meal templates"""
    
    def test_meal_templates_loaded(self):
        """Test that meal templates are loaded"""
        assert len(MEAL_TEMPLATES) > 0
        assert all(isinstance(t, MealTemplate) for t in MEAL_TEMPLATES)
    
    def test_template_ids_unique(self):
        """Test that template IDs are unique"""
        ids = [t.template_id for t in MEAL_TEMPLATES]
        assert len(ids) == len(set(ids))
    
    def test_templates_have_foods(self):
        """Test that all templates have food queries"""
        for template in MEAL_TEMPLATES:
            assert len(template.foods) > 0
    
    def test_templates_have_target_nutrients(self):
        """Test that all templates have target nutrients"""
        for template in MEAL_TEMPLATES:
            assert len(template.target_nutrients) > 0
    
    def test_specific_template_exists(self):
        """Test that specific templates exist"""
        names = [t.name for t in MEAL_TEMPLATES]
        assert 'Spinach Power Salad' in names
        assert 'Salmon & Sweet Potato' in names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
