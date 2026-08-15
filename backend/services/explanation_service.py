import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from backend.services.shap_service import (
    get_top_shap_features,
)


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    ENV_PATH,
    override=True,
)


GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.5-flash",
)


@lru_cache(maxsize=1)
def get_client():
    """
    Create and cache the Gemini client.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def build_prompt(
    district,
    mandal,
    observation,
    prediction,
    shap_result,
):
    """
    Build a grounded prompt using only
    Jala Raksha backend data.
    """

    data = {
        "location": {
            "district": district,
            "mandal": mandal,
        },
        "groundwater": {
            "value_m": observation.get("value"),
        },
        "rainfall": {
            "monthly_rainfall_mm": (
                observation.get(
                    "monthly_rainfall_mm_model"
                )
            ),
            "rainfall_days": (
                observation.get(
                    "rainfall_days"
                )
            ),
            "available": (
                observation.get(
                    "rainfall_available"
                )
            ),
            "confidence": (
                observation.get(
                    "rainfall_confidence"
                )
            ),
        },
        "model_prediction": {
            "classification": (
                prediction.get(
                    "classification"
                )
            ),
            "confidence": (
                prediction.get(
                    "confidence"
                )
            ),
            "probabilities": (
                prediction.get(
                    "probabilities"
                )
            ),
        },
        "shap_explanation": {
            "prediction": (
                shap_result.get(
                    "prediction"
                )
            ),
            "confidence": (
                shap_result.get(
                    "confidence"
                )
            ),
            "top_features": (
                shap_result.get(
                    "top_features"
                )
            ),
        },
    }

    return f"""
You are the explanation engine for Jala Raksha,
a groundwater risk assessment system.

Explain the existing machine-learning prediction
to a normal user.

STRICT RULES:

1. Use ONLY the supplied data.
2. Never invent measurements.
3. Never invent rainfall conditions.
4. Never change the model classification.
5. Never claim the prediction is certain.
6. Explain SHAP factors in simple language.
7. Do not expose raw SHAP numbers unless useful.
8. If rainfall is unavailable, say so clearly.
9. The groundwater value comes from the dataset.
10. The classification comes from the Random Forest.
11. Recommendations must be practical and cautious.
12. SHAP shows model influence, not physical causation.
13. Return ONLY valid JSON.

JALA RAKSHA DATA:

{json.dumps(data, indent=2, default=str)}

Return exactly:

{{
  "summary": "A clear 2-3 sentence explanation.",
  "key_factors": [
    {{
      "factor": "Human-readable factor name",
      "explanation": "Simple explanation of the factor's influence."
    }}
  ],
  "recommendations": [
    "Practical recommendation 1",
    "Practical recommendation 2",
    "Practical recommendation 3"
  ],
  "disclaimer": "Short decision-support disclaimer."
}}
"""


def validate_explanation(
    explanation
):
    """
    Validate the Gemini response.
    """

    required = [
        "summary",
        "key_factors",
        "recommendations",
        "disclaimer",
    ]

    for field in required:
        if field not in explanation:
            raise RuntimeError(
                f"Missing explanation field: {field}"
            )

    if not isinstance(
        explanation["summary"],
        str,
    ):
        raise RuntimeError(
            "summary must be a string."
        )

    if not isinstance(
        explanation["key_factors"],
        list,
    ):
        raise RuntimeError(
            "key_factors must be a list."
        )

    if not isinstance(
        explanation["recommendations"],
        list,
    ):
        raise RuntimeError(
            "recommendations must be a list."
        )

    if not isinstance(
        explanation["disclaimer"],
        str,
    ):
        raise RuntimeError(
            "disclaimer must be a string."
        )

    return True


def generate_explanation(
    district,
    mandal,
    observation,
    prediction,
):
    """
    Generate a grounded Gemini explanation
    using Random Forest + SHAP.
    """

    shap_result = get_top_shap_features(
        observation,
        top_n=5,
    )

    prompt = build_prompt(
        district=district,
        mandal=mandal,
        observation=observation,
        prediction=prediction,
        shap_result=shap_result,
    )

    client = get_client()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
    "response_mime_type": "application/json",
},
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    try:
        explanation = json.loads(
            response.text
        )

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON."
        ) from exc

    validate_explanation(
        explanation
    )

    return explanation