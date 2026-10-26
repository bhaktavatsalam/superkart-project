import os
import sys
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Monkey patch to safeguard unpickling across library patch variations
try:
    import numpy as np
    import numpy.random._mt19937 as old_mt
    if not hasattr(old_mt, 'MT19937'):
        import numpy.random as nr
        sys.modules['numpy.random._mt19937'] = nr
except Exception:
    import numpy.random as nr
    import types
    mod = types.ModuleType('numpy.random._mt19937')
    mod.MT19937 = nr.MT19937 if hasattr(nr, 'MT19937') else None
    sys.modules['numpy.random._mt19937'] = mod

app = Flask(__name__)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "superkart_model.joblib")

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    # Programmatically extract the exact feature matrix signature your model trained on
    MODEL_FEATURES = model.feature_names_in_.tolist()
    print("✔ Model and feature profiles loaded successfully into Backend runtime.")
else:
    model = None
    MODEL_FEATURES = []
    print(f"Warning: {MODEL_PATH} not found.")

def align_features(input_data_list):
    """
    Ingests raw feature records, applies preprocessing transforms, 
    and aligns structural dummies with the model's exact fit-time signature.
    """
    df = pd.DataFrame(input_data_list)
    
    # 1. Standardize string variations (Unifies 'reg' to 'Regular' as done in training)
    if 'Product_Sugar_Content' in df.columns:
        df['Product_Sugar_Content'] = df['Product_Sugar_Content'].replace({'reg': 'Regular'})
        
    # 2. Apply One-Hot Encoding transformation
    categorical_cols = ['Product_Sugar_Content', 'Product_Type', 'Store_Size', 
                        'Store_Location_City_Type', 'Store_Type', 'Product_Type_Category']
    
    # Filter only categories present in the incoming payload slice to avoid empty dummy cracks
    active_cats = [col for col in categorical_cols if col in df.columns]
    df_encoded = pd.get_dummies(df, columns=active_cats)
    
    # 3. Dynamic Structural Matrix Alignment
    # Recreates every hidden dummy column seen at fit time and defaults missing states to 0
    for col in MODEL_FEATURES:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
            
    # Re-order variables to strictly mirror the original training array sequence
    return df_encoded[MODEL_FEATURES]

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "model_loaded": (model is not None),
        "total_expected_features": len(MODEL_FEATURES)
    }), 200

@app.route('/predict', methods=['POST'])
def predict_sales():
    if model is None:
        return jsonify({"status": "error", "message": "Model engine uninitialized."}), 503
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Malformed request. No JSON payload received."}), 400
        
        # Preprocess and align incoming vector features
        processed_df = align_features(data)
        
        raw_predictions = model.predict(processed_df)
        formatted_predictions = [round(float(pred), 2) for pred in raw_predictions]
        
        return jsonify({"status": "success", "predictions": formatted_predictions}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/predictbatch', methods=['POST'])
def predict_batch_sales():
    if model is None:
        return jsonify({"status": "error", "message": "Model engine uninitialized."}), 503
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Malformed batch request. Empty payload."}), 400
        
        # Preprocess and align full data matrix rows
        processed_df = align_features(data)
        
        raw_predictions = model.predict(processed_df)
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
