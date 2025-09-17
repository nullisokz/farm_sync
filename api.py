from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
from PIL import Image, ImageOps
import base64, io
import sqlite3

app = Flask(__name__)
CORS(app)

current_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(current_dir, "models/random_forest_crop.joblib"))
scaler = joblib.load(os.path.join(current_dir, "models/scaler.joblib"))

mnist_model = None
mnist_scaler = None
try:
    mnist_model = joblib.load(os.path.join(current_dir, "models/mnist_et.joblib"))
    mnist_scaler = joblib.load(os.path.join(current_dir, "models/mnist_scaler.joblib"))
    print("[MNIST] model + scaler loaded")
except Exception as e:
    print(f"[MNIST] Warning: could not load model/scaler: {e}")

def get_connection():
    conn = sqlite3.connect("predictions.db")
    conn.row_factory = sqlite3.Row
    return conn

def Write_to_db(data, prediction):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                INSERT INTO predictions (N, P, K,  humidity,  rainfall,temperature, crop, ph,name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['N'],
                data['P'],
                data['K'],
                data['humidity'],
                data['rainfall'],
                data['temperature'],
                prediction,
                data['ph'],
                data['name']
                          
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

        Write_to_db(data,prediction[0])

        prediction_cap = prediction[0].capitalize()

        return jsonify({
            'prediction': prediction_cap,
            'status': "success"
        })
        
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        })
    

def _decode_data_url_png(data_url: str) -> bytes:
    # "data:image/png;base64,AAAA..."
    header, b64 = data_url.split(",", 1)
    return base64.b64decode(b64)

def _prepare_28x28(img_bytes: bytes, invert=True, binarize=False, threshold=128):
    img = Image.open(io.BytesIO(img_bytes)).convert("L")  # gråskala
    img = img.resize((28, 28), Image.BILINEAR)
    if invert:
        img = ImageOps.invert(img)  # vår canvas: svart på vit -> MNIST: vit på svart
    arr2d = np.array(img, dtype=np.float32)
    if binarize:
        arr2d = (arr2d > threshold).astype(np.float32) * 255.0
    X = arr2d.reshape(1, -1)  # (1, 784)
    return X, arr2d

@app.route("/mnist/check", methods=["POST"])
def mnist_check():
    """
    Body JSON:
      { "image": "data:image/png;base64,...", "target_digit": 0-9, "threshold": 0.85 }
    Return JSON:
      { status, passed, pred, prob, target }
    """
    try:
        if mnist_model is None or mnist_scaler is None:
            return jsonify({"status":"error","error":"MNIST model/scaler not loaded"}), 500

        data = request.json or {}
        data_url = data.get("image")
        target = int(data.get("target_digit", -1))
        threshold = float(data.get("threshold", 0.20))

        if not data_url or target < 0 or target > 9:
            return jsonify({"status":"error","error":"Missing image or invalid target_digit"}), 400

        img_bytes = _decode_data_url_png(data_url)
        X, _ = _prepare_28x28(img_bytes, invert=True, binarize=False)

        Xs = mnist_scaler.transform(X)
        pred = int(mnist_model.predict(Xs)[0])

        if hasattr(mnist_model, "predict_proba"):
            prob = float(mnist_model.predict_proba(Xs)[0][pred])
        else:
            prob = 1.0 if pred == target else 0.0

        passed = (pred == target) or (prob >= threshold)

        return jsonify({
            "status": "success",
            "passed": passed,
            "pred": pred,
            "prob": prob,
            "target": target
        })
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)