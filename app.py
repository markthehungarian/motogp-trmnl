from flask import Flask, jsonify
import requests
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
        upcoming = [e for e in events if (date_str := e.get("date_start") or e.get("date")) and 
                    datetime.strptime(date_str[:10], "%Y-%m-%d").date() >= today]

        next_event = upcoming[0] if upcoming else (events[0] if events else {})

        circuit_raw = next_event.get("circuit") if isinstance(next_event, dict) else None
        circuit_name = ""
        if isinstance(circuit_raw, dict):
            circuit_name = circuit_raw.get("name") or circuit_raw.get("title", "Unknown")
        elif isinstance(circuit_raw, str):
            circuit_name = circuit_raw

        clean_name = normalize_circuit_name(circuit_name)
        info = SCHEDULE.get(clean_name, SCHEDULE["default"])

        # === STANDINGS with full debug ===
        standings = {"motogp": [], "moto2": [], "moto3": []}
        try:
            standings_resp = requests.get(f"{base}/results/standings?seasonUuid={season_uuid}", timeout=15).json()
            standings_list = standings_resp if isinstance(standings_resp, list) else []

            print("=== First 10 category values from API ===")
            for i, entry in enumerate(standings_list[:10]):
                cat = str(entry.get("category") or entry.get("class") or entry.get("categoryName") or "").strip()
                print(f"Entry {i}: category = '{cat}'")

            for entry in standings_list:
                cat = str(entry.get("category") or entry.get("class") or entry.get("categoryName") or "").lower().replace(" ", "")
                rider = entry.get("rider", {}) or {}
                name = rider.get("name") or rider.get("full_name") or "Unknown Rider"
                pos = entry.get("position", 0)
                pts = entry.get("points", 0)

                if "motogp" in cat:
                    if len(standings["motogp"]) < 3:
                        standings["motogp"].append({"position": pos, "rider_name": name, "points": pts})
                elif "moto2" in cat:
                    if len(standings["moto2"]) < 3:
                        standings["moto2"].append({"position": pos, "rider_name": name, "points": pts})
                elif "moto3" in cat:
                    if len(standings["moto3"]) < 3:
                        standings["moto3"].append({"position": pos, "rider_name": name, "points": pts})

            print(f"Standings loaded → MotoGP: {len(standings['motogp'])}, Moto2: {len(standings['moto2'])}, Moto3: {len(standings['moto3'])}")
        except Exception as se:
            print(f"Standings fetch failed: {se}")

        data = {
            "next_race": {
                "circuit": circuit_name,
                "short_name": info["short_name"],
                "weekend_date": info["weekend_date"],
                "round": info["round"],
                "track_map_url": CIRCUIT_MAPS.get(clean_name, CIRCUIT_MAPS["default"]),
                "track_length": "4.423" if clean_name == "Circuito de Jerez – Ángel Nieto" else "N/A",
                "lap_record_rider": "Jorge Martín" if clean_name == "Circuito de Jerez – Ángel Nieto" else "TBD",
                "lap_record_time": "1:36.405" if clean_name == "Circuito de Jerez – Ángel Nieto" else "TBD"
            },
            "standings": standings,
            "last_updated": datetime.now().isoformat()
        }
        return data

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
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
