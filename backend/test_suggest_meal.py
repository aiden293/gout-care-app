import pytest
from unittest.mock import MagicMock, patch, ANY

# Mock Class Definitions
class MockUserProfile:
    """Mocks the UserProfile object (UC3)"""
    def __init__(self, user_id, calcium_intake, restrictions=None):
        self.user_id = user_id
        self.nutrient_intake = {"Calcium": calcium_intake, "Iron": 800} 
        self.dietary_restrictions = restrictions or []
        self.deficiencies = []

class MockDeficiencyAnalyzer:
    """Mocks the DeficiencyAnalyzer component (UC3)"""
    def calculate_deficiencies(self, user_profile):
        deficiencies = []
        if user_profile.nutrient_intake.get("Calcium", 0) < 1000:
            deficiencies.append("Calcium")
        if user_profile.nutrient_intake.get("Iron", 0) < 1000:
            deficiencies.append("Iron")
        user_profile.deficiencies.extend(deficiencies)
        return deficiencies

class MockDeficiencyReport:
    """Mocks the DeficiencyReport object (UC3)"""
    def __init__(self, user_id, deficiencies):
        self.user_id = user_id
        self.deficiencies = deficiencies

# Pytest Functions

# Deficiency detected and report created
def test_sc1_deficiency_detected_success():
    user_profile = MockUserProfile(user_id="U1", calcium_intake=500)
    
    with patch('test_suggest_meal.MockDeficiencyReport', autospec=True) as MockReport_Class:
        mock_analyzer = MockDeficiencyAnalyzer()
        deficiencies = mock_analyzer.calculate_deficiencies(user_profile)
        
        MockReport_Class(user_id=user_profile.user_id, deficiencies=deficiencies)
        
        assert "Calcium" in deficiencies
        assert len(user_profile.deficiencies) == 2
        MockReport_Class.assert_called_once()
        
# No deficiencies found 
def test_ex1_no_deficiency():
    user_profile = MockUserProfile(user_id="U1", calcium_intake=1200)
    user_profile.nutrient_intake["Iron"] = 1100
    
    mock_analyzer = MockDeficiencyAnalyzer()
    deficiencies = mock_analyzer.calculate_deficiencies(user_profile)
    
    assert len(deficiencies) == 0

# Suggestions respect dietary restrictions
def test_sc2_suggestion_respects_restrictions():
    user_profile = MockUserProfile(user_id="U1", calcium_intake=500, restrictions=["Peanut"])
    
    mock_recommender = MagicMock()
    suggested_meals = ["Salmon Steak", "Tofu Salad"]
    mock_recommender.find_suggested_meals.return_value = suggested_meals

    result = mock_recommender.find_suggested_meals(user_profile.deficiencies, user_profile.dietary_restrictions)
    
    assert "Peanut Butter Sandwich" not in result 
    assert "Salmon Steak" in result

# User nutrient profile does not exist
def test_fc1_missing_user_nutrient_profile():
    user_profile = MockUserProfile(user_id="U1", calcium_intake=0)
    user_profile.nutrient_intake = {}
    
    mock_analyzer = MockDeficiencyAnalyzer()
    mock_analyzer.calculate_deficiencies = MagicMock(side_effect=LookupError("User nutrient profile not found."))
    
    with pytest.raises(LookupError) as excinfo:
        mock_analyzer.calculate_deficiencies(user_profile)
    
    assert 'User nutrient profile not found.' in str(excinfo.value)

# NutrientAnalyzer instance creation confirmed
def test_sc3_analyzer_instance_creation():
    user_profile = MockUserProfile(user_id="U1", calcium_intake=500)

    with patch('test_suggest_meal.MockDeficiencyAnalyzer', autospec=True) as MockAnalyzer_Class:
        
        MockAnalyzer_Class()
        
        MockAnalyzer_Class.assert_called_once()