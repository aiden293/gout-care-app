"""
Food Service - Business logic for food operations
"""

from typing import List, Optional
from models.food import Food


class FoodService:
    """Service layer for food-related business logic"""
    
    def __init__(self, database):
        """
        Initialize with a database instance
        
        Args:
            database: Database instance with search, get_by_id, get_all methods
        """
        self.database = database
    
    def search_foods(self, query: str, limit: int = 20) -> List[dict]:
        """
        Search for foods by query string
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of food dictionaries
        """
        if not query or len(query) < 2:
            return []
        
        return self.database.search(query, limit=limit)
    
    def get_food_by_id(self, food_id: int) -> Optional[dict]:
        """
        Get a specific food by ID
        
        Args:
            food_id: Food ID
            
        Returns:
            Food dictionary or None if not found
        """
        return self.database.get_by_id(food_id)
    
    def get_all_foods(self, limit: int = 50) -> List[dict]:
        """
        Get all foods (limited)
        
        Args:
            limit: Maximum number of foods to return
            
        Returns:
            List of food dictionaries
        """
        return self.database.get_all(limit=limit)
    
    def filter_by_allergens(self, foods: List[dict], allergens: str) -> List[dict]:
        """
        Filter out foods containing allergen keywords
        
        Args:
            foods: List of food dictionaries
            allergens: Comma-separated allergen keywords
            
        Returns:
            Filtered list of foods
        """
        if not allergens:
            return foods
        
        allergen_keywords = [a.strip().lower() for a in allergens.split(',')]
        filtered = []
        
        for food in foods:
            food_name = food.get('name', '').lower()
            if not any(allergen in food_name for allergen in allergen_keywords):
                filtered.append(food)
        
        return filtered
    
    def validate_food_data(self, food_dict: dict) -> bool:
        """
        Validate that food data has required fields
        
        Args:
            food_dict: Food dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['id', 'name']
        return all(field in food_dict for field in required_fields)
