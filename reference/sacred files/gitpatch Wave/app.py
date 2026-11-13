from flask import Flask, render_template, jsonify, request
import numpy as np
import os
import sys
import webbrowser
from threading import Timer

# --- 1. PATH HANDLING FOR PYINSTALLER ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 2. FLASK APP SETUP ---
app = Flask(__name__, 
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

# Math functions available for your equations
ALLOWED_MATH = {
    "sin": np.sin, "cos": np.cos, "tan": np.tan,
    "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi,
    "abs": np.abs, "log": np.log, "log10": np.log10, "e": np.e
}

# --- 3. ROUTES ---
@app.route('/')
def intro():
    return render_template('intro.html')

@app.route('/plotter')
def plotter():
    return render_template('index.html')

@app.route('/calculate_wave')
def calculate_wave():
    try:
        args = request.args.to_dict()
        min_x = float(args.pop('minX', -15))
        max_x = float(args.pop('maxX', 15))
        t_val = float(args.pop('t', 0))
        
        x = np.linspace(min_x, max_x, 1000)

        # Separate equations (eq0, eq1...) from variables
        equations = {k: v for k, v in args.items() if k.startswith('eq')}
        for k in equations: args.pop(k)

        # Setup evaluation context
        safe_dict = ALLOWED_MATH.copy()
        safe_dict['x'] = x
        safe_dict['t'] = t_val
        
        # Add your custom variables (A, k, w, etc.) to the math context
        for key, value in args.items():
            try: 
                # Ensure we don't overwrite core math functions
                if key not in ALLOWED_MATH:
                    safe_dict[key] = float(value)
            except: pass

        results = []
        total_y = np.zeros_like(x)
        
        for key in sorted(equations.keys()):
            clean_eq = equations[key].replace("^", "**")
            # Evaluate using your custom variable letters
            y = eval(clean_eq, {"__builtins__": None}, safe_dict)
            
            if isinstance(y, (int, float)): y = np.full_like(x, y)
            results.append(y.tolist())
            total_y += y 

        return jsonify({
            "x": x.tolist(),
            "lines": results, 
            "superposition": total_y.tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# --- 4. BROWSER AUTO-OPENER ---
def open_browser():
    webbrowser.open_new('http://127.0.0.1:8080/')

if __name__ == '__main__':
    Timer(1.5, open_browser).start()
    app.run(host='127.0.0.1', port=8080, debug=False)