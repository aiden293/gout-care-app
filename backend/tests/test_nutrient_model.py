"""
Unit tests for Nutrient models
"""

import pytest
from models.nutrient import Nutrient, NutrientProfile


class TestNutrient:
    """Test Nutrient class"""
    
    def test_nutrient_creation(self):
        """Test creating a nutrient"""
        nutrient = Nutrient(
            name='protein',
            amount=50.0,
            unit='g',
            target=100.0
        )
        assert nutrient.name == 'protein'
        assert nutrient.amount == 50.0
        assert nutrient.target == 100.0
    
    def test_get_deficit(self):
        """Test calculating deficit"""
        nutrient = Nutrient('protein', 50.0, 'g', 100.0)
        assert nutrient.get_deficit() == 50.0
        
        # No deficit if above target
        nutrient2 = Nutrient('protein', 150.0, 'g', 100.0)
        assert nutrient2.get_deficit() == 0.0
    
    def test_is_deficient(self):
        """Test checking if nutrient is deficient"""
        deficient = Nutrient('iron', 5.0, 'mg', 18.0)
        assert deficient.is_deficient() is True
        
        sufficient = Nutrient('iron', 20.0, 'mg', 18.0)
        assert sufficient.is_deficient() is False
    
    def test_to_dict(self):
        """Test converting nutrient to dictionary"""
        nutrient = Nutrient('calcium', 500.0, 'mg', 1000.0)
        result = nutrient.to_dict()
        assert result['nutrient'] == 'calcium'
        assert result['amount'] == 500.0
        assert result['target'] == 1000.0
        assert result['deficit'] == 500.0


class TestNutrientProfile:
    """Test NutrientProfile class"""
    
    def test_profile_creation(self):
        """Test creating a nutrient profile"""
        profile = NutrientProfile()
        assert len(profile.nutrients) == 0
    
    def test_add_nutrient(self):
        """Test adding nutrients"""
        profile = NutrientProfile()
        profile.add_nutrient('protein', 10.0)
        profile.add_nutrient('protein', 5.0)  # Should accumulate
        assert profile.get_nutrient('protein') == 15.0
    
    def test_add_from_dict(self):
        """Test adding nutrients from dictionary"""
        profile = NutrientProfile()
        nutrients = {'protein': 20.0, 'carbs': 50.0, 'fat': 10.0}
        profile.add_from_dict(nutrients)
        assert profile.get_nutrient('protein') == 20.0
        assert profile.get_nutrient('carbs') == 50.0
    
    def test_get_all_nutrients(self):
        """Test getting all nutrients"""
        profile = NutrientProfile()
        profile.add_nutrient('protein', 10.0)
        profile.add_nutrient('carbs', 20.0)
        nutrients = profile.get_all_nutrients()
        assert nutrients['protein'] == 10.0
        assert nutrients['carbs'] == 20.0
    
    def test_calculate_deficiencies(self):
        """Test calculating deficiencies"""
        profile = NutrientProfile()
        profile.add_nutrient('protein', 50.0)
        profile.add_nutrient('iron', 5.0)
        profile.add_nutrient('calcium', 1200.0)
        
        targets = {
            'protein': 100.0,
            'iron': 18.0,
            'calcium': 1000.0
        }
        
        deficiencies = profile.calculate_deficiencies(targets)
        assert len(deficiencies) == 2  # protein and iron
        
        deficit_names = [d.name for d in deficiencies]
        assert 'protein' in deficit_names
        assert 'iron' in deficit_names
        assert 'calcium' not in deficit_names
    
    def test_get_daily_average(self):
        """Test calculating daily average"""
        profile = NutrientProfile()
        profile.add_nutrient('protein', 70.0)
        profile.add_nutrient('carbs', 210.0)
        
        daily = profile.get_daily_average(7)
        assert daily['protein'] == 10.0
        assert daily['carbs'] == 30.0
    
    def test_get_daily_average_zero_days(self):
        """Test daily average with zero days"""
        profile = NutrientProfile()
        profile.add_nutrient('protein', 70.0)
        daily = profile.get_daily_average(0)
        assert len(daily) == 0
    
    def test_get_macro_targets(self):
        """Test getting macronutrient targets"""
        targets = NutrientProfile.get_macro_targets(70)  # 70kg
        assert targets['protein'] == 112.0  # 70 * 1.6
        assert targets['carbs'] == 210.0    # 70 * 3
        assert targets['fat'] == 56.0       # 70 * 0.8
        assert targets['fiber'] == 25
    
    def test_get_micro_targets(self):
        """Test getting micronutrient targets"""
        targets = NutrientProfile.get_micro_targets()
        assert targets['calcium'] == 1000
        assert targets['iron'] == 18
        assert targets['vitaminC'] == 90
    
    def test_nutrient_units(self):
        """Test nutrient units are defined"""
        assert 'calories' in NutrientProfile.NUTRIENT_UNITS
        assert 'protein' in NutrientProfile.NUTRIENT_UNITS
        assert NutrientProfile.NUTRIENT_UNITS['calories'] == 'kcal'
        assert NutrientProfile.NUTRIENT_UNITS['protein'] == 'g'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
