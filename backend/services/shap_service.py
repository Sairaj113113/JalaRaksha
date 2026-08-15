from functools import lru_cache

import numpy as np
import shap

from backend.services.risk_service import (
    load_model,
    load_imputer,
    prepare_features,
    get_model_features,
)


@lru_cache(maxsize=1)
def load_explainer():
    """
    Create and cache the SHAP TreeExplainer
    for the trained Random Forest model.
    """
    model = load_model()

    return shap.TreeExplainer(
        model
    )


def explain_observation(observation):
    """
    Generate SHAP feature contributions for
    one groundwater observation.

    Uses the exact same feature preparation,
    feature ordering and imputer as prediction.
    """

    if observation is None:
        raise ValueError(
            "Observation is required for SHAP explanation."
        )

    model = load_model()
    imputer = load_imputer()
    explainer = load_explainer()

    features = get_model_features()

    # Same feature preparation used by the ML model.
    X = prepare_features(
        observation
    )

    # Same imputation used during training/prediction.
    X_imputed = imputer.transform(
        X
    )

    # Calculate SHAP values.
    shap_values = explainer.shap_values(
        X_imputed
    )

    prediction = model.predict(
        X_imputed
    )[0]

    probabilities = model.predict_proba(
        X_imputed
    )[0]

    classes = list(
        model.classes_
    )

    predicted_class_index = classes.index(
        prediction
    )

    # SHAP has returned different structures
    # across SHAP versions. Normalize them.
    if isinstance(
        shap_values,
        list
    ):
        class_values = np.asarray(
            shap_values[predicted_class_index]
        )[0]

    else:
        shap_array = np.asarray(
            shap_values
        )

        if shap_array.ndim == 3:
            class_values = shap_array[
                0,
                :,
                predicted_class_index
            ]

        elif shap_array.ndim == 2:
            class_values = shap_array[0]

        else:
            raise ValueError(
                "Unexpected SHAP output shape: "
                f"{shap_array.shape}"
            )

    feature_values = X_imputed[0]

    contributions = []

    for feature, value, shap_value in zip(
        features,
        feature_values,
        class_values,
    ):
        contributions.append(
            {
                "feature": feature,
                "value": (
                    float(value)
                    if np.isfinite(value)
                    else None
                ),
                "shap_value": float(
                    shap_value
                ),
                "absolute_impact": float(
                    abs(shap_value)
                ),
            }
        )

    # Most influential features first.
    contributions.sort(
        key=lambda item: item[
            "absolute_impact"
        ],
        reverse=True,
    )

    confidence = float(
        max(probabilities)
    )

    return {
        "prediction": str(
            prediction
        ),
        "confidence": confidence,
        "features": contributions,
    }


def get_top_shap_features(
    observation,
    top_n=5,
):
    """
    Return only the most influential features.
    """

    if top_n < 1:
        raise ValueError(
            "top_n must be at least 1."
        )

    explanation = explain_observation(
        observation
    )

    return {
        "prediction": explanation[
            "prediction"
        ],
        "confidence": explanation[
            "confidence"
        ],
        "top_features": explanation[
            "features"
        ][:top_n],
    }