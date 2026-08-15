from functools import lru_cache

import joblib
import pandas as pd

from backend.config import (
    RF_MODEL_PATH,
    IMPUTER_PATH,
    FEATURES_PATH,
    MODEL_FEATURES,
)
from backend.services.location_service import (
    get_latest_observation,
)


@lru_cache(maxsize=1)
def load_model():
    """
    Load the trained Random Forest model once.
    """
    return joblib.load(RF_MODEL_PATH)


@lru_cache(maxsize=1)
def load_imputer():
    """
    Load the trained imputer once.
    """
    return joblib.load(IMPUTER_PATH)


@lru_cache(maxsize=1)
def load_feature_list():
    """
    Load the feature list saved during training.
    """
    features = joblib.load(FEATURES_PATH)

    if isinstance(features, (list, tuple)):
        return list(features)

    return list(features)


def get_model_features():
    """
    Return the exact features expected by the trained model.
    """
    features = load_feature_list()

    if features != MODEL_FEATURES:
        raise ValueError(
            "Saved model feature list does not match "
            "the backend MODEL_FEATURES configuration."
        )

    return features


def prepare_features(observation):
    """
    Extract the exact model features from one observation.

    The observation must come from
    get_latest_observation().
    """
    features = get_model_features()

    missing_features = [
        feature
        for feature in features
        if feature not in observation
    ]

    if missing_features:
        raise ValueError(
            f"Missing model features: {missing_features}"
        )

    X = pd.DataFrame(
        [
            {
                feature: observation[feature]
                for feature in features
            }
        ]
    )

    # Convert values to numeric where possible.
    for column in X.columns:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    return X


def predict_observation(observation):
    """
    Run the trained Random Forest on one observation.
    """
    if observation is None:
        raise ValueError(
            "Observation is required for prediction."
        )

    model = load_model()
    imputer = load_imputer()

    X = prepare_features(observation)

    # Apply the same imputation process used during training.
    X_imputed = imputer.transform(X)

    # Prediction.
    prediction = model.predict(
        X_imputed
    )[0]

    # Class probabilities.
    probabilities = model.predict_proba(
        X_imputed
    )[0]

    model_classes = model.classes_

    probability_dict = {
        str(label): float(probability)
        for label, probability
        in zip(
            model_classes,
            probabilities
        )
    }

    confidence = float(
        max(probabilities)
    )

    return {
        "classification": str(
            prediction
        ),
        "confidence": confidence,
        "probabilities": probability_dict,
    }


def predict_location(district, mandal):
    """
    Resolve the latest observation for a district + mandal
    and run the ML prediction.

    This ensures the prediction uses the same shared
    latest-observation logic as the rest of the backend.
    """
    observation = get_latest_observation(
        district,
        mandal
    )

    if observation is None:
        return None

    prediction = predict_observation(
        observation
    )

    return {
        "observation": observation,
        "prediction": prediction,
    }