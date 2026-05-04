# HomeValue AI v2

ML-powered Indian property price predictor. Predicts home prices across 8 major Indian cities with 80+ localities, 5 property types, and 16 amenities.

## Features

- **10,000+ property records** with realistic market-correlated pricing
- **4 ML models** compared with cross-validation & hyperparameter tuning
- **Prediction intervals** via quantile regression (80% confidence)
- **Professional React frontend** with futuristic UI
- **Production-ready** Flask API with CORS, rate limiting, error handling

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate data & train models
```bash
python model/generate_data.py
python model/train.py
```

### 3. Build frontend
```bash
cd frontend
npm install
npm run build
```

### 4. Run server

**Development:**
```bash
python app/app.py
```

**Production:**
```bash
gunicorn wsgi:app
```

Visit `http://localhost:5000`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/config` | GET | Frontend configuration |
| `/api/model-info` | GET | Training report & metrics |
| `/api/predict` | POST | Predict house price |

### Predict Request
```json
{
  "city": "Mumbai",
  "locality": "Andheri",
  "property_type": "Apartment",
  "area": 1200,
  "bedrooms": 3,
  "bathrooms": 2,
  "furnishing": "Semi-Furnished",
  "age": 5,
  "floor": 8,
  "parking": 1,
  "gym": 1,
  "security": 1
}
```

## Project Structure

```
home/
├── app/
│   ├── app.py              # Flask API (CORS, rate limiting)
│   └── static/             # Built React frontend
├── frontend/               # React source (Vite)
├── model/
│   ├── generate_data.py    # Synthetic data generator
│   ├── train.py            # Model training pipeline
│   └── *.pkl               # Saved models
├── data/
│   └── house_data.csv      # Training dataset
├── reports/
│   └── training_report.json
├── wsgi.py                 # WSGI entry point
├── gunicorn.conf.py        # Production config
└── requirements.txt
```
