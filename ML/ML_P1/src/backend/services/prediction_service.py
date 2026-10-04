import numpy as np


def predict_house_price(model, scaler, rm, lstat, ptratio):

    # Create input array
    features = np.array([[rm, lstat, ptratio]])
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)

    return prediction[0]