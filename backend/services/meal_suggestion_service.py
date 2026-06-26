"""
Meal Suggestion Service - Business logic for generating meal suggestions
"""

from typing import List, Dict, Optional
from models.meal_template import MealTemplate, MEAL_TEMPLATES
from models.nutrient import NutrientProfile


class MealSuggestionService:
    """Service for generating personalized meal suggestions"""
    
    def __init__(self, food_service):
        """
        Initialize with food service dependency
        
        Args:
            food_service: FoodService instance for searching foods
        """
        self.food_service = food_service
        self.meal_templates = MEAL_TEMPLATES
    
    def suggest_meals(
        self,
        deficiencies: List[Dict],
        allergies: str = '',
        max_results: int = 8
    ) -> List[Dict]:
        """
        Generate meal suggestions based on nutrient deficiencies
        
        Args:
            deficiencies: List of nutrient deficiencies
            allergies: Comma-separated allergen keywords
            max_results: Maximum number of meal suggestions
            
        Returns:
            List of suggested meals with scores
        """
        if not deficiencies:
            return []
        
        # Extract deficient nutrient names
        deficit_nutrients = [d['nutrient'] for d in deficiencies]
        allergen_keywords = self._parse_allergens(allergies)
        
        scored_meals = []
        
        for template in self.meal_templates:
            # Skip if template contains allergens
            if template.matches_allergen(allergen_keywords):
                continue
            
            # Calculate how many deficiencies this meal addresses
            coverage_count = template.count_covered_deficiencies(deficit_nutrients)
            
            if coverage_count > 0:
                # Build the meal with actual food data
                meal_data = self._build_meal_from_template(
                    template,
                    allergen_keywords
                )
                
                if meal_data:
                    meal_data['deficitsCovered'] = coverage_count
                    meal_data['score'] = coverage_count
                    scored_meals.append(meal_data)
        
        # Sort by score and return top results
        scored_meals.sort(key=lambda x: x['score'], reverse=True)
        return scored_meals[:max_results]
    
    def _parse_allergens(self, allergies) -> List[str]:
        """Parse allergen string or list into list of keywords"""
        if not allergies:
            return []
        
        # Handle list input
        if isinstance(allergies, list):
            return [a.strip().lower() if isinstance(a, str) else str(a).lower() for a in allergies]
        
        # Handle string input
        return [a.strip().lower() for a in allergies.split(',')]
    
    def _build_meal_from_template(
        self,
        template: MealTemplate,
        allergen_keywords: List[str]
    ) -> Optional[Dict]:
        """
        Build a complete meal from a template by searching for foods
        
        Args:
            template: MealTemplate to build from
            allergen_keywords: List of allergen keywords to avoid
            
        Returns:
            Complete meal dictionary or None if any food contains allergen
        """
        foods = []
        nutrient_profile = NutrientProfile()
        
        for food_query in template.foods:
            # Search for the food
            search_results = self.food_service.search_foods(
                food_query.query,
                limit=1
            )
            
            if not search_results:
                continue
            
            food = search_results[0]
            food_name = food.get('name', '').lower()
            
            # Check if this specific food contains allergen
            if any(allergen in food_name for allergen in allergen_keywords):
                return None  # Skip entire meal
            
            multiplier = food_query.multiplier
            
            # Scale nutrients by multiplier
            scaled_nutrients = {}
            for key in nutrient_profile.NUTRIENT_UNITS.keys():
                value = food.get(key, 0)
                scaled_value = self._safe_float(value) * multiplier
                scaled_nutrients[key] = scaled_value
                nutrient_profile.add_nutrient(key, scaled_value)
            
            # Add food to meal
            foods.append({
                'id': food.get('id'),
                'name': food.get('name'),
                'amount': multiplier,
                'unit': food_query.unit,
                'nutrients': scaled_nutrients
            })
        
        if not foods:
            return None
        
        return {
            'id': template.template_id,
            'name': template.name,
            'category': template.category,
            'foods': foods,
            'totalNutrients': nutrient_profile.get_all_nutrients()
        }
    
    def _safe_float(self, value, default: float = 0.0) -> float:
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def add_meal_template(self, template: MealTemplate) -> None:
        """Add a new meal template to the collection"""
        self.meal_templates.append(template)
    
    def get_templates_by_nutrient(self, nutrient: str) -> List[MealTemplate]:
        """Get all templates that address a specific nutrient"""
        return [
            t for t in self.meal_templates
            if t.addresses_deficiency(nutrient)
        ]
