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
    """Handles single instance or lightweight structural item tracking."""
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

# =====================================================================
# NEW: BATCH PREDICTION ENDPOINT
# =====================================================================
@app.route('/predictbatch', methods=['POST'])
def predict_batch_sales():
    """
    Consumes multi-row batch payloads (e.g., historical file rows).
    Computes total consolidated revenue forecasts across all input rows.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Malformed batch request. Empty payload."}), 400
        
        # Ingest full nested data array directly into a Dataframe layout
        input_df = pd.DataFrame(data)
        
        # Execute batch inference matrix multiplication
        raw_predictions = model.predict(input_df)
        formatted_predictions = [round(float(pred), 2) for pred in raw_predictions]
        
        # Compute macro operational supply chain total metrics
        total_predicted_batch_revenue = round(sum(formatted_predictions), 2)
        record_count = len(formatted_predictions)
        
        return jsonify({
            "status": "success",
            "batch_summary": {
                "total_records_processed": record_count,
                "consolidated_batch_revenue": total_predicted_batch_revenue
            },
            "predictions": formatted_predictions
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Batch process failure: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
