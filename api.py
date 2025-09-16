from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)

current_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(current_dir, "models/random_forest_crop.joblib"))
scaler = joblib.load(os.path.join(current_dir, "models/scaler.joblib"))

@app.route("/predict", methods=['POST'])
def predict():
    try:
        data = request.json
        features = np.array([[
            data['N'], data['P'], data['K'],
            data['temperature'], data['humidity'],
            data['ph'], data['rainfall']
        ]])

        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)

        return jsonify({
            'prediction': prediction[0],
            'status': "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        })
    
if __name__ == '__main__':
    app.run(debug=True)