# TrainWatcher

A lightweight server that provides real-time NYC subway arrival times via a REST API. Designed to run on a Raspberry Pi and integrate with iOS Shortcuts for Siri voice queries.

## Features

- Real-time train arrivals from MTA GTFS-RT feeds
- Filter by direction (uptown/downtown) and train line
- Text responses optimized for Siri text-to-speech
- JSON output available for other integrations

## Quick Start

```bash
# Clone and install
git clone https://github.com/drewwileyroberts/trainWatcher.git
cd trainWatcher
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python server.py
```

Server starts at `http://localhost:5050`

## API

### GET /next-train

Returns upcoming train arrivals.

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| direction | uptown, downtown | both | Filter by direction |
| train | A, B, C | all | Filter by train line |
| format | text, json | text | Response format |

**Examples:**
```
/next-train                          # All trains, both directions
/next-train?direction=uptown         # Uptown trains only
/next-train?train=A                  # A trains only
/next-train?train=B&direction=downtown  # Downtown B trains
/next-train?format=json              # JSON response
```

**Text response:**
```
Uptown: A train in 3 minutes, C train in 7 minutes. Downtown: B train in 2 minutes.
```

**JSON response:**
```json
{
  "northbound": [{"route": "A", "minutes": 3, "time": "5:42 PM"}],
  "southbound": [{"route": "B", "minutes": 2, "time": "5:40 PM"}]
}
```

## Configuration

The default station is **86th St - Central Park West** (A/B/C trains).

To change the station, edit `mta.py`:
- `STOP_ID`: The MTA station ID (find IDs in [GTFS static data](https://atisdata.s3.amazonaws.com/pub/GTFS/gtfs-nyct-subway.zip))
- `FEEDS`: Add/remove feed URLs based on which lines serve your station
- `RELEVANT_ROUTES`: The train lines to include

MTA feed URLs: https://api.mta.info/

## Deployment on Raspberry Pi

1. Copy files to Pi and install in a virtual environment
2. Create a systemd service:

```ini
[Unit]
Description=Train Watcher MTA API Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/trainWatcher
ExecStart=/home/pi/trainWatcher/venv/bin/python server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl enable trainwatcher
sudo systemctl start trainwatcher
```

## iOS Shortcut Setup

1. Create new Shortcut
2. Add "Get Contents of URL" action with your Pi's URL
3. Add "Speak Text" action with the response
4. Add to Siri with your trigger phrase

## License

MIT
