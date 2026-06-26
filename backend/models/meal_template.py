"""
Meal Template model - represents predefined meal suggestions
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class FoodQuery:
    """Represents a food search query with serving information"""
    query: str
    multiplier: float
    unit: str


@dataclass
class MealTemplate:
    """Represents a meal template for suggestions"""
    template_id: int
    name: str
    category: str
    foods: List[FoodQuery] = field(default_factory=list)
    target_nutrients: List[str] = field(default_factory=list)
    
    def matches_allergen(self, allergen_keywords: List[str]) -> bool:
        """Check if template contains any allergen keywords"""
        template_text = f"{self.name} {self.category}".lower()
        for food in self.foods:
            template_text += f" {food.query}".lower()
        
        return any(allergen.lower() in template_text for allergen in allergen_keywords)
    
    def addresses_deficiency(self, deficient_nutrient: str) -> bool:
        """Check if this template addresses a specific deficiency"""
        return deficient_nutrient.lower() in [n.lower() for n in self.target_nutrients]
    
    def count_covered_deficiencies(self, deficient_nutrients: List[str]) -> int:
        """Count how many deficiencies this template addresses"""
        deficit_set = set(n.lower() for n in deficient_nutrients)
        template_set = set(n.lower() for n in self.target_nutrients)
        return len(deficit_set.intersection(template_set))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.template_id,
            'name': self.name,
            'category': self.category,
            'foods': [
                {'query': f.query, 'multiplier': f.multiplier, 'unit': f.unit}
                for f in self.foods
            ],
            'nutrients': self.target_nutrients
        }


# Predefined meal templates
MEAL_TEMPLATES = [
    MealTemplate(
        template_id=1,
        name='Spinach Power Salad',
        category='Salad',
        foods=[
            FoodQuery('spinach raw', 2.0, '100 g'),
            FoodQuery('chicken breast', 1.5, '100 g'),
            FoodQuery('olive oil', 0.3, '100 g')
        ],
        target_nutrients=['iron', 'vitaminA', 'vitaminK', 'protein', 'magnesium']
    ),
    MealTemplate(
        template_id=2,
        name='Salmon & Sweet Potato',
        category='Main Course',
        foods=[
            FoodQuery('salmon', 1.5, '100 g'),
            FoodQuery('sweet potato', 2.0, '100 g'),
            FoodQuery('broccoli', 1.0, '100 g')
        ],
        target_nutrients=['protein', 'vitaminD', 'vitaminB12', 'potassium', 'vitaminC']
    ),
    MealTemplate(
        template_id=3,
        name='Greek Yogurt Parfait',
        category='Breakfast',
        foods=[
            FoodQuery('yogurt greek', 2.0, '100 g'),
            FoodQuery('blueberries', 1.0, '100 g'),
            FoodQuery('almonds', 0.3, '100 g')
        ],
        target_nutrients=['protein', 'calcium', 'vitaminB12', 'vitaminE']
    ),
    MealTemplate(
        template_id=4,
        name='Lentil Curry Bowl',
        category='Main Course',
        foods=[
            FoodQuery('lentils cooked', 2.0, '100 g'),
            FoodQuery('rice brown', 1.5, '100 g'),
            FoodQuery('spinach', 1.0, '100 g')
        ],
        target_nutrients=['protein', 'iron', 'folate', 'fiber', 'magnesium']
    ),
    MealTemplate(
        template_id=5,
        name='Egg & Avocado Toast',
        category='Breakfast',
        foods=[
            FoodQuery('egg', 2.0, '100 g'),
            FoodQuery('avocado', 1.0, '100 g'),
            FoodQuery('bread whole wheat', 1.0, '100 g')
        ],
        target_nutrients=['protein', 'vitaminB12', 'folate', 'vitaminE', 'fat']
    ),
    MealTemplate(
        template_id=6,
        name='Beef & Quinoa Bowl',
        category='Main Course',
        foods=[
            FoodQuery('beef lean', 1.5, '100 g'),
            FoodQuery('quinoa cooked', 1.5, '100 g'),
            FoodQuery('kale', 1.0, '100 g')
        ],
        target_nutrients=['protein', 'iron', 'zinc', 'vitaminB12', 'magnesium']
    ),
    MealTemplate(
        template_id=7,
        name='Tuna Salad Wrap',
        category='Lunch',
        foods=[
            FoodQuery('tuna', 1.5, '100 g'),
            FoodQuery('lettuce', 1.0, '100 g'),
            FoodQuery('tortilla whole wheat', 1.0, '100 g')
        ],
        target_nutrients=['protein', 'vitaminD', 'vitaminB12', 'niacin']
    ),
    MealTemplate(
        template_id=8,
        name='Oatmeal with Berries',
        category='Breakfast',
        foods=[
            FoodQuery('oatmeal', 1.5, '100 g'),
            FoodQuery('strawberries', 1.0, '100 g'),
            FoodQuery('milk', 1.0, '100 g')
        ],
        target_nutrients=['fiber', 'calcium', 'vitaminC', 'iron']
    )
]
