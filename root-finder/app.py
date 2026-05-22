from flask import Flask, render_template, request, jsonify
from sympy import symbols, lambdify, sympify, diff

app = Flask(__name__)

x = symbols('x')

# Root-finding methods with error handling for division by zero
def bisection_method_with_error(f, x1, x2, E=1e-5):
    iterations, errors = [], []
    while abs(x2 - x1) > E:
        x0 = (x1 + x2) / 2
        if f(x0) * f(x1) < 0:
            x2 = x0
        else:
            x1 = x0
        errors.append(abs(f(x0)))
        iterations.append((x1, x2, x0))
    return x0, iterations, errors

def newton_raphson_method_with_error(f, df, x0, E=1e-5):
    iterations, errors = [], []
    while True:
        derivative = df(x0)
        if abs(derivative) < 1e-6:  # Check if the derivative is too small
            raise ValueError(f"Derivative is too small at x = {x0}. Cannot continue Newton-Raphson method.")
        x1 = x0 - f(x0) / derivative
        error = abs(x1 - x0)
        errors.append(abs(f(x1)))
        iterations.append(x1)
        if error < E:
            break
        x0 = x1
    return x1, iterations, errors

def secant_method_with_error(f, x0, x1, E=1e-5):
    iterations, errors = [], []
    while abs(x1 - x0) > E:
        denominator = f(x1) - f(x0)
        if abs(denominator) < 1e-6:  # Check if the denominator is too small
            raise ValueError(f"Denominator is too small at x0 = {x0}, x1 = {x1}. Cannot continue Secant method.")
        x2 = x1 - (f(x1) * (x1 - x0)) / denominator
        errors.append(abs(f(x2)))
        iterations.append((x0, x1, x2))
        x0, x1 = x1, x2
    return x2, iterations, errors

def regular_false_position_with_error(f, x0, x1, E=1e-5):
    iterations, errors = [], []
    while abs(x1 - x0) > E:
        # Calculate the new root using the false position formula
        fx0 = f(x0)
        fx1 = f(x1)
        if abs(fx1 - fx0) < 1e-6:  # Prevent division by a very small number
            raise ValueError(f"Denominator is too small for Regular False Position method at x0={x0}, x1={x1}.")
        x2 = x1 - (fx1 * (x1 - x0)) / (fx1 - fx0)
        f_x2 = f(x2)
        
        # Determine which side to update
        if f_x2 * fx0 < 0:
            x1 = x2
        else:
            x0 = x2
        # Record iteration data
        errors.append(abs(f_x2))
        iterations.append((x0, x1, x2))
        if abs(f_x2) < E:  # If the function value is close to zero, stop
            break
    return x2, iterations, errors

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        equation = data['equation']
        interval = [float(i) for i in data['interval']]
        method = data['method']

        # Parse and lambdify the function
        func_expr = sympify(equation)
        f = lambdify(x, func_expr, 'numpy')
        df = lambdify(x, diff(func_expr, x), 'numpy')

        results = {}
        if method == "Bisection" or method == "All":
            root, iterations, errors = bisection_method_with_error(f, interval[0], interval[1])
            results["Bisection"] = {"root": root, "iterations": iterations, "errors": errors}

        if method == "Newton-Raphson" or method == "All":
            root, iterations, errors = newton_raphson_method_with_error(f, df, interval[0])
            results["Newton-Raphson"] = {"root": root, "iterations": iterations, "errors": errors}

        if method == "Secant" or method == "All":
            root, iterations, errors = secant_method_with_error(f, interval[0], interval[1])
            results["Secant"] = {"root": root, "iterations": iterations, "errors": errors}

        if method == "Regular False Position" or method == "All":
            root, iterations, errors = regular_false_position_with_error(f, interval[0], interval[1])
            results["Regular False Position"] = {"root": root, "iterations": iterations, "errors": errors}

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
