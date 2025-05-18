import time
import objc
from Foundation import NSObject, NSRunLoop, NSDate
from CoreLocation import CLLocationManager
import requests
import json
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# ------------- CONFIGURATION -------------

# Replace with your Slack user OAuth token (must start with xoxp-)
SLACK_TOKEN = "xoxp-your-slack-token-here"

# List of location dictionaries. Add your own as needed!
LOCATIONS = [
    {
        "name": "Main Office",
        "coords": (40.7128, -74.0060),  # Example: New York City
        "status_text": "In Main Office",
        "status_emoji": ":office:"
    },
    {
        "name": "Branch Office",
        "coords": (34.0522, -118.2437),  # Example: Los Angeles
        "status_text": "In Branch Office",
        "status_emoji": ":office_building:"
    }
    # Add more locations as needed...
]
REMOTE_STATUS = {"status_text": "Working remotely", "status_emoji": ":house_with_garden:"}
THRESHOLD_KM = 0.2  # Distance (km) to be considered "at" an office

# Active hours (inclusive): 24-hour format, e.g., (6, 21) is 6:00 to 21:59
ACTIVE_HOURS = (6, 21)

# Days to skip (0=Monday, 1=Tuesday, ..., 6=Sunday), e.g., [5, 6] skips Saturday and Sunday
WEEKEND_DAYS = [5, 6]

# ------------- END CONFIGURATION -------------

class LocationDelegate(NSObject):
    def init(self):
        self = objc.super(LocationDelegate, self).init()
        if self is None: return None
        self.has_location = False
        return self
    def locationManager_didUpdateLocations_(self, manager, locations):
        location = locations[-1]
        self.latitude = location.coordinate().latitude
        self.longitude = location.coordinate().longitude
        self.has_location = True
    def locationManager_didFailWithError_(self, manager, error):
        self.has_location = True

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c

def get_location():
    try:
        delegate = LocationDelegate.alloc().init()
        manager = CLLocationManager.alloc().init()
        manager.setDelegate_(delegate)
        manager.requestWhenInUseAuthorization()
        manager.startUpdatingLocation()
        timeout = 10
        start = time.time()
        while not delegate.has_location and (time.time() - start < timeout):
            NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))
        manager.stopUpdatingLocation()
        if hasattr(delegate, "latitude") and hasattr(delegate, "longitude"):
            return delegate.latitude, delegate.longitude
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Location error: {e}")
    return None, None

def get_status_from_location(lat, lon):
    if lat is None or lon is None:
        return REMOTE_STATUS
    for loc in LOCATIONS:
        if haversine(lat, lon, *loc["coords"]) < THRESHOLD_KM:
            return {"status_text": loc["status_text"], "status_emoji": loc["status_emoji"]}
    return REMOTE_STATUS

def update_slack_status(text, emoji):
    try:
        url = 'https://slack.com/api/users.profile.set'
        headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}
        profile = {"status_text": text, "status_emoji": emoji, "status_expiration": 0}
        data = {"profile": json.dumps(profile)}
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if not response.ok:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Slack status update failed (HTTP error)")
        return response.ok
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Slack API error: {e}")
        return False

def main():
    today = None
    last_status = None
    while True:
        try:
            now = datetime.now()
            if now.weekday() in WEEKEND_DAYS:
                if today != now.date():
                    print(f"{now.strftime('%Y-%m-%d')} is a weekend. Skipping status updates today.")
                    today = now.date()
                time.sleep(61)
                continue
            if ACTIVE_HOURS[0] <= now.hour <= ACTIVE_HOURS[1]:
                if today != now.date():
                    last_status = None
                    today = now.date()
                lat, lon = get_location()
                status = get_status_from_location(lat, lon)
                status_tuple = (status["status_text"], status["status_emoji"])
                if last_status != status_tuple:
                    if update_slack_status(status["status_text"], status["status_emoji"]):
                        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} Status changed to: {status['status_text']} {status['status_emoji']}")
                        last_status = status_tuple
                    else:
                        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} Slack status update failed, will retry.")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] General error: {e}")
        time.sleep(61)

if __name__ == "__main__":
    main()
