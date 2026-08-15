from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


DATA_DIR = BASE_DIR / "data"
INTERIM_DIR = DATA_DIR / "interim"

GROUNDWATER_DATA_PATH = (
    INTERIM_DIR / "jala_raksha_model_data.csv"
)


MODELS_DIR = BASE_DIR / "models"

RF_MODEL_PATH = (
    MODELS_DIR / "jala_raksha_rf.pkl"
)

IMPUTER_PATH = (
    MODELS_DIR / "jala_raksha_imputer.pkl"
)

FEATURES_PATH = (
    MODELS_DIR / "jala_raksha_features.pkl"
)


API_TITLE = "Jala Raksha API"
API_VERSION = "1.0.0"


GPS_MAX_DISTANCE_KM = 25.0


CLASS_LABELS = [
    "Safe",
    "Semi-Critical",
    "Over-Exploited",
    "Critical",
]


MODEL_FEATURES = [
    "value",
    "lat",
    "long",
    "year",
    "month",
    "station_distance_km",
    "rainfall_available",
    "rainfall_days",
    "monthly_rainfall_mm_model",
    "rainfall_deficit_flag",
    "heavy_rainfall_flag",
    "monsoon_month",
    "month_sin",
    "month_cos",
    "coordinate_quality",
]