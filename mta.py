import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime
from typing import Optional

# 86th St - Central Park West
STOP_ID = "A24"

FEEDS = {
    "ACE": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "BDFM": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
}

# Routes that stop at 86th St CPW
RELEVANT_ROUTES = {"A", "B", "C"}


def fetch_feed(url: str) -> Optional[gtfs_realtime_pb2.FeedMessage]:
    """Fetch and parse a GTFS-RT feed."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
    except Exception as e:
        print(f"Error fetching feed {url}: {e}")
        return None


def get_arrivals(routes: Optional[set] = None) -> dict:
    """Get upcoming train arrivals at 86th St CPW.

    Args:
        routes: Optional set of route IDs to filter (e.g., {"A"}, {"B", "C"}).
                If None, returns all relevant routes (A, B, C).
    """
    now = datetime.now()
    arrivals = {"northbound": [], "southbound": []}

    # Use provided routes or default to all
    filter_routes = routes if routes else RELEVANT_ROUTES

    for feed_name, feed_url in FEEDS.items():
        feed = fetch_feed(feed_url)
        if not feed:
            continue

        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue

            trip = entity.trip_update
            route_id = trip.trip.route_id

            if route_id not in filter_routes:
                continue

            for stop_time in trip.stop_time_update:
                stop_id = stop_time.stop_id

                # Check if this is our station (A24N = northbound, A24S = southbound)
                if not stop_id.startswith(STOP_ID):
                    continue

                # Get arrival time (prefer arrival, fall back to departure)
                if stop_time.HasField("arrival"):
                    arrival_time = stop_time.arrival.time
                elif stop_time.HasField("departure"):
                    arrival_time = stop_time.departure.time
                else:
                    continue

                arrival_dt = datetime.fromtimestamp(arrival_time)
                minutes_away = int((arrival_dt - now).total_seconds() / 60)

                # Only include trains arriving in the future
                if minutes_away < 0:
                    continue

                direction = "northbound" if stop_id.endswith("N") else "southbound"
                arrivals[direction].append({
                    "route": route_id,
                    "minutes": minutes_away,
                    "time": arrival_dt.strftime("%-I:%M %p"),
                })

    # Sort by arrival time
    arrivals["northbound"].sort(key=lambda x: x["minutes"])
    arrivals["southbound"].sort(key=lambda x: x["minutes"])

    return arrivals


def format_for_siri(arrivals: dict, direction: Optional[str] = None) -> str:
    """Format arrivals as a Siri-friendly spoken response."""
    parts = []

    directions = [direction] if direction else ["northbound", "southbound"]

    for d in directions:
        if d not in arrivals:
            continue

        trains = arrivals[d][:3]  # Top 3 trains per direction

        if not trains:
            parts.append(f"No {d} trains scheduled.")
            continue

        dir_label = "Uptown" if d == "northbound" else "Downtown"

        train_strs = []
        for t in trains:
            if t["minutes"] == 0:
                train_strs.append(f"{t['route']} train arriving now")
            elif t["minutes"] == 1:
                train_strs.append(f"{t['route']} train in 1 minute")
            else:
                train_strs.append(f"{t['route']} train in {t['minutes']} minutes")

        parts.append(f"{dir_label}: {', '.join(train_strs)}.")

    return " ".join(parts) if parts else "No train information available."


if __name__ == "__main__":
    # Test the module directly
    arrivals = get_arrivals()
    print(format_for_siri(arrivals))
