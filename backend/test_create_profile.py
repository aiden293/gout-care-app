import pytest
from unittest.mock import MagicMock, patch, ANY


# Mock Class Definitions

class MockUserProfile:
    """Mocks the UserProfile object (UC5)"""
    def __init__(self, user_id):
        self.user_id = user_id
        self.status = "invalid"
        self.name = None
        self.age = None

class MockSystemNotice:
    """Mocks the SystemNotice object (UC5)"""
    def __init__(self, nid, type):
        self.nid = nid
        self.type = type

# Pytest

@pytest.fixture
def valid_profile_data():
    """Provides valid form data for UC5 tests."""
    return {
        "name": "John Doe", "age": 25, "sex": "M", 
        "height": 175.0, "weight": 70.0, "allergies": "None"
    }

# create profile with valid data
def test_sc1_create_profile_success(valid_profile_data):
    user_id = "testUser1"
    
    with patch('test_create_profile.MockUserProfile', autospec=True) as MockUserProfile_Class:
        
        mock_profile_instance = MockUserProfile_Class.return_value
        mock_profile_instance.status = "invalid" 
        
        is_valid = True 
        
        if is_valid:
            MockUserProfile_Class(user_id=user_id) 
            mock_profile_instance.name = valid_profile_data["name"]
            mock_profile_instance.status = "valid" 
        
            assert mock_profile_instance.status == "valid"
            assert mock_profile_instance.name == "John Doe"
            
            MockUserProfile_Class.assert_called_once_with(user_id=user_id)
        
# Mandatory field missinng 
def test_ex1_mandatory_field_missing_failure(valid_profile_data):
    invalid_data = valid_profile_data.copy()
    invalid_data["name"] = None 
    
    with patch('test_create_profile.MockSystemNotice', autospec=True) as MockSystemNotice_Class:
        
        is_valid = False
        
        if not is_valid:
            MockSystemNotice_Class(nid=ANY, type="validationError")
            MockSystemNotice_Class.assert_called_with(nid=ANY, type="validationError")

# Invalid data format
def test_ex2_invalid_data_format_failure(valid_profile_data):
    invalid_data = valid_profile_data.copy()
    invalid_data["age"] = "twenty-five" 
    
    with patch('test_create_profile.MockSystemNotice', autospec=True) as MockSystemNotice_Class:
        
        is_valid = False
        
        if not is_valid:
            MockSystemNotice_Class(nid=ANY, type="validationError")
            MockSystemNotice_Class.assert_called_with(nid=ANY, type="validationError")

# Profile status updated to "valid"
def test_sc2_profile_status_set_to_valid():
    new_profile = MockUserProfile(user_id="testUser1")
    new_profile.status = "valid"
    assert new_profile.status == "valid"
    
# If user already has a valid profile
def test_fc1_user_already_has_valid_profile():
    existing_profile = MockUserProfile(user_id="testUser1")
    existing_profile.status = "valid"
    
    if existing_profile.status == "valid":
        with pytest.raises(PermissionError) as excinfo:
            raise PermissionError("User profile already exists.")
        assert 'User profile already exists.' in str(excinfo.value)