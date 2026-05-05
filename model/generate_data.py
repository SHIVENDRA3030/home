"""
Generate a realistic synthetic Indian house price dataset (Enhanced v2).
- 10,000 records across 8 cities, 80+ localities
- Realistic price distributions with market-correlated noise
- Non-linear feature interactions (area×location, age² depreciation, etc.)
"""

import csv
import random
import math
import os

random.seed(42)
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'house_data.csv')

# ── City + locality base pricing (₹/sqft) ─────────────────────
# Prices reflect 2024-25 Indian real estate market ranges
CITIES = {
    'Mumbai': {
        'Andheri': 22000, 'Bandra': 35000, 'Borivali': 16000, 'Dadar': 28000,
        'Goregaon': 18000, 'Juhu': 40000, 'Malad': 15000, 'Powai': 25000,
        'Thane': 13000, 'Navi Mumbai': 12000
    },
    'Delhi': {
        'Dwarka': 14000, 'Rohini': 11000, 'Saket': 20000, 'Vasant Kunj': 22000,
        'Connaught Place': 38000, 'Nehru Place': 16000, 'Janakpuri': 13000,
        'Lajpat Nagar': 18000, 'Karol Bagh': 17000, 'Greater Kailash': 25000
    },
    'Bangalore': {
        'Whitefield': 8500, 'Koramangala': 14000, 'HSR Layout': 12000,
        'Indiranagar': 16000, 'Electronic City': 7000, 'JP Nagar': 9000,
        'Hebbal': 10000, 'Marathahalli': 8000, 'Sarjapur': 7500, 'MG Road': 20000
    },
    'Hyderabad': {
        'Gachibowli': 8000, 'HITEC City': 9000, 'Banjara Hills': 14000,
        'Jubilee Hills': 15000, 'Kondapur': 7500, 'Madhapur': 8500,
        'Secunderabad': 9000, 'Kukatpally': 7000, 'Miyapur': 6500, 'Begumpet': 10000
    },
    'Chennai': {
        'Adyar': 13000, 'Anna Nagar': 12000, 'T Nagar': 16000,
        'Velachery': 9000, 'OMR': 8000, 'Porur': 7500,
        'Mylapore': 15000, 'Nungambakkam': 18000, 'Chromepet': 6500, 'Tambaram': 6000
    },
    'Pune': {
        'Hinjewadi': 8000, 'Kothrud': 11000, 'Viman Nagar': 10000,
        'Baner': 9500, 'Wakad': 8000, 'Hadapsar': 7500,
        'Koregaon Park': 15000, 'Aundh': 11000, 'Kharadi': 8500, 'Shivaji Nagar': 13000
    },
    'Kolkata': {
        'Salt Lake': 7000, 'New Town': 6500, 'Park Street': 14000,
        'Ballygunge': 12000, 'Howrah': 5000, 'Dum Dum': 5500,
        'Garia': 5000, 'Behala': 5500, 'EM Bypass': 7500, 'Alipore': 13000
    },
    'Ahmedabad': {
        'SG Highway': 7000, 'Satellite': 8000, 'Vastrapur': 7500,
        'Bopal': 6000, 'Thaltej': 7500, 'Prahlad Nagar': 8500,
        'CG Road': 10000, 'Navrangpura': 9000, 'Gota': 5500, 'Chandkheda': 5000
    }
}

# ── Property type configs ──────────────────────────────────────
PROPERTY_TYPES = {
    'Apartment': {'size_range': (500, 2500), 'mult': 1.0, 'weight': 0.45},
    'Villa': {'size_range': (1500, 5000), 'mult': 1.4, 'weight': 0.10},
    'Independent House': {'size_range': (800, 3500), 'mult': 1.2, 'weight': 0.15},
    'Penthouse': {'size_range': (2000, 5000), 'mult': 1.8, 'weight': 0.05},
    'Studio': {'size_range': (300, 800), 'mult': 0.7, 'weight': 0.25},
}

FURNISHING = ['Unfurnished', 'Semi-Furnished', 'Fully-Furnished']
FURNISH_WEIGHTS = [0.40, 0.35, 0.25]
FURNISH_MULT = {'Unfurnished': 1.0, 'Semi-Furnished': 1.12, 'Fully-Furnished': 1.25}

# ── Amenity bonuses (₹) — correlated with property type ──────
AMENITIES = {
    'parking': 250000,
    'pool': 800000,
    'garden': 200000,
    'gym': 400000,
    'security': 300000,
    'lift': 350000,
    'power_backup': 250000,
    'modular_kitchen': 300000,
    'clubhouse': 500000,
    'children_play': 200000,
    'jogging_track': 150000,
    'sports_court': 400000,
    'rainwater_harvesting': 100000,
    'solar_panels': 350000,
    'smart_home': 600000,
    'servant_room': 400000,
}

