from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello — API running on Render!"

@app.route("/api/hello", methods=["GET"])
def hello():
    name = request.args.get("name", "world")
    return jsonify({"message": f"hello, {name}"}), 200

@app.route("/api/weather", methods=["GET"])
def weather():
    # پارامتر city از query string میاد
    city = request.args.get("city", "Tehran")
    # اگر کلید WeatherAPI رو در محیط گذاشته باشی از سرویس واقعی استفاده می‌کنیم
    weather_key = os.environ.get("WEATHER_KEY")
    if weather_key:
        try:
            resp = requests.get(
                "https://api.weatherapi.com/v1/current.json",
                params={"key": weather_key, "q": city, "aqi": "no"},
                timeout=10
            )
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            return jsonify({"error": "failed to call weatherapi", "detail": str(e)}), 500
    # اگر کلید وجود نداشت، دادهٔ نمونه برمی‌گردونیم
    return jsonify({"city": city, "temp_c": 25, "condition": "Sunny", "note": "demo data — set WEATHER_KEY to enable real data"}), 200

# ساده‌ترین روش احراز هویت: X-API-KEY header
def check_api_key():
    required = os.environ.get("API_KEY")
    if not required:
        return True
    provided = request.headers.get("X-API-KEY")
    return provided == required

@app.before_request
def require_key():
    # فقط مسیر / و /api/hello رو بدون کلید می‌ذاریم (آزمایشی)
    if request.path.startswith("/api/"):
        if not check_api_key():
            return jsonify({"error": "missing or invalid X-API-KEY"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
