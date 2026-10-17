
from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field


# ==================================================
# 1. Project Paths
# ==================================================

# Project root: ML_P2/
PROJECT_DIR = Path(__file__).resolve().parents[2]

FRONTEND_DIR = PROJECT_DIR / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

MODEL_DIR = PROJECT_DIR / "backend" / "model"
MODEL_PATH = MODEL_DIR / "model.pkl"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"


# ==================================================
# 2. Feature Columns
# ==================================================

# Must match the columns used to fit preprocessor.pkl.
FEATURE_COLUMNS = [
    "age",
    "workclass",
    "education_level",
    "education-num",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital-gain",
    "capital-loss",
    "hours-per-week",
    "native-country",
]


# ==================================================
# 3. Load Model and Preprocessor
# ==================================================

if not MODEL_PATH.is_file():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

if not PREPROCESSOR_PATH.is_file():
    raise FileNotFoundError(
        f"Preprocessor file not found: {PREPROCESSOR_PATH}"
    )

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

# Verify that the preprocessor expects the correct columns.
if hasattr(preprocessor, "feature_names_in_"):
    expected_columns = list(preprocessor.feature_names_in_)

    if expected_columns != FEATURE_COLUMNS:
        raise ValueError(
            "Input columns do not match the fitted preprocessor. "
            f"Expected: {expected_columns}"
        )


# ==================================================
# 4. Create FastAPI Application
# ==================================================

app = FastAPI(
    title="Income Prediction API",
    description=(
        "Predict whether a person's income is <=50K or >50K "
        "using a trained XGBoost model."
    ),
    version="1.0.0",
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


# ==================================================
# 5. Input Validation Schema
# ==================================================

class PredictionInput(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    age: int = Field(ge=0)
    workclass: str
    education_level: str
    education_num: int = Field(alias="education-num", ge=0)

    marital_status: str = Field(alias="marital-status")
    occupation: str
    relationship: str
    race: str
    sex: str

    capital_gain: float = Field(alias="capital-gain", ge=0)
    capital_loss: float = Field(alias="capital-loss", ge=0)
    hours_per_week: int = Field(alias="hours-per-week", ge=0)

    native_country: str = Field(alias="native-country")


# ==================================================
# 6. Home Page
# ==================================================

@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


# ==================================================
# 7. Health Check
# ==================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
    }


# ==================================================
# 8. Prediction Endpoint
# ==================================================

@app.post("/predict")
def predict(data: PredictionInput):
    try:
        # Step 1: Convert validated input into a DataFrame.
        input_data = pd.DataFrame(
            [data.model_dump(by_alias=True)]
        )

        # Step 2: Ensure the expected column names and order.
        input_data = input_data[FEATURE_COLUMNS]

        # Step 3: Apply the fitted preprocessing pipeline.
        processed_data = preprocessor.transform(input_data)

        # Step 4: Predict the encoded income class.
        prediction = model.predict(processed_data)[0]

        # Step 5: Convert NumPy scalar to a Python scalar.
        if hasattr(prediction, "item"):
            prediction = prediction.item()

        # Training mapping:
        # <=50K -> 0
        # >50K  -> 1
        if prediction == 0:
            income_category = "<=50K"
        elif prediction == 1:
            income_category = ">50K"
        else:
            raise ValueError(
                f"Unexpected prediction class: {prediction}"
            )

        # Step 6: Return a readable response.
        return {
            "prediction": prediction,
            "income_category": income_category,
            "message": "Prediction completed successfully.",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}",
        ) from exc
