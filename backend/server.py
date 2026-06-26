#!/usr/bin/env python3
"""
Python Backend for ATE Nutrition Tracking App
Equivalent to server.js - supports both MySQL and JSON database modes
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from services.food_service import FoodService
from services.meal_suggestion_service import MealSuggestionService
from models.meal_template import MEAL_TEMPLATES

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
PORT = int(os.getenv('PORT', 5001))  # Use 5001 to avoid conflict with Node.js server
USE_JSON_DB = os.getenv('USE_JSON_DB', 'true').lower() in ('1', 'true', 'yes')

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'nutrition_db')
}

# JSON Database
json_db = None
food_service = None
meal_service = None

if USE_JSON_DB:
    try:
        from json_db import JsonDatabase
        json_file = os.path.join(os.path.dirname(__file__), 'usda_foods.json')
        if os.path.exists(json_file):
            json_db = JsonDatabase(json_file)
            print(f"✓ JSON database loaded from {json_file}")
            
            # Initialize services with dependency injection
            food_service = FoodService(json_db)
            meal_service = MealSuggestionService(food_service)
            print("✓ Services initialized")
        else:
            print(f"⚠ JSON file not found: {json_file}")
    except ImportError as e:
        print(f"⚠ Error importing modules: {e}")
        print("⚠ Falling back to SQL mode")
        USE_JSON_DB = False

# Helper Functions
def get_db_connection():
    """Create MySQL database connection"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def safe_float(value, default=0.0):
    """Safely convert value to float"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def search_foods_sql(query):
    """Search foods using MySQL database"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        sql_query = """
            SELECT DISTINCT
                f.fdc_id as id,
                f.description as name,
                '100 g' as unit,
                MAX(CASE WHEN n.nutrient_id = 208 THEN fn.amount END) as calories,
                MAX(CASE WHEN n.nutrient_id = 203 THEN fn.amount END) as protein,
                MAX(CASE WHEN n.nutrient_id = 205 THEN fn.amount END) as carbs,
                MAX(CASE WHEN n.nutrient_id = 204 THEN fn.amount END) as fat,
                MAX(CASE WHEN n.nutrient_id = 291 THEN fn.amount END) as fiber,
                MAX(CASE WHEN n.nutrient_id = 269 THEN fn.amount END) as sugar,
                MAX(CASE WHEN n.nutrient_id = 301 THEN fn.amount END) as calcium,
                MAX(CASE WHEN n.nutrient_id = 303 THEN fn.amount END) as iron,
                MAX(CASE WHEN n.nutrient_id = 304 THEN fn.amount END) as magnesium,
                MAX(CASE WHEN n.nutrient_id = 305 THEN fn.amount END) as phosphorus,
                MAX(CASE WHEN n.nutrient_id = 306 THEN fn.amount END) as potassium,
                MAX(CASE WHEN n.nutrient_id = 307 THEN fn.amount END) as sodium,
                MAX(CASE WHEN n.nutrient_id = 309 THEN fn.amount END) as zinc,
                MAX(CASE WHEN n.nutrient_id = 320 THEN fn.amount END) as vitaminA,
                MAX(CASE WHEN n.nutrient_id = 401 THEN fn.amount END) as vitaminC,
                MAX(CASE WHEN n.nutrient_id = 328 THEN fn.amount END) as vitaminD,
                MAX(CASE WHEN n.nutrient_id = 323 THEN fn.amount END) as vitaminE,
                MAX(CASE WHEN n.nutrient_id = 430 THEN fn.amount END) as vitaminK,
                MAX(CASE WHEN n.nutrient_id = 415 THEN fn.amount END) as vitaminB6,
                MAX(CASE WHEN n.nutrient_id = 418 THEN fn.amount END) as vitaminB12,
                MAX(CASE WHEN n.nutrient_id = 417 THEN fn.amount END) as folate,
                MAX(CASE WHEN n.nutrient_id = 406 THEN fn.amount END) as niacin
            FROM food f
            JOIN food_nutrient fn ON f.fdc_id = fn.fdc_id
            JOIN nutrient n ON fn.nutrient_id = n.id
            WHERE f.description LIKE %s
            GROUP BY f.fdc_id, f.description
            LIMIT 20
        """
        cursor.execute(sql_query, (f'%{query}%',))
        results = cursor.fetchall()

        for row in results:
            for key in row:
                if key not in ('id', 'name', 'unit') and row[key] is None:
                    row[key] = 0.0
        
        return results
    except Error as e:
        print(f"SQL Error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def search_foods_json(query):
    """Search foods using JSON database"""
    if not json_db:
        return []
    return json_db.search(query)

# Meal templates are now imported from models.meal_template
# MEAL_TEMPLATES constant provides backward compatibility

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    db_mode = 'JSON' if USE_JSON_DB else 'SQL'
    json_available = json_db is not None
    return jsonify({
        'status': 'ok',
        'mode': db_mode,
        'json_db_available': json_available,
        'backend': 'Python/Flask'
    })

@app.route('/api/foods', methods=['GET'])
def get_all_foods():
    """Get all foods (limited to 50)"""
    if USE_JSON_DB and json_db:
        results = json_db.get_all(limit=50)
    else:
        connection = get_db_connection()
        if not connection:
            return jsonify([])
        
        try:
            cursor = connection.cursor(dictionary=True)
            sql_query = """
                SELECT DISTINCT
                    f.fdc_id as id,
                    f.description as name,
                    '100 g' as unit,
                    MAX(CASE WHEN n.nutrient_id = 208 THEN fn.amount END) as calories,
                    MAX(CASE WHEN n.nutrient_id = 203 THEN fn.amount END) as protein,
                    MAX(CASE WHEN n.nutrient_id = 205 THEN fn.amount END) as carbs,
                    MAX(CASE WHEN n.nutrient_id = 204 THEN fn.amount END) as fat,
                    MAX(CASE WHEN n.nutrient_id = 291 THEN fn.amount END) as fiber,
                    MAX(CASE WHEN n.nutrient_id = 269 THEN fn.amount END) as sugar,
                    MAX(CASE WHEN n.nutrient_id = 301 THEN fn.amount END) as calcium,
                    MAX(CASE WHEN n.nutrient_id = 303 THEN fn.amount END) as iron,
                    MAX(CASE WHEN n.nutrient_id = 304 THEN fn.amount END) as magnesium,
                    MAX(CASE WHEN n.nutrient_id = 305 THEN fn.amount END) as phosphorus,
                    MAX(CASE WHEN n.nutrient_id = 306 THEN fn.amount END) as potassium,
                    MAX(CASE WHEN n.nutrient_id = 307 THEN fn.amount END) as sodium,
                    MAX(CASE WHEN n.nutrient_id = 309 THEN fn.amount END) as zinc,
                    MAX(CASE WHEN n.nutrient_id = 320 THEN fn.amount END) as vitaminA,
                    MAX(CASE WHEN n.nutrient_id = 401 THEN fn.amount END) as vitaminC,
                    MAX(CASE WHEN n.nutrient_id = 328 THEN fn.amount END) as vitaminD,
                    MAX(CASE WHEN n.nutrient_id = 323 THEN fn.amount END) as vitaminE,
                    MAX(CASE WHEN n.nutrient_id = 430 THEN fn.amount END) as vitaminK,
                    MAX(CASE WHEN n.nutrient_id = 415 THEN fn.amount END) as vitaminB6,
                    MAX(CASE WHEN n.nutrient_id = 418 THEN fn.amount END) as vitaminB12,
                    MAX(CASE WHEN n.nutrient_id = 417 THEN fn.amount END) as folate,
                    MAX(CASE WHEN n.nutrient_id = 406 THEN fn.amount END) as niacin
                FROM food f
                JOIN food_nutrient fn ON f.fdc_id = fn.fdc_id
                JOIN nutrient n ON fn.nutrient_id = n.id
                GROUP BY f.fdc_id, f.description
                LIMIT 50
            """
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            for row in results:
                for key in row:
                    if key not in ('id', 'name', 'unit') and row[key] is None:
                        row[key] = 0.0
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify(results)

@app.route('/api/foods/search/<query>', methods=['GET'])
def search_foods(query):
    """Search for foods by query string"""
    if not query or len(query) < 2:
        return jsonify([])
    
    # Use FoodService if available, otherwise fall back to direct database access
    if USE_JSON_DB and food_service:
        results = food_service.search_foods(query)
    elif USE_JSON_DB and json_db:
        results = search_foods_json(query)
    else:
        results = search_foods_sql(query)
    
    return jsonify(results)

@app.route('/api/suggest-meals', methods=['POST'])
def suggest_meals():
    """Suggest meals based on nutritional deficiencies, excluding user's allergies"""
    try:
        data = request.get_json()
        deficiencies = data.get('deficiencies', [])
        allergies = data.get('allergies', '').lower()
        
        # Use MealSuggestionService if available
        if meal_service:
            suggestions = meal_service.suggest_meals(deficiencies, allergies)
            return jsonify(suggestions)
        
        # Fallback to original implementation if services not initialized
        if not deficiencies:
            return jsonify([])
        
        deficit_nutrients = set(d['nutrient'].lower() for d in deficiencies)
        
        scored_meals = []
        for template in MEAL_TEMPLATES:
            # Convert MealTemplate to dict format for backward compatibility
            template_dict = template.to_dict() if hasattr(template, 'to_dict') else template
            
            if allergies:
                allergen_keywords = allergies.split(',')
                template_text = json.dumps(template_dict).lower()
                if any(allergen.strip() in template_text for allergen in allergen_keywords):
                    continue
            
            template_nutrients = set(n.lower() for n in template_dict.get('nutrients', []))
            covered = deficit_nutrients.intersection(template_nutrients)
            
            if covered:
                foods = []
                total_nutrients = {
                    'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0,
                    'fiber': 0, 'sugar': 0, 'calcium': 0, 'iron': 0,
                    'magnesium': 0, 'phosphorus': 0, 'potassium': 0,
                    'sodium': 0, 'zinc': 0, 'vitaminA': 0, 'vitaminC': 0,
                    'vitaminD': 0, 'vitaminE': 0, 'vitaminK': 0,
                    'vitaminB6': 0, 'vitaminB12': 0, 'folate': 0, 'niacin': 0
                }
                
                allergen_keywords = []
                if allergies:
                    allergen_keywords = [a.strip() for a in allergies.split(',')]
                
                skip_meal = False 
                
                for food_template in template_dict['foods']:
                    if USE_JSON_DB and json_db:
                        search_results = search_foods_json(food_template['query'])
                    else:
                        search_results = search_foods_sql(food_template['query'])
                    
                    if search_results:
                        food = search_results[0]
                        food_name = food.get('name', '').lower()
                
                        if allergen_keywords and any(allergen in food_name for allergen in allergen_keywords):
                            skip_meal = True
                            break  
                        
                        multiplier = food_template['multiplier']
                
                        foods.append({
                            'id': food['id'],
                            'name': food['name'],
                            'amount': multiplier,
                            'unit': food_template['unit'],
                            'nutrients': {
                                key: safe_float(food.get(key, 0)) * multiplier
                                for key in total_nutrients.keys()
                            }
                        })
                        
                        for key in total_nutrients.keys():
                            total_nutrients[key] += safe_float(food.get(key, 0)) * multiplier
                
                if skip_meal:
                    continue
                
                if foods:
                    scored_meals.append({
                        'id': template_dict['id'],
                        'name': template_dict['name'],
                        'category': template_dict['category'],
                        'foods': foods,
                        'totalNutrients': total_nutrients,
                        'deficitsCovered': len(covered),
                        'score': len(covered)
                    })
        
        scored_meals.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(scored_meals[:8])
        
    except Exception as e:
        print(f"Error in suggest_meals: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print(f"\n{'='*50}")
    print(f"Python Backend Server Starting")
    print(f"{'='*50}")
    print(f"Mode: {'JSON Database' if USE_JSON_DB else 'MySQL Database'}")
    print(f"Port: {PORT}")
    print(f"CORS: Enabled")
    if USE_JSON_DB and json_db:
        print(f"✓ JSON Database Ready")
    elif not USE_JSON_DB:
        print(f"MySQL Config: {MYSQL_CONFIG['user']}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}")
    print(f"{'='*50}\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
