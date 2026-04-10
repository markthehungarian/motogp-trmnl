from flask import Flask, jsonify
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900

# YOUR CUSTOM TRACK MAPS
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

# SCHEDULE
SCHEDULE = {
    "Chang International Circuit": {"short_name": "BURIRAM (TL)", "weekend_date": "27 February – 1 March", "round": 1},
    "Autódromo Internacional Ayrton Senna": {"short_name": "BRAZIL", "weekend_date": "20-22 March", "round": 2},
    "Circuit of the Americas": {"short_name": "COTA (USA)", "weekend_date": "27-29 March", "round": 3},
    "Lusail International Circuit": {"short_name": "LUSAIL (QT)", "weekend_date": "10-12 April", "round": 4},
    "Circuito de Jerez – Ángel Nieto": {"short_name": "JEREZ (ES)", "weekend_date": "24-26 April", "round": 5},
    "Bugatti Circuit": {"short_name": "LE MANS (FR)", "weekend_date": "8-10 May", "round": 6},
    "Circuit de Barcelona-Catalunya": {"short_name": "CATALUNYA (ES)", "weekend_date": "15-17 May", "round": 7},
    "Autodromo Internazionale del Mugello": {"short_name": "MUGELLO (IT)", "weekend_date": "29-31 May", "round": 8},
    "Balaton Park Circuit": {"short_name": "BALATON PARK (HU)", "weekend_date": "5-7 June", "round": 9},
    "Brno Circuit": {"short_name": "BRNO (CZ)", "weekend_date": "19-21 June", "round": 10},
    "TT Circuit Assen": {"short_name": "ASSEN (NL)", "weekend_date": "26-28 June", "round": 11},
    "Sachsenring": {"short_name": "SACHSENRING (D)", "weekend_date": "10-12 July", "round": 12},
    "Silverstone Circuit": {"short_name": "SILVERSTONE (UK)", "weekend_date": "7-9 August", "round": 13},
    "MotorLand Aragón": {"short_name": "ARAGON (ES)", "weekend_date": "28-30 August", "round": 14},
    "Misano World Circuit Marco Simoncelli": {"short_name": "SAN MARINO", "weekend_date": "11-13 September", "round": 15},
    "Red Bull Ring": {"short_name": "RED BULL RING (AT)", "weekend_date": "18-20 September", "round": 16},
    "Mobility Resort Motegi": {"short_name": "MOTEGI (JP)", "weekend_date": "2-4 October", "round": 17},
    "Pertamina Mandalika International Street Circuit": {"short_name": "INDONESIA", "weekend_date": "9-11 October", "round": 18},
    "Phillip Island Grand Prix Circuit": {"short_name": "PHILLIP ISLAND (AU)", "weekend_date": "23-25 October", "round": 19},
    "Petronas Sepang International Circuit": {"short_name": "SEPANG (ML)", "weekend_date": "30 October – 1 November", "round": 20},
    "Algarve International Circuit": {"short_name": "PORTUGAL", "weekend_date": "13-15 November", "round": 21},
    "Circuit Ricardo Tormo": {"short_name": "VALENCIA (ES)", "weekend_date": "20-22 November", "round": 22},
    "default": {"short_name": "UNKNOWN", "weekend_date": "TBD", "round": 0}
}

# YOUR MANUAL STANDINGS (from your PDF)
STATIC_STANDINGS = {
    "motogp": [
        {"position": 1, "rider_name": "M. Bezzecchi", "points": 81},
        {"position": 2, "rider_name": "J. Martin",   "points": 77},
        {"position": 3, "rider_name": "P. Acosta",   "points": 60}
    ],
    "moto2": [
        {"position": 1, "rider_name": "M. Gonzalez", "points": 39.5},
        {"position": 2, "rider_name": "I. Guevara",  "points": 36},
        {"position": 3, "rider_name": "D. Holgado",  "points": 33}
    ],
    "moto3": [
        {"position": 1, "rider_name": "M. Quiles",   "points": 65},
        {"position": 2, "rider_name": "A. Carpe",    "points": 42},
        {"position": 3, "rider_name": "V. Perrone",  "points": 38}
    ]
}

def normalize_circuit_name(name):
    if not name:
        return "default"
    name = name.replace(" - ", " – ")
    name = name.strip()
    return name

def fetch_motogp_data():
    try:
        # For now we use a static next race (Jerez)
        data = {
            "next_race": {
                "circuit": "Circuito de Jerez – Ángel Nieto",
                "short_name": "JEREZ (ES)",
                "weekend_date": "24-26 April",
                "round": 5,
                "track_map_url": CIRCUIT_MAPS.get("Circuito de Jerez – Ángel Nieto", CIRCUIT_MAPS["default"]),
                "track_length": "4.423",
                "lap_record_rider": "Jorge Martín",
                "lap_record_time": "1:36.405"
            },
            "standings": STATIC_STANDINGS,
            "last_updated": datetime.now().isoformat()
        }
        return data

    except Exception as e:
        return {"error": str(e), "last_updated": datetime.now().isoformat()}

@app.route("/")
@app.route("/motogp")
def motogp():
    if time.time() - CACHE["timestamp"] > CACHE_TTL or not CACHE["data"]:
        CACHE["data"] = fetch_motogp_data()
        CACHE["timestamp"] = time.time()
    return jsonify(CACHE["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
