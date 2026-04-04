from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 900  # 15 minutes

# Circuit map dictionary – covers all 2026 MotoGP circuits
CIRCUIT_MAPS = {
    "Chang International Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Buriram_International_Circuit.svg/800px-Buriram_International_Circuit.svg.png",
    "Autódromo Internacional Ayrton Senna": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Aut%C3%B3dromo_Internacional_Ayrton_Senna_%28Goi%C3%A2nia%29.svg/800px-Aut%C3%B3dromo_Internacional_Ayrton_Senna_%28Goi%C3%A2nia%29.svg.png",
    "Circuit of the Americas": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/COTA_track_map.svg/800px-COTA_track_map.svg.png",
    "Lusail International Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Lusail_International_Circuit.svg/800px-Lusail_International_Circuit.svg.png",
    "Circuito de Jerez – Ángel Nieto": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Circuito_de_Jerez.svg/800px-Circuito_de_Jerez.svg.png",
    "Bugatti Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Bugatti_Circuit.svg/800px-Bugatti_Circuit.svg.png",
    "Circuit de Barcelona-Catalunya": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Circuit_de_Barcelona-Catalunya.svg/800px-Circuit_de_Barcelona-Catalunya.svg.png",
    "Autodromo Internazionale del Mugello": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Mugello_track_map.svg/800px-Mugello_track_map.svg.png",
    "Balaton Park Circuit": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Balaton_Park_Circuit.svg/800px-Balaton_Park_Circuit.svg.png",  # may need verification if image changes
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

    # Fallback for any unknown circuit name
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
