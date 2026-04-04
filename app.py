from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900  # 15 minutes cache

# Circuit name → track map image URL (from Wikipedia — add more as needed)
CIRCUIT_MAPS = {
    "Circuit of the Americas": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/COTA_track_map.svg/800px-COTA_track_map.svg.png",
    "Autódromo Internacional do Algarve": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Portimao_track_map.svg/800px-Portimao_track_map.svg.png",
    "Mugello Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Mugello_track_map.svg/800px-Mugello_track_map.svg.png",
    # Add more circuits here from Wikipedia's List of Grand Prix motorcycle circuits page
    "default": "https://via.placeholder.com/400x200/333/fff?text=Track+Map+Coming+Soon"
}

def fetch_motogp_data():
    season_year = 2026  # Update this each year or fetch dynamically
    base = "https://api.motogp.pulselive.com/motogp/v1"

    try:
        # Next/upcoming events
        events = requests.get(f"{base}/results/events?season={season_year}&status=upcoming").json()
        next_event = events[0] if events else {"title": "No upcoming race", "circuit": "N/A"}

        # Standings (simplified)
        standings_resp = requests.get(f"{base}/results/standings?season={season_year}").json()

        data = {
            "next_race": {
                "title": next_event.get("title", "Next Race"),
                "date": next_event.get("date", "TBD"),
                "circuit": next_event.get("circuit", "Unknown"),
                "track_map_url": CIRCUIT_MAPS.get(next_event.get("circuit"), CIRCUIT_MAPS["default"])
            },
            "standings": {
                "motogp": [r for r in standings_resp if r.get("category") == "MotoGP"][:8],
                "moto2": [r for r in standings_resp if r.get("category") == "Moto2"][:6],
                "moto3": [r for r in standings_resp if r.get("category") == "Moto3"][:6]
            },
            "last_updated": datetime.now().isoformat()
        }
        return data
    except Exception as e:
        return {"error": str(e), "last_updated": datetime.now().isoformat()}

@app.route("/motogp")
def motogp():
    if time.time() - CACHE["timestamp"] > CACHE_TTL or not CACHE["data"]:
        CACHE["data"] = fetch_motogp_data()
        CACHE["timestamp"] = time.time()
    return jsonify(CACHE["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
