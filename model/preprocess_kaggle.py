import pandas as pd
import numpy as np
import re
import os

print("Starting Kaggle dataset preprocessing...")

INPUT_FILE = os.path.join("data", "kaggle_real_estate.csv")
OUTPUT_FILE = os.path.join("data", "house_data.csv")

if not os.path.exists(INPUT_FILE):
    print(f"Error: {INPUT_FILE} not found!")
    exit(1)

df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} rows from raw dataset.")

# 1. Price
def parse_price(val):
    if pd.isna(val): return np.nan
    val = str(val).upper().replace('₹', '').replace(',', '').strip()
    try:
        if 'CR' in val:
            num = float(re.sub(r'[^\d.]', '', val))
            return int(num * 10000000)
        elif 'L' in val:
            num = float(re.sub(r'[^\d.]', '', val))
            return int(num * 100000)
        else:
            num = float(re.sub(r'[^\d.]', '', val))
            return int(num)
    except:
        return np.nan

df['price'] = df['Price'].apply(parse_price)

# 2. Location -> city, locality
def parse_location(val):
    if pd.isna(val): return 'Unknown', 'Unknown'
    parts = str(val).split(',')
    if len(parts) >= 2:
        city = parts[-1].strip()
        locality = ','.join(parts[:-1]).strip()
        return city, locality
    return 'Unknown', str(val).strip()

df[['city', 'locality']] = df.apply(lambda row: pd.Series(parse_location(row['Location'])), axis=1)

# 3. Area and Bathrooms
df['area'] = df['Total_Area'].fillna(0).astype(int)
df['bathrooms'] = df['Baths'].fillna(1).astype(int)

# 4. Bedrooms
def extract_bedrooms(title):
    if pd.isna(title): return 2
    match = re.search(r'(\d+)\s*BHK', str(title), re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 2 # default

df['bedrooms'] = df['Property Title'].apply(extract_bedrooms)

# 5. Property Type
def extract_prop_type(title):
    if pd.isna(title): return 'Apartment'
    title = str(title).lower()
    if 'villa' in title: return 'Villa'
    if 'house' in title: return 'Independent House'
    if 'builder' in title or 'floor' in title: return 'Builder Floor'
    if 'penthouse' in title: return 'Penthouse'
    return 'Apartment'

df['property_type'] = df['Property Title'].apply(extract_prop_type)

# 6. Age and Floor and Furnishing (from Description)
def parse_description(desc):
    if pd.isna(desc): return 5, 0, 'Unfurnished'
    desc = str(desc).lower()
    
    # Age
    age = 5
    age_match = re.search(r'(\d+)\s*(to\s*\d+\s*)?years?\s*old', desc)
    if age_match:
        age = int(age_match.group(1))
        
    # Floor
    floor = 0
    floor_match = re.search(r'(floor\s*|on\s*)(\d+)', desc)
    if floor_match:
        floor = int(floor_match.group(2))
        
    # Furnishing
    furnishing = 'Unfurnished'
    if 'fully furnished' in desc or 'fully-furnished' in desc:
        furnishing = 'Fully Furnished'
    elif 'semi-furnished' in desc or 'semi furnished' in desc:
        furnishing = 'Semi-Furnished'
    elif 'furnished' in desc:
        furnishing = 'Furnished'
        
    return age, floor, furnishing

df[['age', 'floor', 'furnishing']] = df.apply(lambda row: pd.Series(parse_description(row['Description'])), axis=1)

# 7. Amenities
amenity_keywords = {
    'parking': ['parking', 'car park', 'garage'],
    'pool': ['pool', 'swimming'],
    'garden': ['garden', 'park'],
    'gym': ['gym', 'fitness'],
    'security': ['security', 'guard', 'cctv'],
    'lift': ['lift', 'elevator'],
    'power_backup': ['power backup', 'generator'],
    'modular_kitchen': ['modular kitchen'],
    'clubhouse': ['clubhouse', 'club house'],
    'children_play': ['play area', 'kids', 'children'],
    'jogging_track': ['jogging', 'track'],
    'sports_court': ['court', 'sports', 'tennis', 'badminton'],
    'rainwater_harvesting': ['rainwater', 'rain water'],
    'solar_panels': ['solar'],
    'smart_home': ['smart'],
    'servant_room': ['servant', 'maid']
}

for col, keywords in amenity_keywords.items():
    df[col] = df['Description'].apply(lambda d: 1 if not pd.isna(d) and any(k in str(d).lower() for k in keywords) else 0)

# Filter out invalid rows (missing price or area)
df = df.dropna(subset=['price', 'area'])
df = df[df['price'] > 0]
df = df[df['area'] > 100]

# Filter rare cities (keep top ones)
city_counts = df['city'].value_counts()
top_cities = city_counts[city_counts >= 50].index.tolist()
df = df[df['city'].isin(top_cities)]

# Filter rare localities to prevent dimensionality explosion in One-Hot Encoding
def filter_localities(group):
    loc_counts = group['locality'].value_counts()
    top_locs = loc_counts.head(20).index.tolist() # Keep top 20 localities per city
    group['locality'] = group['locality'].apply(lambda x: x if x in top_locs else 'Other')
    return group

df = df.groupby('city', group_keys=False).apply(filter_localities)

final_cols = [
    'city', 'locality', 'property_type', 'area', 'bedrooms', 'bathrooms', 
    'furnishing', 'age', 'floor', 'parking', 'pool', 'garden', 'gym', 
    'security', 'lift', 'power_backup', 'modular_kitchen', 'clubhouse', 
    'children_play', 'jogging_track', 'sports_court', 'rainwater_harvesting', 
    'solar_panels', 'smart_home', 'servant_room', 'price'
]

df_final = df[final_cols].copy()
df_final.to_csv(OUTPUT_FILE, index=False)

print(f"Successfully processed and saved {len(df_final)} rows to {OUTPUT_FILE}.")
