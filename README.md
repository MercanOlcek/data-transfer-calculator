# Data Transfer Time Calculator & IP Tracker

A simple Python terminal (TUI) app that calculates estimated data transfer time and tracks IP information.  
**Developed by Mercan Ölçek.**

## Screenshots & Descriptions

![Screenshot 1](screenshots/Screenshot%20From%202026-11-21%2018-14-27.png)

**Description:** Main TUI screen showing the IP tracker, calculator panel, and controls.

![Screenshot 2](screenshots/Screenshot%20From%202026-11-21%2018-14-45.png)

**Description:** IP tracker view showing local/public IP details and status information.

![Screenshot 3](screenshots/Screenshot%20From%202026-11-21%2018-15-02.png)

**Description:** Calculator input flow where the user enters data size (TB) and internet speed (Mbit/s).

![Screenshot 4](screenshots/Screenshot%20From%202026-11-21%2018-15-08.png)

**Description:** Calculation result displayed in English as days, hours, minutes, and seconds.

## Features

- **Data Transfer Time Calculator**
  - Enter data size in **TB** (terabytes).
  - Enter internet speed in **Mbit/s**.
  - Get the estimated transfer time in **days, hours, minutes, seconds**.
- **IP Tracker**
  - Shows **local IP**.
  - Fetches **public IP** details (location, ISP, timezone).
  - Refresh IP info and keep a small in-session IP check history.
- **Terminal UI (curses)**
  - Runs inside an interactive terminal using Python's built-in `curses` library.

## Formula

Calculated in `trans.py`:

1. `bits = TB * 1024^4 * 8`
2. `total_seconds = bits / (Mbps * 1,000,000)`
3. Convert seconds to `days, hours, minutes, seconds`

Example: `0 days, 1 hours, 30 minutes, 0 seconds`

## Controls

- `C` - Calculate transfer time
- `R` - Refresh IP information
- `Q` - Quit
- `Esc` - Cancel input
- `Enter` - Confirm input / calculate

## Run

```bash
cd /home/mercan/mega
./megagigawhat/bin/python app.py
```
