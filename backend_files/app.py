import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "superkart_model.joblib")

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✔ Model loaded successfully into Backend runtime.")
else:
    print(f"Warning: {MODEL_PATH} not found. Please upload the file to this folder.")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "model_loaded": os.path.exists(MODEL_PATH)}), 200

@app.route('/predict', methods=['POST'])
def predict_sales():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Malformed request. No JSON payload received."}), 400
        
        input_df = pd.DataFrame(data)
        raw_predictions = model.predict(input_df)
        formatted_predictions = [round(float(pred), 2) for pred in raw_predictions]
        
        return jsonify({"status": "success", "predictions": formatted_predictions}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
