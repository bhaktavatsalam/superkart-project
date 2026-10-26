import os
import sys
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# =====================================================================
# MONKEY PATCH: DYNAMIC RANDOM STATE TRANSLATION (BYPASS NUMPY TYPE ERROR)
# =====================================================================
# This forces pickle to dynamically map the old BitGenerator structure 
# to the current NumPy layout regardless of container patch imbalances.
try:
    import numpy as np
    import numpy.random._mt19937 as old_mt
    # If the alias is missing, link it directly to the system random module
    if not hasattr(old_mt, 'MT19937'):
        import numpy.random as nr
        sys.modules['numpy.random._mt19937'] = nr
except Exception:
    import numpy.random as nr
    import types
    # Dynamically inject the missing tracking module into the active python path
    mod = types.ModuleType('numpy.random._mt19937')
    mod.MT19937 = nr.MT19937 if hasattr(nr, 'MT19937') else None
    sys.modules['numpy.random._mt19937'] = mod

# Initialize Flask Application
app = Flask(__name__)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "superkart_model.joblib")

# Safe unpickling attempt
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("✔ Model unpickled and loaded successfully into Backend runtime.")
    else:
        model = None
        print(f"Warning: {MODEL_PATH} not found. Running server without estimator.")
except Exception as unpickle_error:
    model = None
    print(f"🚨 Unpickling fallback intercept triggered. Error isolated: {str(unpickle_error)}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "model_loaded": (model is not None),
        "file_exists": os.path.exists(MODEL_PATH)
    }), 200

@app.route('/predict', methods=['POST'])
def predict_sales():
    if model is None:
        return jsonify({"status": "error", "message": "Model engine is uninitialized due to library mismatch."}), 503
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

@app.route('/predictbatch', methods=['POST'])
def predict_batch_sales():
    if model is None:
        return jsonify({"status": "error", "message": "Model engine is uninitialized due to library mismatch."}), 503
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Malformed batch request. Empty payload."}), 400
        
        input_df = pd.DataFrame(data)
        raw_predictions = model.predict(input_df)
        formatted_predictions = [round(float(pred), 2) for pred in raw_predictions]
        
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
