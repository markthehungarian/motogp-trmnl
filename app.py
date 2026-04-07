from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900

# NEW: Simpler direct SVG links (these load reliably on TRMNL)
CIRCUIT_MAPS = {
    "Circuito de Jerez – Ángel Nieto": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Circuito_de_Jerez.svg",
    "Chang International Circuit": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Buriram_International_Circuit.svg",
    "Circuit of the Americas": "https://upload.wikimedia.org/wikipedia/commons/0/0a/COTA_track_map.svg",
    # ... you can add the rest later if you want, but for now this will fix Jerez

    "default": "https://via.placeholder.com/700x280/222/eee?text=TRACK+MAP"
}

# (Keep the rest of your app.py exactly as it was — the SCHEDULE dict, normalize function, fetch_motogp_data, etc.)

@app.route("/")
@app.route("/motogp")
def motogp():
    if time.time() - CACHE["timestamp"] > CACHE_TTL or not CACHE["data"]:
        CACHE["data"] = fetch_motogp_data()
        CACHE["timestamp"] = time.time()
    return jsonify(CACHE["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
