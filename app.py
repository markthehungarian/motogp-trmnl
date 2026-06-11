from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900  # 15 minutes cache

BASE_URL = "https://api.motogp.pulselive.com/motogp/v1"

# ============================================================
# STATIC DATA - UPDATE THE URLs AND LAP RECORDS BELOW
# ============================================================

# Your custom track map images (GitHub raw URLs)
CIRCUIT_MAPS = {
    # 2026 Calendar circuits (mapped to your filenames)
    "Chang International Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/buriram.png",
    "Autódromo Internacional Ayrton Senna": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/brazil.png",
    "Circuit of the Americas": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/cota.png",
    "Lusail International Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/lusail.png",
    "Circuito de Jerez – Ángel Nieto": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/jerez.png",
    "Bugatti Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/lemans.png",
    "Circuit de Barcelona-Catalunya": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/catalunya.png",
    "Autodromo Internazionale del Mugello": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/mugello.png",
    "Balaton Park Circuit": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/balaton.png",
    "Automotodrom Brno": "https://raw.githubusercontent.com/markthehungarian/motogp-trmnl/main/track-maps/brno.png",
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

# Lap record + track length (static - update when a new record is set)
CIRCUIT_INFO = {
    # === Next races (already filled with current records) ===
    "Automotodrom Brno": {
        "length": "5.403",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:52.303"
    },
    "TT Circuit Assen": {
        "length": "4.555",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:30.540"
    },
    "Sachsenring": {
        "length": "3.671",
        "lap_record_rider": "F. Di Giannantonio",
        "lap_record_time": "1:19.071"
    },

    # === Other 2026 circuits (pre-filled with latest known records) ===
    "Chang International Circuit": {
        "length": "4.554",
        "lap_record_rider": "M. Bezzecchi",
        "lap_record_time": "1:28.526"
    },
    "Autódromo Internacional Ayrton Senna": {
        "length": "3.835",
        "lap_record_rider": "M. Bezzecchi",
        "lap_record_time": "1:17.408"
    },
    "Circuit of the Americas": {
        "length": "5.513",
        "lap_record_rider": "F. Di Giannantonio",
        "lap_record_time": "2:00.864"
    },
    "Lusail International Circuit": {
        "length": "5.380",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:52.872"
    },
    "Circuito de Jerez – Ángel Nieto": {
        "length": "4.423",
        "lap_record_rider": "M. Márquez",
        "lap_record_time": "1:36.405"
    },
    "Bugatti Circuit": {
        "length": "4.185",
        "lap_record_rider": "M. Márquez",
        "lap_record_time": "1:29.288"
    },
    "Circuit de Barcelona-Catalunya": {
        "length": "4.657",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:38.680"
    },
    "Autodromo Internazionale del Mugello": {
        "length": "5.245",
        "lap_record_rider": "M. Bezzecchi",
        "lap_record_time": "1:43.921"
    },
    "Balaton Park Circuit": {
        "length": "4.115",
        "lap_record_rider": "M. Bezzecchi",
        "lap_record_time": "1:35.XXX"   # Update when confirmed
    },
    "Silverstone Circuit": {
        "length": "5.891",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:58.168"
    },
    "MotorLand Aragón": {
        "length": "5.077",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:46.XXX"
    },
    "Misano World Circuit Marco Simoncelli": {
        "length": "4.226",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:30.XXX"
    },
    "Red Bull Ring": {
        "length": "4.318",
        "lap_record_rider": "J. Martín",
        "lap_record_time": "1:22.643"
    },
    "Mobility Resort Motegi": {
        "length": "4.801",
        "lap_record_rider": "M. Márquez",
        "lap_record_time": "1:44.XXX"
    },
    "Pertamina Mandalika International Street Circuit": {
        "length": "4.313",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:31.XXX"
    },
    "Phillip Island Grand Prix Circuit": {
        "length": "4.448",
        "lap_record_rider": "J. Martín",
        "lap_record_time": "1:27.767"
    },
    "Petronas Sepang International Circuit": {
        "length": "5.543",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:56.337"
    },
    "Algarve International Circuit": {
        "length": "4.592",
        "lap_record_rider": "J. Martín",
        "lap_record_time": "1:38.672"
    },
    "Circuit Ricardo Tormo": {
        "length": "4.005",
        "lap_record_rider": "F. Bagnaia",
        "lap_record_time": "1:29.401"
    },

    "default": {
        "length": "N/A",
        "lap_record_rider": "TBD",
        "lap_record_time": "TBD"
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def shorten_rider_name(full_name):
    if not full_name:
        return "Unknown"
    parts = full_name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}. {parts[-1]}"
    return full_name

def get_current_season_uuid():
    try:
        seasons = requests.get(f"{BASE_URL}/results/seasons", timeout=10).json()
        for s in seasons:
            if s.get("current") or str(s.get("year")) == "2026":
                return s["id"]
        return seasons[0]["id"] if seasons else None
    except Exception as e:
        print(f"Error getting season UUID: {e}")
        return None

# ============================================================
# MAIN DATA FETCH FUNCTION (LIVE)
# ============================================================

def fetch_motogp_data():
    try:
        season_uuid = get_current_season_uuid()
        if not season_uuid:
            raise Exception("Could not determine current season")

        # Get all events and sort by date
        all_events = requests.get(
            f"{BASE_URL}/results/events?seasonUuid={season_uuid}",
            timeout=15
        ).json()

        sorted_events = sorted(all_events, key=lambda e: e.get("date_start", "9999-12-31"))

        # Find the next upcoming event
        next_event = None
        now = datetime.now()
        for e in sorted_events:
            try:
                event_date = datetime.fromisoformat(e.get("date_start", ""))
                if event_date > now:
                    next_event = e
                    break
            except:
                continue

        if not next_event and sorted_events:
            next_event = sorted_events[0]

        if not next_event:
            raise Exception("No events found")

        # Calculate round number
        round_num = sorted_events.index(next_event) + 1 if next_event in sorted_events else 0

        # Format weekend dates
        date_start_str = next_event.get("date_start", "")
        date_end_str = next_event.get("date_end", date_start_str)
        try:
            start = datetime.fromisoformat(date_start_str)
            end = datetime.fromisoformat(date_end_str)
            weekend_date = f"{start.day}–{end.day} {start.strftime('%B')}"
        except:
            weekend_date = date_start_str

        # Circuit and event info
        circuit = next_event.get("circuit", {})
        circuit_name = circuit.get("name", "Unknown Circuit")
        title = next_event.get("name", next_event.get("sponsored_name", "Next Grand Prix"))
        short_name = next_event.get("short_name", circuit_name.split()[-1].upper() if circuit_name else "TBD")

        # Get track map and lap record from static dictionaries
        info = CIRCUIT_INFO.get(circuit_name, CIRCUIT_INFO["default"])
        track_map_url = CIRCUIT_MAPS.get(circuit_name, CIRCUIT_MAPS["default"])

        # Fetch live standings (top 3 for each class)
        cat_uuids = {
            "motogp": "e8c110ad-64aa-4e8e-8a86-f2f152f6a942",
            "moto2": "549640b8-fd9c-4245-acfd-60e4bc38b25c",
            "moto3": "954f7e65-2ef2-4423-b949-4961cc603e45"
        }

        standings = {}
        for cat, cat_uuid in cat_uuids.items():
            try:
                stand_resp = requests.get(
                    f"{BASE_URL}/results/standings?seasonUuid={season_uuid}&categoryUuid={cat_uuid}",
                    timeout=10
                ).json()
                classification = stand_resp.get("classification", [])[:3]
                top3 = []
                for entry in classification:
                    rider = entry.get("rider", {})
                    top3.append({
                        "position": entry.get("position"),
                        "rider_name": shorten_rider_name(rider.get("full_name", "")),
                        "points": entry.get("points", 0)
                    })
                standings[cat] = top3
            except Exception as e:
                print(f"Error fetching {cat} standings: {e}")
                standings[cat] = []

        return {
            "next_race": {
                "round": round_num,
                "title": title,
                "date": weekend_date,
                "circuit": circuit_name,
                "short_name": short_name,
                "track_map_url": track_map_url,
                "track_length": info.get("length", "N/A"),
                "lap_record_rider": info.get("lap_record_rider", "TBD"),
                "lap_record_time": info.get("lap_record_time", "TBD")
            },
            "standings": standings,
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "message": "Failed to fetch MotoGP data – check Render logs",
            "last_updated": datetime.now().isoformat()
        }

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
@app.route("/motogp")
def motogp():
    if time.time() - CACHE["timestamp"] > CACHE_TTL or not CACHE["data"]:
        CACHE["data"] = fetch_motogp_data()
        CACHE["timestamp"] = time.time()
    return jsonify(CACHE["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
