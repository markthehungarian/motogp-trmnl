from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900

# UPDATED CIRCUIT_MAPS - using your own GitHub raw images
CIRCUIT_MAPS = {
    "Chang International Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/buriram.png",
    "Autódromo Internacional Ayrton Senna": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/brazil.png",
    "Circuit of the Americas": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/cota.png",
    "Lusail International Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/lusail.png",
    "Circuito de Jerez – Ángel Nieto": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/jerez.png",
    "Bugatti Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/lemans.png",
    "Circuit de Barcelona-Catalunya": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/catalunya.png",
    "Autodromo Internazionale del Mugello": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/mugello.png",
    "Balaton Park Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/balaton.png",
    "Brno Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/brno.png",
    "TT Circuit Assen": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/assen.png",
    "Sachsenring": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/sachsen.png",
    "Silverstone Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/silver.png",
    "MotorLand Aragón": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/aragon.png",
    "Misano World Circuit Marco Simoncelli": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/misano.png",
    "Red Bull Ring": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/austria.png",
    "Mobility Resort Motegi": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/motegi.png",
    "Pertamina Mandalika International Street Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/indonesia.png",
    "Phillip Island Grand Prix Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/phillip.png",
    "Petronas Sepang International Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/sepang.png",
    "Algarve International Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/portugal.png",
    "Circuit Ricardo Tormo": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/valencia.png",

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
