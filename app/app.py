"""
Flask backend for HomeValue AI — v2 (Production-ready).
- Graceful model loading with fallback
- CORS support
- Rate limiting
- Prediction intervals via quantile regression
- Proper error handling and logging
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import joblib
import numpy as np
import pandas as pd

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')

# ── App setup ─────────────────────────────────────────────────
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute", "10 per second"],
    storage_uri="memory://",
)

# ── Model loading with graceful fallback ──────────────────────
model = None
quantile_low = None
quantile_high = None
encoders = None
feature_cols = None
model_loaded = False
training_report = None


def load_models():
    """Load ML models with graceful error handling."""
    global model, quantile_low, quantile_high, encoders, feature_cols, model_loaded, training_report

    try:
        model_path = os.path.join(MODEL_DIR, 'house_model.pkl')
        encoders_path = os.path.join(MODEL_DIR, 'encoders.pkl')
        features_path = os.path.join(MODEL_DIR, 'feature_cols.pkl')
        q10_path = os.path.join(MODEL_DIR, 'quantile_10.pkl')
        q90_path = os.path.join(MODEL_DIR, 'quantile_90.pkl')
        report_path = os.path.join(REPORT_DIR, 'training_report.json')

        # Check required files
        for path, name in [
            (model_path, 'house_model.pkl'),
            (encoders_path, 'encoders.pkl'),
            (features_path, 'feature_cols.pkl'),
        ]:
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Missing model file: {name}. "
                    f"Run `python model/train.py` first."
                )

        model = joblib.load(model_path)
        encoders = joblib.load(encoders_path)
        feature_cols = joblib.load(features_path)

        # Quantile models are optional (graceful degradation)
        if os.path.exists(q10_path) and os.path.exists(q90_path):
            quantile_low = joblib.load(q10_path)
            quantile_high = joblib.load(q90_path)
            logger.info("✅ Quantile models loaded (prediction intervals available)")
        else:
            logger.warning("⚠️  Quantile models not found — using ±10% fallback for intervals")

        # Training report (optional)
        if os.path.exists(report_path):
            import json
            with open(report_path) as f:
                training_report = json.load(f)

        model_loaded = True
        logger.info(f"✅ Models loaded successfully")
        logger.info(f"   Features: {len(feature_cols)}")
        logger.info(f"   Cities: {len(encoders['city'].classes_)}")
        logger.info(f"   Localities: {len(encoders['locality'].classes_)}")

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        model_loaded = False
    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}")
        model_loaded = False


load_models()

# ── City data ─────────────────────────────────────────────────
CITIES = {
    'Mumbai': ['Andheri', 'Bandra', 'Borivali', 'Dadar', 'Goregaon', 'Juhu', 'Malad', 'Powai', 'Thane', 'Navi Mumbai'],
    'Delhi': ['Dwarka', 'Rohini', 'Saket', 'Vasant Kunj', 'Connaught Place', 'Nehru Place', 'Janakpuri', 'Lajpat Nagar', 'Karol Bagh', 'Greater Kailash'],
    'Bangalore': ['Whitefield', 'Koramangala', 'HSR Layout', 'Indiranagar', 'Electronic City', 'JP Nagar', 'Hebbal', 'Marathahalli', 'Sarjapur', 'MG Road'],
    'Hyderabad': ['Gachibowli', 'HITEC City', 'Banjara Hills', 'Jubilee Hills', 'Kondapur', 'Madhapur', 'Secunderabad', 'Kukatpally', 'Miyapur', 'Begumpet'],
    'Chennai': ['Adyar', 'Anna Nagar', 'T Nagar', 'Velachery', 'OMR', 'Porur', 'Mylapore', 'Nungambakkam', 'Chromepet', 'Tambaram'],
    'Pune': ['Hinjewadi', 'Kothrud', 'Viman Nagar', 'Baner', 'Wakad', 'Hadapsar', 'Koregaon Park', 'Aundh', 'Kharadi', 'Shivaji Nagar'],
    'Kolkata': ['Salt Lake', 'New Town', 'Park Street', 'Ballygunge', 'Howrah', 'Dum Dum', 'Garia', 'Behala', 'EM Bypass', 'Alipore'],
    'Ahmedabad': ['SG Highway', 'Satellite', 'Vastrapur', 'Bopal', 'Thaltej', 'Prahlad Nagar', 'CG Road', 'Navrangpura', 'Gota', 'Chandkheda'],
}

PROPERTY_TYPES = ['Apartment', 'Villa', 'Independent House', 'Penthouse', 'Studio']
FURNISHING_OPTIONS = ['Unfurnished', 'Semi-Furnished', 'Fully-Furnished']

AMENITY_LIST = [
    'parking', 'pool', 'garden', 'gym', 'security', 'lift',
    'power_backup', 'modular_kitchen', 'clubhouse', 'children_play',
    'jogging_track', 'sports_court', 'rainwater_harvesting',
    'solar_panels', 'smart_home', 'servant_room'
]

LUXURY_LABELS = {
    0: 'Basic', 1: 'Basic', 2: 'Comfortable', 3: 'Comfortable',
    4: 'Standard', 5: 'Standard', 6: 'Standard',
    7: 'Premium', 8: 'Premium', 9: 'Premium', 10: 'Premium',
    11: 'Luxury', 12: 'Luxury', 13: 'Elite', 14: 'Elite', 15: 'Elite', 16: 'Ultra Luxury'
}

LUXURY_EMOJIS = {
    'Basic': '🏠', 'Comfortable': '🏡', 'Standard': '🏘️',
    'Premium': '🏅', 'Luxury': '💎', 'Elite': '👑', 'Ultra Luxury': '🌟'
}


# ── API Routes ────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve React frontend (built files in static/)."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'model_loaded': model_loaded,
        'features': len(feature_cols) if feature_cols else 0,
    })


@app.route('/api/config')
@limiter.limit("30 per minute")
def get_config():
    """Return frontend configuration."""
    return jsonify({
        'cities': CITIES,
        'property_types': PROPERTY_TYPES,
        'furnishing_options': FURNISHING_OPTIONS,
        'amenities': AMENITY_LIST,
        'model_loaded': model_loaded,
    })


@app.route('/api/model-info')
@limiter.limit("10 per minute")
def model_info():
    """Return training report and model metadata."""
    if training_report:
        return jsonify(training_report)
    return jsonify({'error': 'Training report not available'}), 404


@app.route('/api/predict', methods=['POST'])
@limiter.limit("20 per minute")
def predict():
    """Predict house price with confidence intervals."""
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded. Run `python model/train.py` to train.',
            'code': 'MODEL_NOT_LOADED',
        }), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        # ── Extract & validate fields ────────────────────────
        city = data.get('city', '').strip()
        locality = data.get('locality', '').strip()
        property_type = data.get('property_type', '').strip()
        furnishing = data.get('furnishing', '').strip()

        # Numeric fields with validation
        try:
            area = int(data.get('area', 0))
            bedrooms = int(data.get('bedrooms', 3))
            bathrooms = int(data.get('bathrooms', 2))
            age = int(data.get('age', 0))
            floor_num = int(data.get('floor', 0))
        except (ValueError, TypeError):
            return jsonify({'error': 'Numeric fields must be valid integers'}), 400

        # Validation
        errors = []
        if not city:
            errors.append('City is required')
        elif city not in CITIES:
            errors.append(f'Invalid city: {city}. Valid: {", ".join(CITIES.keys())}')

        if not locality:
            errors.append('Locality is required')
        elif city in CITIES and locality not in CITIES[city]:
            errors.append(f'Invalid locality for {city}')

        if not property_type:
            errors.append('Property type is required')
        elif property_type not in PROPERTY_TYPES:
            errors.append(f'Invalid property type')

        if not furnishing:
            errors.append('Furnishing is required')
        elif furnishing not in FURNISHING_OPTIONS:
            errors.append(f'Invalid furnishing option')

        if area < 100 or area > 10000:
            errors.append('Area must be between 100 and 10,000 sqft')

        if bedrooms < 1 or bedrooms > 6:
            errors.append('Bedrooms must be 1-6')

        if bathrooms < 1 or bathrooms > 4:
            errors.append('Bathrooms must be 1-4')

        if age < 0 or age > 50:
            errors.append('Property age must be 0-50 years')

        if floor_num < 0 or floor_num > 50:
            errors.append('Floor must be 0-50')

        if errors:
            return jsonify({'error': '; '.join(errors), 'code': 'VALIDATION_ERROR'}), 400

        # ── Encode categoricals ──────────────────────────────
        city_enc = encoders['city'].transform([city])[0]
        try:
            locality_enc = encoders['locality'].transform([locality])[0]
        except ValueError:
            locality_enc = 0  # Unseen locality — graceful fallback
        prop_enc = encoders['property_type'].transform([property_type])[0]
        furn_enc = encoders['furnishing'].transform([furnishing])[0]

        # ── Amenity flags ────────────────────────────────────
        amenities = {}
        for amenity in AMENITY_LIST:
            amenities[amenity] = 1 if data.get(amenity, 0) else 0

        amenity_count = sum(amenities.values())
        bed_bath_ratio = bedrooms / max(bathrooms, 1)
        area_per_bedroom = area / max(bedrooms, 1)

        # ── Build feature row ────────────────────────────────
        row = {
            'city_encoded': city_enc,
            'locality_encoded': locality_enc,
            'property_type_encoded': prop_enc,
            'area': area,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'furnishing_encoded': furn_enc,
            'age': age,
            'floor': floor_num,
            **amenities,
            'amenity_count': amenity_count,
            'bed_bath_ratio': bed_bath_ratio,
            'area_per_bedroom': area_per_bedroom,
        }

        features_df = pd.DataFrame([[row[c] for c in feature_cols]], columns=feature_cols)

        # ── Predict ──────────────────────────────────────────
        predicted_price = max(0, int(model.predict(features_df)[0]))

        # ── Prediction intervals ─────────────────────────────
        if quantile_low and quantile_high:
            price_low = max(0, int(quantile_low.predict(features_df)[0]))
            price_high = max(0, int(quantile_high.predict(features_df)[0]))
        else:
            # Fallback: ±10%
            price_low = int(predicted_price * 0.90)
            price_high = int(predicted_price * 1.10)

        # Ensure low < predicted < high
        price_low = min(price_low, predicted_price)
        price_high = max(price_high, predicted_price)

        # ── Derived metrics ──────────────────────────────────
        price_per_sqft = round(predicted_price / area) if area > 0 else 0

        luxury_label = LUXURY_LABELS.get(amenity_count, 'Basic')
        luxury_emoji = LUXURY_EMOJIS.get(luxury_label, '🏠')

        # EMI estimate (8.5% interest, 20 years)
        monthly_rate = 0.085 / 12
        tenure_months = 240
        emi = int(
            predicted_price * monthly_rate * (1 + monthly_rate) ** tenure_months
            / ((1 + monthly_rate) ** tenure_months - 1)
        )

        return jsonify({
            'predicted_price': predicted_price,
            'price_range_low': price_low,
            'price_range_high': price_high,
            'price_per_sqft': price_per_sqft,
            'luxury_score': amenity_count,
            'luxury_label': luxury_label,
            'luxury_emoji': luxury_emoji,
            'emi_monthly': emi,
            'city': city,
            'locality': locality,
            'property_type': property_type,
            'area': area,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
        })

    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}', 'code': 'INVALID_INPUT'}), 400
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({'error': 'Internal prediction error', 'code': 'INTERNAL_ERROR'}), 500


# ── Error handlers ────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(429)
def rate_limited(e):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.', 'code': 'RATE_LIMITED'}), 429


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ── Main ──────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🏠 HomeValue AI v2 starting on http://0.0.0.0:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
