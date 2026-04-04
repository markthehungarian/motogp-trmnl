from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900  # 15 minutes

# Circuit map dictionary (expand as needed)
CIRCUIT_MAPS = {
    "Circuit of the Americas": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/COTA_track_map.svg/800px-COTA_track_map.svg.png",
    "Autódromo Internacional do Algarve": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Portimao_track_map.svg/800px-Portimao_track_map.svg.png",
    "Mugello Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Mugello_track_map.svg/800px-Mugello_track_map.svg.png",
    # Add more from https://en.wikipedia.org/wiki/List_of_Grand_Prix_motorcycle_circuits
    "default": "https://via.placeholder.com/400x200/333/fff?text=Track+Map+Coming+Soon"
}

def get_current_season_year():
    try:
        seasons = requests.get("https://api.motogp.pulselive.com/motogp/v1/results/seasons").json()
        for s in seasons:
            if s.get("current") or s.get("year") == datetime.now().year:
                return s.get("year")
        return datetime.now().year  # fallback to current year
    except:
        return 2026  # fallback for now

def fetch_motogp_data():
    season_year = get_current_season_year()
    base = "https://api.motogp.pulselive.com/motogp/v1"

    try:
        print(f"Fetching data for season {season_year}")  # visible in Render logs

        # Get upcoming events
        events_url = f"{base}/results/events?season={season_year}"
        events_resp = requests.get(events_url, timeout=10).json()
        
        # Filter for upcoming (or use status if available)
        upcoming = [e for e in events_resp if not e.get("finished", False) and not e.get("completed", False)]
        next_event = upcoming[0] if upcoming else events_resp[0] if events_resp else {}

        # Get standings (this endpoint may need adjustment)
        standings_url = f"{base}/results/standings?season={season_year}"
        standings_resp = requests.get(standings_url, timeout=10).json()

        # Build simplified data
        data = {
            "next_race": {
                "title": next_event.get("name") or next_event.get("title", "Next Race"),
                "date": next_event.get("date_start") or next_event.get("date", "TBD"),
                "circuit": next_event.get("circuit", {}).get("name") or next_event.get("circuit_name", "Unknown"),
                "track_map_url": CIRCUIT_MAPS.get(
                    next_event.get("circuit", {}).get("name") or next_event.get("circuit_name"), 
                    CIRCUIT_MAPS["default"]
                )
            },
            "standings": {
                "motogp": [r for r in standings_resp if r.get("category") in ["MotoGP", "motogp"]][:8],
                "moto2": [r for r in standings_resp if r.get("category") in ["Moto2", "moto2"]][:6],
                "moto3": [r for r in standings_resp if r.get("category") in ["Moto3", "moto3"]][:6]
            },
            "last_updated": datetime.now().isoformat(),
            "season": season_year
        }
        return data

    except Exception as e:
        print(f"Error fetching MotoGP data: {str(e)}")  # This will show in Render Logs
        return {
            "error": str(e),
            "message": "Failed to fetch from MotoGP API - check Render logs for details",
            "last_updated": datetime.now().isoformat(),
            "season": season_year
        }

@app.route("/motogp")
def motogp():
    if time.time() - CACHE["timestamp"] > CACHE_TTL or not CACHE["data"]:
        CACHE["data"] = fetch_motogp_data()
        CACHE["timestamp"] = time.time()
    return jsonify(CACHE["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
