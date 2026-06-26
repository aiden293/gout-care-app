# ATE! Nutrition Tracking App

A comprehensive nutrition tracking application with real-time food search, meal logging, weekly analytics, and personalized recommendations.

## Getting Started

This application uses a **Python/Flask backend** and **React frontend**.

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

### 1. Backend Setup (Python/Flask)

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Run the Backend
```bash
cd backend
python3 server.py
```

The backend will start on **http://localhost:5001**

**Note:** The Python backend uses the USDA FoodData Central database (`usda_foods.json`) with 7,327+ foods.

### 2. Frontend Setup (React)

#### Install Node Dependencies
```bash
# From the root directory
npm install
```

#### Run the Frontend
```bash
npm start
```

The app will open at **http://localhost:3000**

## Project Structure

```
ATE-_Nutrition_Tracking_App/
├── backend/
│   ├── server.py              # Python Flask API server
│   ├── json_db.py            # JSON database handler
│   ├── requirements.txt       # Python dependencies
│   └── usda_foods.json       # Food nutrition database
├── src/
│   └── App.js                # React frontend application
└── public/
    └── index.html            # HTML template
```

## Testing

### Run Backend Tests

The backend has comprehensive unit tests with **91% code coverage**.

#### Install Test Dependencies
```bash
cd backend
pip install pytest pytest-cov
```

#### Run All Tests
```bash
cd backend
pytest
```

#### Run Tests with Coverage Report
```bash
cd backend
pytest --cov=. --cov-report=term-missing .
```

**Note:** The `.coveragerc` file in the `backend` directory configures coverage to exclude test files, ensuring cross-platform compatibility (Windows, macOS, Linux).

**Expected Output:**
```
============================= 172 passed in 1.23s =============================
Name                                        Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------
json_db.py                                    103      4   96%   222-224, 228
models/__init__.py                              0      0  100%
models/food.py                                 70      0  100%
models/meal_template.py                        42      0  100%
models/nutrient.py                             58      0  100%
server.py                                     182     43   76%   54-58, 287-328, ...
services/__init__.py                            0      0  100%
services/food_service.py                       28      0  100%
services/meal_suggestion_service.py            74      2   98%   98-99
-------------------------------------------------------------------------
TOTAL                                         557     49   91%
```

#### Test Coverage Summary
- **Overall: 91% coverage** (508/557 statements)
- **json_db.py: 96% coverage** (99/103 statements)
- **models: 100% coverage** (170/170 statements)
- **services: 99% coverage** (101/102 statements)
- **server.py: 76% coverage** (139/182 statements)
- **172 tests passing** covering:
  - Flask API endpoints (GET/POST)
  - JSON database operations
  - SQL database fallback
  - OOP models (Food, Nutrient, MealTemplate)
  - Service layer (FoodService, MealSuggestionService)
  - Integration tests with real database
  - Meal suggestion algorithm
  - Nutrient calculations
  - Error handling

## Running in Production

### Build Frontend
```bash
npm run build
```

### Run Backend
```bash
cd backend
python3 server.py
```
