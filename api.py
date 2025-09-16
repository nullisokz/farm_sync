from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

import sqlite3

app = Flask(__name__)
CORS(app)

current_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(current_dir, "models/random_forest_crop.joblib"))
scaler = joblib.load(os.path.join(current_dir, "models/scaler.joblib"))

def get_connection():
    conn = sqlite3.connect("predicitons.db")
    conn.row_factory = sqlite3.Row
    return conn

def Write_to_db(data, prediction):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                INSERT INTO predictions (N, P, K, temperature, humidity, ph, rainfall, predicted_yield, crop)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['N'],
                data['P'],
                data['K'],
                data['temperature'],
                data['humidity'],
                data['ph'],
                data['rainfall'],
                prediction         
            ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"db error : {e}")
        return False


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

        Write_to_db(data,prediction)

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