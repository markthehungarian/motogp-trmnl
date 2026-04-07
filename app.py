from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900

# UPDATED: Now using direct SVG URLs (much more reliable on TRMNL)
CIRCUIT_MAPS = {
    "Chang International Circuit": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Buriram_International_Circuit.svg",
    "Autódromo Internacional Ayrton Senna": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Aut%C3%B3dromo_Internacional_Ayrton_Senna_%28Goi%C3%A2nia%29.svg",
    "Circuit of the Americas": "https://upload.wikimedia.org/wikipedia/commons/0/0a/COTA_track_map.svg",
    "Lusail International Circuit": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Lusail_International_Circuit.svg",
    "Circuito de Jerez – Ángel Nieto": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Circuito_de_Jerez.svg",
    "Bugatti Circuit": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Bugatti_Circuit.svg",
    "Circuit de Barcelona-Catalunya": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Circuit_de_Barcelona-Catalunya.svg",
    "Autodromo Internazionale del Mugello": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Mugello_track_map.svg",
    "Balaton Park Circuit": "https://upload.wikimedia.org/wikipedia/commons/8/8f/Balaton_Park_Circuit.svg",
    "Brno Circuit": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Brno_Circuit.svg",
    "TT Circuit Assen": "https://upload.wikimedia.org/wikipedia/commons/5/5e/TT_Circuit_Assen.svg",
    "Sachsenring": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Sachsenring.svg",
    "Silverstone Circuit": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Silverstone_Circuit.svg",
    "MotorLand Aragón": "https://upload.wikimedia.org/wikipedia/commons/5/5e/MotorLand_Arag%C3%B3n.svg",
    "Misano World Circuit Marco Simoncelli": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Misano_World_Circuit.svg",
    "Red Bull Ring": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Red_Bull_Ring.svg",
    "Mobility Resort Motegi": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Twin_Ring_Motegi.svg",
    "Pertamina Mandalika International Street Circuit": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Mandalika_International_Street_Circuit.svg",
    "Phillip Island Grand Prix Circuit": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Phillip_Island_Grand_Prix_Circuit.svg",
    "Petronas Sepang International Circuit": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Sepang_International_Circuit.svg",
    "Algarve International Circuit": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Portimao_track_map.svg",
    "Circuit Ricardo Tormo": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Circuit_Ricardo_Tormo.svg",

    "default": "https://via.placeholder.com/600x300/333/fff?text=Track+Map+Coming+Soon"
}

# NEW: Full schedule from your PDF (short name + weekend dates + round number)
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

def normalize_circuit_name(name):
    if not name:
        return "default"
    name = name.replace(" - ", " – ")
    name = name.strip()
    return name

def fetch_motogp_data():
    base = "https://api.motogp.pulselive.com/motogp/v1"
    try:
        seasons = requests.get(f"{base}/results/seasons", timeout=10).json()
        season_uuid = next((s["id"] for s in seasons if s.get("current") or str(s.get("year")) == "2026"), "2026")

        events_resp = requests.get(f"{base}/results/events?seasonUuid={season_uuid}", timeout=15).json()
        events = events_resp if isinstance(events_resp, list) else []

        today = datetime.now().date()
        upcoming = []
        for e in events:
            date_str = e.get("date_start") or e.get("date")
            if date_str:
                try:
                    event_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                    if event_date >= today:
                        upcoming.append(e)
                except:
                    pass

        next_event = upcoming[0] if upcoming else (events[0] if events else {})

        circuit_raw = next_event.get("circuit") if isinstance(next_event, dict) else None
        circuit_name = ""
        if isinstance(circuit_raw, dict):
            circuit_name = circuit_raw.get("name") or circuit_raw.get("title", "Unknown")
        elif isinstance(circuit_raw, str):
            circuit_name = circuit_raw

        clean_name = normalize_circuit_name(circuit_name)
        info = SCHEDULE.get(clean_name, SCHEDULE["default"])

        data = {
            "next_race": {
                "circuit": circuit_name,
                "short_name": info["short_name"],
                "weekend_date": info["weekend_date"],
                "round": info["round"],
                "track_map_url": CIRCUIT_MAPS.get(clean_name, CIRCUIT_MAPS["default"]),
                "track_length": "4.423" if clean_name == "Circuito de Jerez – Ángel Nieto" else "N/A",  # you can expand later
                "lap_record_rider": "Jorge Martín" if clean_name == "Circuito de Jerez – Ángel Nieto" else "TBD",
                "lap_record_time": "1:36.405" if clean_name == "Circuito de Jerez – Ángel Nieto" else "TBD"
            },
            "standings": {"motogp": [], "moto2": [], "moto3": []},
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
