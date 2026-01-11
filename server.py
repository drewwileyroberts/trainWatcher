from flask import Flask, request, jsonify
from mta import get_arrivals, format_for_siri

app = Flask(__name__)


@app.route("/next-train", methods=["GET"])
def next_train():
    """
    Get next train arrivals at 86th St - Central Park West.

    Query params:
        direction: 'uptown', 'downtown', or omit for both
        train: 'A', 'B', 'C', or omit for all trains
        format: 'json' for raw data, omit for Siri-friendly text
    """
    direction_param = request.args.get("direction", "").lower()
    train_param = request.args.get("train", "").upper()
    output_format = request.args.get("format", "text").lower()

    # Map direction param to internal representation
    direction = None
    if direction_param in ("uptown", "northbound", "north"):
        direction = "northbound"
    elif direction_param in ("downtown", "southbound", "south"):
        direction = "southbound"

    # Filter by specific train line if requested
    routes = None
    if train_param in ("A", "B", "C"):
        routes = {train_param}

    arrivals = get_arrivals(routes=routes)

    if output_format == "json":
        return jsonify(arrivals)

    # Return plain text for Siri
    response_text = format_for_siri(arrivals, direction)
    return response_text, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
