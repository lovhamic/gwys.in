# ⑂ Git:Patch Wave

An interactive wave-superposition plotter with a git-themed dark UI. Define one or more wave equations, control their variables with sliders, and watch them animate and combine on a canvas in real time.


## Features

- Plot any number of custom equations (e.g. `A * sin(x - t)`, `sin(k*x - w*t)`)
- Add named variables (`A`, `k`, `w`, ...) with editable min/max/slider range
- Superposition mode — overlay the sum of all waves as a highlighted white curve
- Live animation ("Live Exec") that advances `t` and re-renders continuously
- Pan (click + drag) and zoom (scroll wheel) on the canvas
- Grid overlay with live coordinate readout

---

## Project Structure

```
gitpatch Wave/
├── app.py                # Flask app: routes + wave calculation endpoint
├── requirements.txt      # Python dependencies
├── Procfile               # Process definition (for platforms like Heroku)
├── static/
│   └── script.js          # Canvas rendering, UI wiring, pan/zoom, animation loop
└── templates/
    ├── intro.html          # Animated splash/landing page ("/")
    └── index.html          # Main plotter UI ("/plotter")
```

---

## Requirements

- Python 3.9+
- pip

Dependencies (see `requirements.txt`):
- `flask` — web server and templating
- `numpy` — vectorized math for evaluating equations across the x-range
- `gunicorn` — production WSGI server (only needed if you deploy; not required to run locally)

---

## Installation

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd "gitpatch Wave"

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Usage

Run the app:

```bash
python app.py
```

This starts a local Flask server on `http://127.0.0.1:8080/` and automatically opens it in your default browser after ~1.5 seconds.

1. You'll land on the **intro screen** — click through to enter the plotter (`/plotter`).
2. Under **Functions**, click **`+ New Branch (Eq)`** to add a wave equation, e.g.:
   ```
   A * sin(x - t)
   sin(k*x - w*t) + 0.5*cos(2*x)
   ```
3. Under **Parameters**, click **`+ New Commit (Var)`** to add a variable used in your equations (e.g. `A`, `k`, `w`). Rename it, then drag its slider or type a value directly.
4. Toggle **MERGE WAVES (SUM)** to overlay the superposition (sum) of all active waves as a glowing white line.
5. Toggle **Live Exec** to animate the waves over time (advances the `t` variable each frame).
6. Toggle **Grid Mesh** to show/hide the coordinate grid.
7. **Pan**: click and drag on the canvas. **Zoom**: scroll the mouse wheel. The coordinate readout in the bottom-right follows your cursor.

### Available math functions/constants in equations

`sin`, `cos`, `tan`, `exp`, `sqrt`, `abs`, `log`, `log10`, `pi`, `e`, plus `x` (the plotted range) and `t` (time, driven by animation) — use `^` for exponents (it's converted to `**` automatically).

---

## How It Works

- **Frontend (`static/script.js` + `templates/index.html`)**: Renders a `<canvas>` and a sidebar of dynamically-added equation/variable rows. On every change (slider drag, typing, pan, zoom, animation tick), it builds a query string from the current equations, variables, `t`, and visible x-range, and calls the backend.
- **Backend (`app.py` → `/calculate_wave`)**: Parses the incoming equation strings and variables, builds an `x` array with `numpy.linspace` across the visible range, evaluates each equation over that array, and returns each line's y-values plus their superposition (sum) as JSON.
- The frontend then maps those data points to canvas pixel coordinates (accounting for pan offset and zoom scale) and draws each wave as a stroked path, with the superposition drawn on top when enabled.
- **Packaging note**: `app.py` includes a `resource_path()` helper for PyInstaller compatibility, so this app can also be bundled as a standalone desktop executable that auto-opens a browser window — not just run as a plain Flask dev server.

---

## Notes / Known Limitations

- This project is intended for **local, single-user use** (e.g. `python app.py` on your own machine). The equation field is evaluated server-side and is **not sandboxed against untrusted input** — do not expose this app on a public network or the internet without first replacing the equation evaluator with a restricted, safe parser.
- The `Procfile` and `gunicorn` dependency are placeholders for platform deployment (e.g. Heroku-style hosts) and are not required or recommended for normal local use.

---

## License

MIT License

Copyright (c) 2026 lovhamic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

