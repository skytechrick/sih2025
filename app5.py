from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Logging
logging.basicConfig(level=logging.INFO)

# 🌱 SoilGrids API - fixed
def get_soil_properties(lat, lon):
    base_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lat": lat,
        "lon": lon,
        "property": "phh2o,soc,cec,clay,sand,silt,nitrogen,bdod,cfvo",  # ✅ fixed: property not properties
        "depth": "sl1,sl2,sl3",  # ✅ fixed: correct depth codes
        "value": "mean"
    }
    

    try:
        response = requests.get(base_url, params=params, timeout=15)
        app.logger.info(f"SoilGrids API status: {response.status_code}")

        if response.status_code != 200:
            app.logger.warning("SoilGrids failed, using fallback soil data")
            return get_fallback_soil_data(lat)

        data = response.json()
        soil_data = {}

        # Process the response safely
        for layer in data.get("properties", {}).get("layers", []):
            prop_name = layer.get("name")
            for depth in layer.get("depths", []):
                depth_label = depth.get("label", "unknown")
                value = depth.get("values", {}).get("mean")
                if value is None:
                    continue

                # Convert units
                if prop_name == "phh2o":
                    val, unit = round(value / 10.0, 2), "pH"
                elif prop_name == "soc":
                    val, unit = round(value / 10.0, 2), "g/kg"
                elif prop_name == "cec":
                    val, unit = round(value / 10.0, 2), "cmol(c)/kg"
                elif prop_name == "nitrogen":
                    val, unit = round(value / 100.0, 2), "g/kg"
                elif prop_name == "bdod":
                    val, unit = round(value / 100.0, 2), "kg/dm³"
                elif prop_name in ["clay", "sand", "silt", "cfvo"]:
                    val, unit = round(value / 10.0, 2), "%"
                else:
                    val, unit = value, "unknown"

                if prop_name not in soil_data:
                    soil_data[prop_name] = {}
                soil_data[prop_name][depth_label] = {"value": val, "unit": unit}

        if not soil_data:
            return get_fallback_soil_data(lat)

        return soil_data

    except Exception as e:
        app.logger.error(f"SoilGrids error: {e}")
        return get_fallback_soil_data(lat)

# 🌱 Fallback Soil Data
def get_fallback_soil_data(lat):
    return {
        "phh2o": {"sl1": {"value": 6.5, "unit": "pH"}},
        "soc": {"sl1": {"value": 15.0, "unit": "g/kg"}},
        "cec": {"sl1": {"value": 18.0, "unit": "cmol(c)/kg"}},
        "clay": {"sl1": {"value": 25.0, "unit": "%"}},
        "sand": {"sl1": {"value": 45.0, "unit": "%"}},
        "silt": {"sl1": {"value": 30.0, "unit": "%"}},
        "nitrogen": {"sl1": {"value": 1.2, "unit": "g/kg"}},
    }

# 🌦 Weather API - 15 day forecast
def get_weather_data(lat, lon):
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_hours,wind_speed_10m_max",
        "forecast_days": 15,
        "timezone": "auto"
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        app.logger.error(f"Weather API error: {e}")
        return {}

# API Route
@app.route("/api/agricultural-insights", methods=["GET"])
def get_agricultural_insights():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if not lat or not lon:
        return jsonify({"error": "Missing lat or lon"}), 400

    soil_data = get_soil_properties(lat, lon)
    weather_data = get_weather_data(lat, lon)

    return jsonify({
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "coords": {"lat": lat, "lon": lon}
        },
        "soil": soil_data,
        "weather": weather_data
    })



# Health check
@app.route("/")
def health_check():
    return jsonify({"status": "API running", "endpoints": ["/api/agricultural-insights"]})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
