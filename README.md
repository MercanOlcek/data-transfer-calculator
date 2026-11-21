# Data Transfer Time Calculator & IP Tracker

A simple Python terminal (TUI) app that calculates estimated data transfer time and tracks IP information.  
**Developed by Mercan Olcek.**



![Screenshot 1](screenshots/Screenshot%20From%202026-11-21%2018-46-27.png)

**Description:** Main TUI screen showing the IP tracker, data transfer calculator, and controls in English.

![Screenshot 2](screenshots/Screenshot%20From%202026-11-21%2018-46-31.png)

**Description:** Calculator input screen where the user enters data size and internet speed.

![Screenshot 3](screenshots/Screenshot%20From%202026-11-21%2018-46-35.png)

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
