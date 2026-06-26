"""
Nutrient models - represents nutritional information and profiles
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Nutrient:
    """Represents a single nutrient with its properties"""
    name: str
    amount: float
    unit: str
    target: float = 0.0
    
    def get_deficit(self) -> float:
        """Calculate deficit if below target"""
        return max(0, self.target - self.amount)
    
    def is_deficient(self) -> bool:
        """Check if nutrient is below target"""
        return self.amount < self.target
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'nutrient': self.name,
            'amount': self.amount,
            'unit': self.unit,
            'target': self.target,
            'deficit': self.get_deficit()
        }


class NutrientProfile:
    """Manages a collection of nutrients and calculates totals/deficiencies"""
    
    # Standard nutrient units
    NUTRIENT_UNITS = {
        'calories': 'kcal',
        'protein': 'g', 'carbs': 'g', 'fat': 'g', 'fiber': 'g', 'sugar': 'g',
        'calcium': 'mg', 'iron': 'mg', 'magnesium': 'mg', 'phosphorus': 'mg',
        'potassium': 'mg', 'sodium': 'mg', 'zinc': 'mg',
        'vitaminA': 'µg RAE', 'vitaminC': 'mg', 'vitaminD': 'µg',
        'vitaminE': 'mg', 'vitaminK': 'µg', 'vitaminB6': 'mg',
        'vitaminB12': 'µg', 'folate': 'µg DFE', 'niacin': 'mg'
    }
    
    def __init__(self):
        self.nutrients: Dict[str, float] = {}
    
    def add_nutrient(self, name: str, amount: float) -> None:
        """Add or update a nutrient amount"""
        self.nutrients[name] = self.nutrients.get(name, 0.0) + amount
    
    def add_from_dict(self, nutrient_dict: Dict[str, float]) -> None:
        """Add nutrients from a dictionary"""
        for name, amount in nutrient_dict.items():
            self.add_nutrient(name, amount)
    
    def get_nutrient(self, name: str) -> float:
        """Get nutrient amount"""
        return self.nutrients.get(name, 0.0)
    
    def get_all_nutrients(self) -> Dict[str, float]:
        """Get all nutrients"""
        return self.nutrients.copy()
    
    def calculate_deficiencies(self, targets: Dict[str, float]) -> list:
        """Calculate nutrient deficiencies based on targets"""
        deficiencies = []
        
        for nutrient_name, target in targets.items():
            current = self.get_nutrient(nutrient_name)
            if current < target:
                unit = self.NUTRIENT_UNITS.get(nutrient_name, 'units')
                nutrient = Nutrient(
                    name=nutrient_name,
                    amount=current,
                    unit=unit,
                    target=target
                )
                deficiencies.append(nutrient)
        
        return deficiencies
    
    def get_daily_average(self, days: int) -> Dict[str, float]:
        """Calculate daily average from total"""
        if days <= 0:
            return {}
        return {k: v / days for k, v in self.nutrients.items()}
    
    @classmethod
    def get_macro_targets(cls, weight_kg: float) -> Dict[str, float]:
        """Calculate macronutrient targets based on body weight"""
        return {
            'protein': weight_kg * 1.6,
            'carbs': weight_kg * 3,
            'fat': weight_kg * 0.8,
            'fiber': 25,
            'sugar': 50
        }
    
    @classmethod
    def get_micro_targets(cls) -> Dict[str, float]:
        """Get standard micronutrient targets (RDA)"""
        return {
            'calcium': 1000,
            'iron': 18,
            'magnesium': 420,
            'potassium': 3500,
            'vitaminC': 90,
            'vitaminD': 20,
            'vitaminB12': 2.4,
            'folate': 400,
            'vitaminA': 900,
            'vitaminK': 120
        }
