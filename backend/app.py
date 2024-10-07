from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import sys
import os
import traceback

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Content of current directory:", os.listdir())

try:
    from pdp_forecast import load_data, preprocess_data, forecast_well, arps_decline
    print("Successfully imported from pdp_forecast")
except ImportError as e:
    print("Error importing from pdp_forecast:", str(e))
    print("Traceback:")
    traceback.print_exc()
    sys.exit(1)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for development

# Load and preprocess data
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "well_prod.csv")
    df = load_data(csv_path)
    df_filtered = preprocess_data(df)
    print(f"Data loaded and preprocessed successfully. Number of wells: {df_filtered['well_api'].nunique()}")
    print(f"Wells in the dataset: {df_filtered['well_api'].unique().tolist()}")
except Exception as e:
    print("Error loading or preprocessing data:", str(e))
    print("Traceback:")
    traceback.print_exc()
    sys.exit(1)

@app.route('/api/wells', methods=['GET'])
def get_wells():
    wells = df_filtered['well_api'].unique().tolist()
    return jsonify(wells)

@app.route('/api/well_data/<well_api>', methods=['GET'])
def get_well_data(well_api):
    try:
        # Convert well_api to string for comparison
        well_data = df_filtered[df_filtered['well_api'].astype(str) == str(well_api)]
        
        print(f"Fetching data for well API: {well_api}")
        print(f"Number of records found: {len(well_data)}")
        
        if len(well_data) < 24:
            error_message = f"Insufficient data for well {well_api}. Only {len(well_data)} records found."
            print(error_message)
            return jsonify({"error": error_message}), 400

        # Select only the last 24 months of data
        last_24_months = well_data.sort_values('prod_date').tail(24)
        
        # Split the data into actual (first 12 months) and forecast period (last 12 months)
        actual_data = last_24_months.iloc[:12]
        forecast_period = last_24_months.iloc[12:]

        # Generate forecast for the last 12 months
        oil_forecast, gas_forecast = forecast_well(actual_data)

        response_data = {
            "dates": last_24_months['prod_date'].tolist(),
            "oil_production": last_24_months['oil'].tolist(),
            "gas_production": last_24_months['gas'].tolist(),
            "oil_forecast": oil_forecast.tolist(),
            "gas_forecast": gas_forecast.tolist(),
            "forecast_dates": forecast_period['prod_date'].tolist()
        }

        return jsonify(response_data)
    except Exception as e:
        error_message = f"Error processing data for well {well_api}: {str(e)}"
        print(error_message)
        print("Traceback:")
        traceback.print_exc()
        return jsonify({"error": error_message}), 500

@app.route('/api/update_forecast/<well_api>', methods=['POST'])
def update_forecast(well_api):
    try:
        params = request.json
        well_data = df_filtered[df_filtered['well_api'].astype(str) == str(well_api)]
        
        if len(well_data) < 24:
            return jsonify({"error": "Insufficient data for this well"}), 400

        train_data = well_data.iloc[:-12]
        test_data = well_data.iloc[-12:]

        # Get the original forecast
        oil_forecast, gas_forecast = forecast_well(train_data)

        # Apply the percentage adjustments
        oil_adjustment = 1 + (params['oil_adjustment'] / 100)
        gas_adjustment = 1 + (params['gas_adjustment'] / 100)

        adjusted_oil_forecast = oil_forecast * oil_adjustment
        adjusted_gas_forecast = gas_forecast * gas_adjustment

        response_data = {
            "oil_forecast": adjusted_oil_forecast.tolist(),
            "gas_forecast": adjusted_gas_forecast.tolist(),
            "forecast_dates": pd.date_range(start=train_data['prod_date'].iloc[-1] + pd.Timedelta(days=30), periods=12, freq='M').tolist()
        }

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
