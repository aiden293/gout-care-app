"""
Food model - represents a food item with nutritional information
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ServingOption:
    """Represents a serving size option for a food item"""
    label: str
    unit: str
    grams_per_unit: float
    gram_weight: float
    amount: float = 1.0
    modifier: str = ''
    description: str = ''
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'label': self.label,
            'unit': self.unit,
            'gramsPerUnit': self.grams_per_unit,
            'gramWeight': self.gram_weight,
            'amount': self.amount,
            'modifier': self.modifier,
            'description': self.description
        }


@dataclass
class Food:
    """Represents a food item with complete nutritional profile"""
    food_id: int
    name: str
    unit: str = '100 g'
    
    # Macronutrients
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    fiber: float = 0.0
    sugar: float = 0.0
    
    # Minerals
    calcium: float = 0.0
    iron: float = 0.0
    magnesium: float = 0.0
    phosphorus: float = 0.0
    potassium: float = 0.0
    sodium: float = 0.0
    zinc: float = 0.0
    
    # Vitamins
    vitamin_a: float = 0.0
    vitamin_c: float = 0.0
    vitamin_d: float = 0.0
    vitamin_e: float = 0.0
    vitamin_k: float = 0.0
    vitamin_b6: float = 0.0
    vitamin_b12: float = 0.0
    folate: float = 0.0
    niacin: float = 0.0
    
    serving_options: List[ServingOption] = field(default_factory=list)
    
    def get_nutrient(self, nutrient_name: str) -> float:
        """Get nutrient value by name (supports both camelCase and snake_case)"""
        # If already snake_case, use directly
        if '_' in nutrient_name:
            return getattr(self, nutrient_name, 0.0)
        
        # Convert camelCase to snake_case
        import re
        # Insert underscore before capital letters
        snake_case = re.sub(r'([a-z])([A-Z])', r'\1_\2', nutrient_name).lower()
        return getattr(self, snake_case, 0.0)
    
    def get_all_nutrients(self) -> Dict[str, float]:
        """Get all nutrients as a dictionary"""
        return {
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'sugar': self.sugar,
            'calcium': self.calcium,
            'iron': self.iron,
            'magnesium': self.magnesium,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'sodium': self.sodium,
            'zinc': self.zinc,
            'vitaminA': self.vitamin_a,
            'vitaminC': self.vitamin_c,
            'vitaminD': self.vitamin_d,
            'vitaminE': self.vitamin_e,
            'vitaminK': self.vitamin_k,
            'vitaminB6': self.vitamin_b6,
            'vitaminB12': self.vitamin_b12,
            'folate': self.folate,
            'niacin': self.niacin
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        nutrients = self.get_all_nutrients()
        return {
            'id': self.food_id,
            'name': self.name,
            'unit': self.unit,
            'servingOptions': [opt.to_dict() for opt in self.serving_options],
            **nutrients
        }
    
    def scale_nutrients(self, multiplier: float) -> Dict[str, float]:
        """Get nutrients scaled by a multiplier"""
        return {k: v * multiplier for k, v in self.get_all_nutrients().items()}
    
    def contains_allergen(self, allergen: str) -> bool:
        """Check if food name contains an allergen keyword"""
        return allergen.lower() in self.name.lower()