# Amenity probability by property type (more realistic)
AMENITY_PROBS = {
    'Studio': {'parking': 0.3, 'pool': 0.05, 'garden': 0.02, 'gym': 0.4, 'security': 0.5,
               'lift': 0.6, 'power_backup': 0.3, 'modular_kitchen': 0.3, 'clubhouse': 0.1,
               'children_play': 0.05, 'jogging_track': 0.05, 'sports_court': 0.02,
               'rainwater_harvesting': 0.1, 'solar_panels': 0.05, 'smart_home': 0.15, 'servant_room': 0.02},
    'Apartment': {'parking': 0.7, 'pool': 0.2, 'garden': 0.15, 'gym': 0.45, 'security': 0.7,
                  'lift': 0.8, 'power_backup': 0.5, 'modular_kitchen': 0.4, 'clubhouse': 0.3,
                  'children_play': 0.35, 'jogging_track': 0.25, 'sports_court': 0.15,
                  'rainwater_harvesting': 0.2, 'solar_panels': 0.1, 'smart_home': 0.2, 'servant_room': 0.15},
    'Independent House': {'parking': 0.85, 'pool': 0.1, 'garden': 0.6, 'gym': 0.15, 'security': 0.5,
                          'lift': 0.05, 'power_backup': 0.6, 'modular_kitchen': 0.5, 'clubhouse': 0.05,
                          'children_play': 0.1, 'jogging_track': 0.05, 'sports_court': 0.1,
                          'rainwater_harvesting': 0.3, 'solar_panels': 0.25, 'smart_home': 0.15, 'servant_room': 0.4},
    'Villa': {'parking': 0.9, 'pool': 0.5, 'garden': 0.7, 'gym': 0.4, 'security': 0.8,
              'lift': 0.1, 'power_backup': 0.7, 'modular_kitchen': 0.65, 'clubhouse': 0.3,
              'children_play': 0.4, 'jogging_track': 0.3, 'sports_court': 0.3,
              'rainwater_harvesting': 0.35, 'solar_panels': 0.3, 'smart_home': 0.4, 'servant_room': 0.6},
    'Penthouse': {'parking': 0.95, 'pool': 0.6, 'garden': 0.2, 'gym': 0.6, 'security': 0.9,
                  'lift': 0.95, 'power_backup': 0.7, 'modular_kitchen': 0.8, 'clubhouse': 0.5,
                  'children_play': 0.2, 'jogging_track': 0.2, 'sports_court': 0.15,
                  'rainwater_harvesting': 0.15, 'solar_panels': 0.2, 'smart_home': 0.6, 'servant_room': 0.5},
}

# ── Bedroom distribution by area range ─────────────────────────
def realistic_bedrooms(area, prop_type):
    """Bedrooms correlated with area (more realistic)."""
    if prop_type == 'Studio':
        return 1
    if area < 600:
        return random.choices([1, 2], weights=[0.7, 0.3])[0]
    elif area < 900:
        return random.choices([1, 2, 3], weights=[0.15, 0.6, 0.25])[0]
    elif area < 1200:
        return random.choices([2, 3], weights=[0.4, 0.6])[0]
    elif area < 1600:
        return random.choices([2, 3, 4], weights=[0.15, 0.6, 0.25])[0]
    elif area < 2200:
        return random.choices([3, 4], weights=[0.55, 0.45])[0]
    elif area < 3000:
        return random.choices([3, 4, 5], weights=[0.2, 0.55, 0.25])[0]
    else:
        return random.choices([4, 5, 6], weights=[0.3, 0.5, 0.2])[0]


def realistic_bathrooms(bedrooms):
    """Bathrooms ≤ bedrooms, usually 1-2 less."""
    if bedrooms <= 1:
        return 1
    elif bedrooms <= 3:
        return random.choices([1, 2], weights=[0.3, 0.7])[0]
    else:
        return random.choices([2, 3, 4], weights=[0.3, 0.5, 0.2])[0]


def realistic_floor(prop_type, age):
    """Floor distribution depends on property type and age."""
    if prop_type in ['Villa', 'Independent House']:
        return 0  # Ground floor
    if prop_type == 'Penthouse':
        return random.randint(15, 40)
    # Apartments — newer buildings tend to be taller
    max_floor = min(10 + age * -0.3 + 20, 40) if age < 20 else random.randint(5, 25)
    return random.randint(0, max(1, int(max_floor)))


def market_noise(base_price, city, locality):
    """Realistic market noise — not uniform ±8%, but fat-tailed.
    Premium localities have more volatile pricing."""
    premium = CITIES[city][locality] / 10000
    volatility = 0.04 + premium * 0.008  # 4-12% volatility
    # Use Box-Muller for gaussian noise
    u1, u2 = random.random(), random.random()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    noise = 1.0 + z * volatility
    return max(0.80, min(1.25, noise))  # Cap at ±20-25%


# ── Generate rows ──────────────────────────────────────────────
ROWS = 10000
rows = []

# Weighted city selection (Mumbai/Delhi/Bangalore have more listings)
city_weights = {
    'Mumbai': 0.18, 'Delhi': 0.16, 'Bangalore': 0.16, 'Hyderabad': 0.13,
    'Chennai': 0.10, 'Pune': 0.12, 'Kolkata': 0.08, 'Ahmedabad': 0.07
}
cities_list = list(city_weights.keys())
cities_weights = list(city_weights.values())

