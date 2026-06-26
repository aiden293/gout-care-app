import pytest
from unittest.mock import MagicMock, patch, ANY

# Mock Class Definitions
class MockNutrientCalculator:
    """Mocks the NutrientCalculator component (UC2)"""
    def calculate_summary(self, ingredients_data):
        total_summary = {"Calories": 0, "Protein": 0}
        for data in ingredients_data:
            portion_size = data.get("portion_size", 1.0)
            
            cal = data['nutrients'].get("Calories", 0)
            if isinstance(cal, str) and cal == "None": 
                 raise ValueError("Invalid nutrient value encountered.")
                 
            total_summary["Calories"] += cal * portion_size
            total_summary["Protein"] += data['nutrients'].get("Protein", 0) * portion_size
        return total_summary

class MockMealNutrientSummary:
    """Mocks the MealNutrientSummary object (UC2)"""
    def __init__(self):
        self.totalNutrients = {}

class MockIngredient:
    """Mocks an Ingredient object"""
    def __init__(self, name, nutrient_data_status):
        self.name = name
        self.nutrient_data_status = nutrient_data_status 

# Pytest Functions
# Creating calculation results and summarization
def test_sc1_calculation_and_summary_success():
    ingredients_data = [{
        "name": "Steak", "portion_size": 2.0, 
        "nutrients": {"Calories": 250, "Protein": 25, "Calcium": 10}
    }]
    
    with patch('test_calculate_nutrients.MockMealNutrientSummary', autospec=True) as MockSummary_Class:
        mock_calc = MockNutrientCalculator() 
        calculated_totals = mock_calc.calculate_summary(ingredients_data)
        MockSummary_Class()
        mock_summary = MockSummary_Class.return_value
        mock_summary.totalNutrients = calculated_totals
        
        assert mock_summary.totalNutrients["Calories"] == 500.0
        assert mock_summary.totalNutrients["Protein"] == 50.0
        MockSummary_Class.assert_called_once()

# Handling multiple ingredients
def test_sc2_handles_multiple_ingredients():
    ingredients_data = [
        {"name": "Rice", "portion_size": 1.0, "nutrients": {"Calories": 200, "Protein": 4}},
        {"name": "Broccoli", "portion_size": 0.5, "nutrients": {"Calories": 50, "Protein": 5}}
    ]
    
    mock_calc = MockNutrientCalculator()
    calculated_totals = mock_calc.calculate_summary(ingredients_data)
    
    assert calculated_totals["Calories"] == 225.0
    assert calculated_totals["Protein"] == 6.5

# Invalid numeric input
def test_fc1_invalid_value_error():
    invalid_data = [{
        "name": "Error Item", "portion_size": 1.0, 
        "nutrients": {"Calories": "None", "Protein": 5}
    }]
    
    mock_calc = MockNutrientCalculator()
    
    with pytest.raises(ValueError) as excinfo:
        mock_calc.calculate_summary(invalid_data)
    
    assert 'Invalid nutrient value encountered.' in str(excinfo.value)
    
# Missing ingredient data in db
def test_ex1_missing_ingredient_data():
    mock_db = MagicMock()
    mock_db.find_nutrients.side_effect = lambda ingredients: (
        {"Steak": {"Calories": 250, "Protein": 25}}, 
        ["Unknown Herb"]
    )
    
    ingredients = [MockIngredient("Steak", "found"), MockIngredient("Unknown Herb", "missing")]
    
    results = mock_db.find_nutrients(ingredients)
    
    assert "Unknown Herb" in results[1]

# Handling fractional amounts and rounding
def test_sc3_handles_fractional_amounts():
    ingredients_data = [
        {"name": "Milk", "portion_size": 0.33, "nutrients": {"Calories": 150, "Calcium": 300}}
    ]
    
    mock_calc = MockNutrientCalculator()
    mock_calc.calculate_summary = MagicMock(return_value={"Calories": 49.5, "Calcium": 99.0})
    
    calculated_totals = mock_calc.calculate_summary(ingredients_data)
    
    assert calculated_totals["Calories"] == 49.5
    assert calculated_totals["Calcium"] == 99.0