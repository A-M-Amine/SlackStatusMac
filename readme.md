# SlackStatusMac

> If you find this project useful, please consider giving it a ⭐️ on GitHub.

SlackStatusMac is an automated Slack status updater for macOS. It updates your Slack status according to your device’s physical location and defined working hours, ensuring accurate visibility of your work presence.

## Features

- Automatically detects your location using macOS CoreLocation services.
- Updates your Slack status to predefined values based on your current location.
- Only updates Slack when a status change occurs, optimizing API usage.
- Skips status changes on specified weekend days.
- Configuration for office locations, work hours, and weekend schedule is straightforward and extensible.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/YOURUSERNAME/SlackStatusMac.git
    cd SlackStatusMac
    ```
2. Install the required dependencies:
    ```bash
    pip install pyobjc-framework-CoreLocation requests
    ```

## Configuration

1. Open `location_slack_status.py` in a text editor.
2. Add your [Slack User OAuth Token](https://api.slack.com/authentication/oauth-v2) with `users.profile:write` scope in the `SLACK_TOKEN` variable.
3. Configure your locations in the `LOCATIONS` list:
    ```python
    LOCATIONS = [
        {
            "name": "Main Office",
            "coords": (40.7128, -74.0060),  # Example coordinates
            "status_text": "In Main Office",
            "status_emoji": ":office:"
        },
        {
            "name": "Branch Office",
            "coords": (34.0522, -118.2437),
            "status_text": "In Branch Office",
            "status_emoji": ":office_building:"
        }
        # Additional locations may be added here
    ]
    ```
4. Adjust the `ACTIVE_HOURS` and `WEEKEND_DAYS` to suit your work schedule:
    ```python
    ACTIVE_HOURS = (6, 21)   # 6:_
