import os
import pickle

from flask import Flask, render_template, request

from services.prediction_service import predict_house_price


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")


app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)


# loading machine learning model made by team ML
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)


# Loading scaler of features used by team ML
with open(SCALER_PATH, "rb") as file:
    scaler = pickle.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    try:
        # Get values entered by user from the HTML form
        rm = float(request.form["RM"])
        lstat = float(request.form["LSTAT"])
        ptratio = float(request.form["PTRATIO"])

        # some validation
        if rm <= 0:
            return render_template(
                "index.html",
                error="RM must be greater than 0."
            )

        if lstat < 0:
            return render_template(
                "index.html",
                error="LSTAT cannot be negative."
            )

        if ptratio <= 0:
            return render_template(
                "index.html",
                error="PTRATIO must be greater than 0."
            )

        # Make prediction
        output = predict_house_price(
            model,
            scaler,
            rm,
            lstat,
            ptratio
        )

        return render_template(
            "index.html",
            target=round(float(output), 2)
        )

    except (ValueError, TypeError):
        return render_template(
            "index.html",
            error="Please enter valid numeric values."
        )

    except KeyError:
        return render_template(
            "index.html",
            error="Missing input value."
        )

    except Exception:
        return render_template(
            "index.html",
            error="Something went wrong while making the prediction."
        )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
