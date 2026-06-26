const fs = require('fs');
const path = require('path');
const StreamArray = require('stream-json/streamers/StreamArray');

const filePath = path.join(__dirname, '../foodNutrientDatabase_trimmed.json');

function safeGet(obj, keys) {
  for (const k of keys) {
    if (obj && Object.prototype.hasOwnProperty.call(obj, k)) return obj[k];
  }
  return undefined;
}

function mapNutrients(item) {
  const out = {
    calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0, sugar: 0,
    calcium: 0, iron: 0, magnesium: 0, phosphorus: 0, potassium: 0, sodium: 0, zinc: 0,
    vitaminA: 0, vitaminC: 0, vitaminD: 0, vitaminE: 0, vitaminK: 0,
    vitaminB6: 0, vitaminB12: 0, folate: 0, niacin: 0
  };

  const nutrients = safeGet(item, ['foodNutrients', 'nutrients', 'nutrient', 'nutrient_values', 'nutrient_values_list']);

  if (Array.isArray(nutrients)) {
    for (const n of nutrients) {
      // USDA FDC: nutrient code is in n.nutrient.number (string like "208", "203", etc.)
      let code = n.nutrient?.number || n.nutrient_code || n.code || n.id || n.nutrientId || n.nutrient;
      if (code) code = String(code); 
      
      const value = Number(n.amount ?? n.value ?? n.nutrient_value ?? n.quantity ?? 0) || 0;
      const nutName = (n.nutrient?.name || n.name || n.nutrient_name || '').toString().toLowerCase();

      // Macronutrients
      if (code === '208' || nutName.includes('energy') && nutName.includes('kcal')) out.calories = value;
      if (code === '203' || nutName.includes('protein')) out.protein = value;
      if (code === '205' || nutName.includes('carbohydrate')) out.carbs = value;
      if (code === '204' || nutName.includes('lipid') || nutName.includes('fat')) out.fat = value;
      if (code === '291' || nutName.includes('fiber')) out.fiber = value;
      if (code === '269' || nutName.includes('sugar')) out.sugar = value;
      
      // Minerals
      if (code === '301' || nutName.includes('calcium')) out.calcium = value;
      if (code === '303' || nutName.includes('iron')) out.iron = value;
      if (code === '304' || nutName.includes('magnesium')) out.magnesium = value;
      if (code === '305' || nutName.includes('phosphorus')) out.phosphorus = value;
      if (code === '306' || nutName.includes('potassium')) out.potassium = value;
      if (code === '307' || nutName.includes('sodium')) out.sodium = value;
      if (code === '309' || nutName.includes('zinc')) out.zinc = value;
      
      // Vitamins
      if (code === '320' || nutName.includes('vitamin a') && nutName.includes('rae')) out.vitaminA = value;
      if (code === '401' || nutName.includes('vitamin c')) out.vitaminC = value;
      if (code === '328' || nutName.includes('vitamin d')) out.vitaminD = value;
      if (code === '323' || nutName.includes('vitamin e') && nutName.includes('tocopherol')) out.vitaminE = value;
      if (code === '430' || nutName.includes('vitamin k')) out.vitaminK = value;
      if (code === '415' || nutName.includes('vitamin b-6')) out.vitaminB6 = value;
      if (code === '418' || nutName.includes('vitamin b-12')) out.vitaminB12 = value;
      if (code === '417' || nutName.includes('folate')) out.folate = value;
      if (code === '406' || nutName.includes('niacin')) out.niacin = value;
    }
  } else if (nutrients && typeof nutrients === 'object') {
    const pick = (keys) => {
      for (const k of keys) if (nutrients[k] != null) return Number(nutrients[k]) || 0;
      return 0;
    };
    out.calories = pick(['calories', 'energy', 'kcal']);
    out.protein = pick(['protein']);
    out.carbs = pick(['carbs', 'carbohydrate', 'carbohydrates']);
    out.fat = pick(['fat', 'fats']);
    out.fiber = pick(['fiber', 'fibre']);
    out.sugar = pick(['sugar']);
    out.calcium = pick(['calcium']);
    out.iron = pick(['iron']);
    out.magnesium = pick(['magnesium']);
    out.phosphorus = pick(['phosphorus']);
    out.potassium = pick(['potassium']);
    out.sodium = pick(['sodium']);
    out.zinc = pick(['zinc']);
    out.vitaminA = pick(['vitamin_a', 'vitaminA']);
    out.vitaminC = pick(['vitamin_c', 'vitaminC']);
    out.vitaminD = pick(['vitamin_d', 'vitaminD']);
    out.vitaminE = pick(['vitamin_e', 'vitaminE']);
    out.vitaminK = pick(['vitamin_k', 'vitaminK']);
    out.vitaminB6 = pick(['vitamin_b6', 'vitaminB6']);
    out.vitaminB12 = pick(['vitamin_b12', 'vitaminB12']);
    out.folate = pick(['folate']);
    out.niacin = pick(['niacin']);
  }

  return out;
}

// Standard measurement options presented to users for every food item.
// Each option includes an approximate `gramsPerUnit` when sensible. Frontend
// can use `gramsPerUnit` to convert the entered numeric amount into grams;
// options without `gramsPerUnit` should be treated as "eyeball" units.
const STANDARD_SERVINGS = [
  { label: 'g', type: 'mass', unit: 'g', gramsPerUnit: 1 },
  { label: 'oz', type: 'mass', unit: 'oz', gramsPerUnit: 28.35 },
  { label: 'cup', type: 'volume', unit: 'cup', gramsPerUnit: 240 },
  { label: 'tbsp', type: 'volume', unit: 'tbsp', gramsPerUnit: 15 },
  { label: 'tsp', type: 'volume', unit: 'tsp', gramsPerUnit: 5 },
  { label: 'bowl', type: 'eyeball', unit: 'bowl', gramsPerUnit: 300 },
  { label: 'piece', type: 'eyeball', unit: 'piece', gramsPerUnit: null }
];

