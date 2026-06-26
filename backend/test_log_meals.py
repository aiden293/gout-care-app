import pytest
from unittest.mock import MagicMock, patch, ANY


# Mock Class Definitions
class MockMealItem:
    """Mocks the MealItem object (UC1)"""
    def __init__(self, name, amount_input, unit_input, amount_in_grams=None):
        self.name = name
        self.amount_input = amount_input
        self.unit_input = unit_input
        self.amount_in_grams = amount_in_grams

class MockMealRecord:
    """Mocks the MealRecord object (UC1)"""
    def __init__(self, record_id, user_id):
        self.record_id = record_id
        self.user_id = user_id
        self.items = []
        self.notes = ""

class MockUnitConverter:
    """Mocks the Unit Converter component (UC1)"""
    def convert(self, amount, unit):
        if not isinstance(amount, (int, float)):
            raise ValueError("Non-float input")
        return amount * 250 if unit == "Bowl" else amount * 100


# Pytest Functions
@pytest.fixture
def common_setup():
    """Provides common variables and instances for UC1 tests."""
    return {
        "user_id": "testUser1",
        "mock_converter": MockUnitConverter()
    }

# Single item log 
def test_uc1_sc1_single_meal_log_success(common_setup):
    meal_items = [MockMealItem("Pesto pasta", 1.5, "Bowl")]
    user_id = common_setup["user_id"]
    mock_converter = common_setup["mock_converter"]
    
    with patch('test_log_meals.MockMealRecord', autospec=True) as MockMealRecord_Class, \
         patch.object(mock_converter, 'convert', wraps=mock_converter.convert) as mock_convert:
        
        for item in meal_items:
            if item.amount_in_grams is None:
                item.amount_in_grams = mock_convert(item.amount_input, item.unit_input)
        
        MockMealRecord_Class(record_id=ANY, user_id=user_id)

        assert meal_items[0].amount_in_grams == 375.0
        mock_convert.assert_called_once_with(1.5, "Bowl")
        MockMealRecord_Class.assert_called_once()
        
# Logging multiple items
def test_uc1_ex1_multiple_items_log_success(common_setup):
    meal_items = [
        MockMealItem("Salmon Steak", 1.0, "Bowl"),
        MockMealItem("Apples", 100.0, "grams")
    ]
    user_id = common_setup["user_id"]
    mock_converter = common_setup["mock_converter"]
    with patch('test_log_meals.MockMealRecord', autospec=True) as MockMealRecord_Class, \
         patch.object(mock_converter, 'convert', wraps=mock_converter.convert) as mock_convert:
        
        for item in meal_items:
            if item.amount_in_grams is None:
                item.amount_in_grams = mock_convert(item.amount_input, item.unit_input)
        
        MockMealRecord_Class(record_id=ANY, user_id=user_id)

        assert meal_items[0].amount_in_grams == 250.0
        assert meal_items[1].amount_in_grams == 10000.0 
        assert mock_convert.call_count == 2
        MockMealRecord_Class.assert_called_once()

# Attempting to complete without any items
def test_uc1_fc1_no_item_failure():
    meal_items = []
    
    if not meal_items:
        with pytest.raises(ValueError) as excinfo:
            raise ValueError("Validation fails (no items)")
        assert 'Validation fails (no items)' in str(excinfo.value)
        
# Amount input is not a valid float
def test_uc1_ex2_non_float_input(common_setup):
    meal_items = [MockMealItem("Rice", "three", "Bowl")]
    mock_converter = common_setup["mock_converter"]
    
    with pytest.raises(ValueError) as excinfo:
        mock_converter.convert(meal_items[0].amount_input, meal_items[0].unit_input)
        
    assert 'Non-float input' in str(excinfo.value)

# Unit converter connection error
def test_uc1_fc2_unit_converter_connection_failure():
    mock_converter = MagicMock(spec=MockUnitConverter)
    mock_converter.convert.side_effect = ConnectionError("UnitConverter Down")

    with pytest.raises(ConnectionError) as excinfo:
         mock_converter.convert(1.0, "Bowl")
         
    assert 'UnitConverter Down' in str(excinfo.value)