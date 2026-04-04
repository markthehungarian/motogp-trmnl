from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900  # 15 minutes

# Your full circuit maps (keep this as-is)
CIRCUIT_MAPS = {
    "Chang International Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Buriram_International_Circuit.svg/800px-Buriram_International_Circuit.svg.png",
    "Autódromo Internacional Ayrton Senna": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Aut%C3%B3dromo_Internacional_Ayrton_Senna_%28Goi%C3%A2nia%29.svg/800px-Aut%C3%B3dromo_Internacional_Ayrton_Senna_%28Goi%C3%A2nia%29.svg.png",
    "Circuit of the Americas": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/COTA_track_map.svg/800px-COTA_track_map.svg.png",
    "Lusail International Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Lusail_International_Circuit.svg/800px-Lusail_International_Circuit.svg.png",
    "Circuito de Jerez – Ángel Nieto": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Circuito_de_Jerez.svg/800px-Circuito_de_Jerez.svg.png",
    "Bugatti Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Bugatti_Circuit.svg/800px-Bugatti_Circuit.svg.png",
    "Circuit de Barcelona-Catalunya": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Circuit_de_Barcelona-Catalunya.svg/800px-Circuit_de_Barcelona-Catalunya.svg.png",
    "Autodromo Internazionale del Mugello": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Mugello_track_map.svg/800px-Mugello_track_map.svg.png",
    "Balaton Park Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Balaton_Park_Circuit.svg/800px-Balaton_Park_Circuit.svg.png",
    "Brno Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Brno_Circuit.svg/800px-Brno_Circuit.svg.png",
    "TT Circuit Assen": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/TT_Circuit_Assen.svg/800px-TT_Circuit_Assen.svg.png",
    "Sachsenring": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Sachsenring.svg/800px-Sachsenring.svg.png",
    "Silverstone Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Silverstone_Circuit.svg/800px-Silverstone_Circuit.svg.png",
    "MotorLand Aragón": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/MotorLand_Arag%C3%B3n.svg/800px-MotorLand_Arag%C3%B3n.svg.png",
    "Misano World Circuit Marco Simoncelli": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Misano_World_Circuit.svg/800px-Misano_World_Circuit.svg.png",
    "Red Bull Ring": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Red_Bull_Ring.svg/800px-Red_Bull_Ring.svg.png",
    "Mobility Resort Motegi": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Twin_Ring_Motegi.svg/800px-Twin_Ring_Motegi.svg.png",
    "Pertamina Mandalika International Street Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Mandalika_International_Street_Circuit.svg/800px-Mandalika_International_Street_Circuit.svg.png",
    "Phillip Island Grand Prix Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phillip_Island_Grand_Prix_Circuit.svg/800px-Phillip_Island_Grand_Prix_Circuit.svg.png",
    "Petronas Sepang International Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Sepang_International_Circuit.svg/800px-Sepang_International_Circuit.svg.png",
    "Algarve International Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Portimao_track_map.svg/800px-Portimao_track_map.svg.png",
    "Circuit Ricardo Tormo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Circuit_Ricardo_Tormo.svg/800px-Circuit_Ricardo_Tormo.svg.png",

    "default": "https://via.placeholder.com/400x200/333/fff?text=Track+Map+Coming+Soon"
}

def safe_get(obj, key, default=None):
    """Safe way to get value whether obj is dict or not"""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default

def fetch_motogp_data():
    base = "https://api.motogp.pulselive.com/motogp/v1"

    try:
        print("=== Starting MotoGP data fetch ===")

        # 1. Get seasons to find current season UUID
        seasons_resp = requests.get(f"{base}/results/seasons", timeout=10)
        print(f"Seasons status: {seasons_resp.status_code}")
        seasons = seasons_resp.json()
        season_uuid = None
        for s in seasons:
            if s.get("current") or str(s.get("year")) == "2026":
                season_uuid = s.get("id")
                print(f"Found season UUID: {season_uuid} for year {s.get('year')}")
                break
        if not season_uuid:
            season_uuid = "2026"  # fallback
            print("Using fallback season")

        # 2. Get events
        events_url = f"{base}/results/events?seasonUuid={season_uuid}"
        events_resp = requests.get(events_url, timeout=15)
        print(f"Events status: {events_resp.status_code} | Items: {len(events_resp.json()) if isinstance(events_resp.json(), list) else 'not list'}")

        events = events_resp.json()
        if not isinstance(events, list):
            events = []

        # Take the first event as "next" for now (we can improve later)
        next_event = events[0] if events else {}

        circuit_raw = safe_get(next_event, "circuit")
        circuit_name = ""
        if isinstance(circuit_raw, dict):
            circuit_name = circuit_raw.get("name") or circuit_raw.get("title") or "Unknown"
        elif isinstance(circuit_raw, str):
            circuit_name = circuit_raw
        else:
            circuit_name = "Unknown"

        print(f"Extracted circuit name: '{circuit_name}'")

        data = {
            "next_race": {
                "title": safe_get(next_event, "name") or safe_get(next_event, "title", "Next Race"),
                "date": safe_get(next_event, "date_start") or safe_get(next_event, "date", "TBD"),
                "circuit": circuit_name,
                "track_map_url": CIRCUIT_MAPS.get(circuit_name, CIRCUIT_MAPS["default"])
            },
            "standings": {"motogp": [], "moto2": [], "moto3": []},  # Temporarily empty – we'll add later
            "last_updated": datetime.now().isoformat(),
            "debug_season_uuid": season_uuid,
            "debug_events_count": len(events)
        }
        return data

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            "error": str(e),
            "message": "Failed to fetch MotoGP data – check Render logs for full traceback",
            "last_updated": datetime.now().isoformat()
        }

@app.route("/motogp")
def motogp():
    if time.time() - CACHE["timestamp"] > CACHE_TTL or not CACHE["data"]:
        CACHE["data"] = fetch_motogp_data()
        CACHE["timestamp"] = time.time()
    return jsonify(CACHE["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