function mapItem(item) {
  const id = safeGet(item, ['fdcId', 'ndbNumber', 'cn_code', 'id', 'code', 'food_id']) || null;
  const name = safeGet(item, ['description', 'descriptor', 'name', 'desc', 'food_name']) || 'Unknown';

  const servingOptions = STANDARD_SERVINGS.map(o => ({ ...o }));
  const defaultServing = { label: 'g', type: 'mass', unit: 'g', gramsPerUnit: 1 };
  const unit = `100 ${defaultServing.label}`;

  const nut = mapNutrients(item);

  return {
    id,
    name,
    unit,
    servingOptions,
    calories: nut.calories,
    protein: nut.protein,
    carbs: nut.carbs,
    fat: nut.fat,
    fiber: nut.fiber,
    sugar: nut.sugar,
    calcium: nut.calcium,
    iron: nut.iron,
    magnesium: nut.magnesium,
    phosphorus: nut.phosphorus,
    potassium: nut.potassium,
    sodium: nut.sodium,
    zinc: nut.zinc,
    vitaminA: nut.vitaminA,  
    vitaminC: nut.vitaminC,      
    vitaminD: nut.vitaminD,      
    vitaminE: nut.vitaminE,      
    vitaminK: nut.vitaminK,      
    vitaminB6: nut.vitaminB6,    
    vitaminB12: nut.vitaminB12,  
    folate: nut.folate,          
    niacin: nut.niacin           
  };
}

function streamFind(limit = 100) {
  return new Promise((resolve, reject) => {
    const results = [];
    const stream = fs.createReadStream(filePath).pipe(StreamArray.withParser());

    stream.on('data', ({key, value}) => {
      results.push(mapItem(value));
      if (results.length >= limit) {
        stream.destroy();
        resolve(results);
      }
    });

    stream.on('end', () => resolve(results));
    stream.on('error', (err) => {
      if (err && /top[- ]level object should be an array/i.test(err.message)) {
        try {
          const data = fs.readFileSync(filePath, 'utf8');
          const parsed = JSON.parse(data);
          let arr = null;
          if (Array.isArray(parsed)) arr = parsed;
          else if (parsed && typeof parsed === 'object') {
            for (const k of Object.keys(parsed)) {
              if (Array.isArray(parsed[k])) {
                arr = parsed[k];
                break;
              }
            }
          }

          if (!arr) return reject(new Error('No array found inside JSON top-level object'));

          const sliced = arr.slice(0, limit).map(mapItem);
          return resolve(sliced);
        } catch (e) {
          return reject(e);
        }
      }
      return reject(err);
    });
  });
}

function streamSearch(query, limit = 50) {
  return new Promise((resolve, reject) => {
    const normalize = (s) => (s || '').toString().toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
    const q = normalize(query);
    const tokens = q.split(/\s+/).filter(Boolean);
    const results = [];
    const stream = fs.createReadStream(filePath).pipe(StreamArray.withParser());

    stream.on('data', ({key, value}) => {
      const nameRaw = (safeGet(value, ['description','descriptor','name','desc','food_name']) || '').toString();
      const name = normalize(nameRaw);
      const ok = tokens.length === 0 ? false : tokens.every(t => name.includes(t));
      if (ok) results.push(mapItem(value));
      if (results.length >= limit) {
        stream.destroy();
        resolve(results);
      }
    });

    stream.on('end', () => {
      try {
        const data = fs.readFileSync(filePath, 'utf8');
        const parsed = JSON.parse(data);
        let arr = null;
        if (Array.isArray(parsed)) arr = parsed;
        else if (parsed && typeof parsed === 'object') {
          for (const k of Object.keys(parsed)) {
            if (Array.isArray(parsed[k])) {
              arr = parsed[k];
              break;
            }
          }
        }

        if (!arr) {
          return resolve(results);
        }

        for (const value of arr) {
          const name = normalize(safeGet(value, ['description','descriptor','name','desc','food_name']) || '');
          if (tokens.length > 0 && tokens.every(t => name.includes(t))) {
            results.push(mapItem(value));
            if (results.length >= limit) break;
          }
        }
        return resolve(results);
      } catch (e) {
        return resolve(results);
      }
    });

    stream.on('error', (err) => {
      if (err && /top[- ]level object should be an array/i.test(err.message)) {
        try {
          const data = fs.readFileSync(filePath, 'utf8');
          const parsed = JSON.parse(data);
          let arr = null;
          if (Array.isArray(parsed)) arr = parsed;
          else if (parsed && typeof parsed === 'object') {
            for (const k of Object.keys(parsed)) {
              if (Array.isArray(parsed[k])) {
                arr = parsed[k];
                break;
              }
            }
          }

          if (!arr) return reject(new Error('No array found inside JSON top-level object'));

          for (const value of arr) {
            const name = normalize(safeGet(value, ['description','descriptor','name','desc','food_name']) || '');
            if (tokens.length > 0 && tokens.every(t => name.includes(t))) {
              results.push(mapItem(value));
              if (results.length >= limit) break;
            }
          }

          return resolve(results);
        } catch (e) {
          return reject(e);
        }
      }
      return reject(err);
    });
  });
}

module.exports = { streamFind, streamSearch, mapItem };
