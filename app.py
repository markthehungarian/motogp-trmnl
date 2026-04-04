from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900  # 15 minutes cache

# ===================================================================
# 1. FULL CIRCUIT MAPS (Wikipedia images)
# ===================================================================
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

# ===================================================================
# 2. FULL CIRCUIT INFO - Track length + Lap Record for all 22 circuits
# ===================================================================
CIRCUIT_INFO = {
    "Chang International Circuit": {"length": "4.554", "lap_record_rider": "Marco Bezzecchi", "lap_record_time": "1:28.526"},
    "Autódromo Internacional Ayrton Senna": {"length": "3.820", "lap_record_rider": "Marco Bezzecchi", "lap_record_time": "1:17.408"},
    "Circuit of the Americas": {"length": "5.513", "lap_record_rider": "Fabio di Giannantonio", "lap_record_time": "2:00.864"},
    "Lusail International Circuit": {"length": "5.380", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:52.000"},
    "Circuito de Jerez – Ángel Nieto": {"length": "4.423", "lap_record_rider": "Jorge Martín", "lap_record_time": "1:36.405"},
    "Bugatti Circuit": {"length": "4.185", "lap_record_rider": "Jorge Martín", "lap_record_time": "1:31.232"},
    "Circuit de Barcelona-Catalunya": {"length": "4.657", "lap_record_rider": "Aleix Espargaró", "lap_record_time": "1:38.190"},
    "Autodromo Internazionale del Mugello": {"length": "5.245", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:45.519"},
    "Balaton Park Circuit": {"length": "4.115", "lap_record_rider": "TBD", "lap_record_time": "TBD"},
    "Brno Circuit": {"length": "5.403", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:52.303"},
    "TT Circuit Assen": {"length": "4.542", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:31.500"},
    "Sachsenring": {"length": "3.671", "lap_record_rider": "Jorge Martín", "lap_record_time": "1:19.071"},
    "Silverstone Circuit": {"length": "5.891", "lap_record_rider": "Aleix Espargaró", "lap_record_time": "1:58.000"},
    "MotorLand Aragón": {"length": "5.077", "lap_record_rider": "Marc Márquez", "lap_record_time": "1:46.000"},
    "Misano World Circuit Marco Simoncelli": {"length": "4.226", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:31.000"},
    "Red Bull Ring": {"length": "4.318", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:23.000"},
    "Mobility Resort Motegi": {"length": "4.801", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:43.000"},
    "Pertamina Mandalika International Street Circuit": {"length": "4.310", "lap_record_rider": "Jorge Martín", "lap_record_time": "1:30.000"},
    "Phillip Island Grand Prix Circuit": {"length": "4.445", "lap_record_rider": "Marc Márquez", "lap_record_time": "1:27.000"},
    "Petronas Sepang International Circuit": {"length": "5.543", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:57.000"},
    "Algarve International Circuit": {"length": "4.592", "lap_record_rider": "Jorge Martín", "lap_record_time": "1:36.000"},
    "Circuit Ricardo Tormo": {"length": "4.005", "lap_record_rider": "Francesco Bagnaia", "lap_record_time": "1:30.000"},

    "default": {"length": "N/A", "lap_record_rider": "TBD", "lap_record_time": "TBD"}
}

def normalize_circuit_name(name):
    """Fix small differences from the API (hyphens, accents, spacing)"""
    if not name:
        return "default"
    name = name.replace(" - ", " – ")          # fix hyphen
    name = name.replace("Á", "A")              # fix Ángel
    name = name.replace("á", "a")
    name = name.strip()
    return name

def fetch_motogp_data():
    base = "https://api.motogp.pulselive.com/motogp/v1"
    try:
        print("=== Starting MotoGP data fetch ===")

        # 1. Get current season UUID
        seasons = requests.get(f"{base}/results/seasons", timeout=10).json()
        season_uuid = next((s["id"] for s in seasons if s.get("current") or str(s.get("year")) == "2026"), "2026")

        # 2. Get ALL events
        events_resp = requests.get(f"{base}/results/events?seasonUuid={season_uuid}", timeout=15).json()
        events = events_resp if isinstance(events_resp, list) else []

        # 3. Filter to FUTURE events only
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

        # 4. Safe circuit name + normalization
        circuit_raw = next_event.get("circuit") if isinstance(next_event, dict) else None
        circuit_name = ""
        if isinstance(circuit_raw, dict):
            circuit_name = circuit_raw.get("name") or circuit_raw.get("title", "Unknown")
        elif isinstance(circuit_raw, str):
            circuit_name = circuit_raw

        clean_name = normalize_circuit_name(circuit_name)
        info = CIRCUIT_INFO.get(clean_name, CIRCUIT_INFO["default"])

        data = {
            "next_race": {
                "circuit": circuit_name,           # keep original for display
                "date": next_event.get("date_start") or next_event.get("date", "TBD"),
                "title": next_event.get("name") or next_event.get("title", ""),
                "track_map_url": CIRCUIT_MAPS.get(clean_name, CIRCUIT_MAPS["default"]),
                "track_length": info["length"],
                "lap_record_rider": info["lap_record_rider"],
                "lap_record_time": info["lap_record_time"]
            },
            "standings": {"motogp": [], "moto2": [], "moto3": []},
            "last_updated": datetime.now().isoformat(),
            "debug_upcoming_count": len(upcoming)
        }
        return data

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {"error": str(e), "message": "Check Render logs", "last_updated": datetime.now().isoformat()}

@app.route("/motogp")
def motogp():
    if time.time() - CACHE["timestamp"] > CACHE_TTL or not CACHE["data"]:
        CACHE["data"] = fetch_motogp_data()
        CACHE["timestamp"] = time.time()
    return jsonify(CACHE["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