prop_types_list = list(PROPERTY_TYPES.keys())
prop_weights = [PROPERTY_TYPES[p]['weight'] for p in prop_types_list]

for _ in range(ROWS):
    # City (weighted by market size)
    city = random.choices(cities_list, weights=cities_weights)[0]
    locality = random.choice(list(CITIES[city].keys()))
    base_price_per_sqft = CITIES[city][locality]

    # Property type (weighted)
    prop_type = random.choices(prop_types_list, weights=prop_weights)[0]
    prop_info = PROPERTY_TYPES[prop_type]

    # Area (gaussian within range, not uniform)
    a_min, a_max = prop_info['size_range']
    a_mid = (a_min + a_max) / 2
    a_std = (a_max - a_min) / 4
    area = int(max(a_min, min(a_max, random.gauss(a_mid, a_std))))

    # Bedrooms/bathrooms correlated with area
    bedrooms = realistic_bedrooms(area, prop_type)
    bathrooms = realistic_bathrooms(bedrooms)

    # Furnishing (weighted — cheaper properties tend to be unfurnished)
    furnishing = random.choices(FURNISHING, weights=FURNISH_WEIGHTS)[0]

    # Age (exponential — more newer properties, fewer old ones)
    age = int(min(35, random.expovariate(1 / 8)))

    # Floor
    floor_num = realistic_floor(prop_type, age)

    # Amenities (correlated with property type, not uniform 40%)
    amenity_probs = AMENITY_PROBS[prop_type]
    amenities = {}
    for k, prob in amenity_probs.items():
        # Premium properties get more amenities
        furn_bonus = 0.1 if furnishing == 'Fully-Furnished' else 0
        age_penalty = -0.05 if age > 20 else 0
        adjusted_prob = min(0.95, max(0.02, prob + furn_bonus + age_penalty))
        amenities[k] = 1 if random.random() < adjusted_prob else 0

    # ── Price calculation (multi-factor, non-linear) ──────────
    # Base price from area × locality rate
    price = area * base_price_per_sqft

    # Property type modifier
    price *= prop_info['mult']

    # Furnishing (compounds with area — bigger furnishing delta for larger homes)
    furn_mult = FURNISH_MULT[furnishing]
    price *= furn_mult

    # Bedrooms — diminishing returns per additional bedroom
    bedroom_bonus = sum(150000 * (0.85 ** i) for i in range(bedrooms))
    price += bedroom_bonus

    # Bathrooms
    price += bathrooms * 80000

    # Age depreciation — non-linear (steeper in first 5 years)
    if age <= 5:
        age_factor = 1.0 - (age * 0.02)
    elif age <= 15:
        age_factor = 0.90 - ((age - 5) * 0.01)
    else:
        age_factor = max(0.65, 0.80 - ((age - 15) * 0.008))
    price *= age_factor

    # Floor premium (apartments/penthouses only — diminishing above 20th floor)
    if prop_type in ['Apartment', 'Penthouse']:
        if floor_num <= 20:
            floor_bonus = floor_num * 15000
        else:
            floor_bonus = 20 * 15000 + (floor_num - 20) * 5000
        price += min(floor_bonus, 400000)

    # Amenity bonuses (with interaction: smart_home + modular_kitchen = synergy)
    amenity_count = 0
    for amenity, active in amenities.items():
        if active:
            price += AMENITIES[amenity]
            amenity_count += 1
    # Synergy bonus: smart home + modular kitchen together are worth more
    if amenities.get('smart_home') and amenities.get('modular_kitchen'):
        price += 150000

    # Market noise (gaussian, not uniform)
    noise = market_noise(price, city, locality)
    price = int(price * noise)

    # Ensure minimum price
    price = max(500000, price)

    row = {
        'city': city, 'locality': locality, 'property_type': prop_type,
        'area': area, 'bedrooms': bedrooms, 'bathrooms': bathrooms,
        'furnishing': furnishing, 'age': age, 'floor': floor_num,
        **amenities, 'price': price
    }
    rows.append(row)

# Write CSV
fieldnames = list(rows[0].keys())
with open(output_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {ROWS} rows -> {output_path}")
print(f"   Cities: {len(CITIES)} | Localities: {sum(len(v) for v in CITIES.values())}")
print(f"   Property types: {len(PROPERTY_TYPES)} | Amenities: {len(AMENITIES)}")
print(f"   Columns: {len(fieldnames)}")

# Quick stats
import pandas as pd
df = pd.DataFrame(rows)
print(f"\n── Price Stats ──")
print(f"   Min:    ₹{df['price'].min():>12,}")
print(f"   Median: ₹{df['price'].median():>12,.0f}")
print(f"   Mean:   ₹{df['price'].mean():>12,.0f}")
print(f"   Max:    ₹{df['price'].max():>12,}")
print(f"\n── Per City (median ₹/sqft) ──")
for city in sorted(CITIES.keys()):
    cdf = df[df['city'] == city]
    med = (cdf['price'] / cdf['area']).median()
    print(f"   {city:12s}: {med:>8,.0f}  ({len(cdf)} listings)")
