import numpy as np
from scipy.interpolate import CubicSpline
from scipy.integrate import quad
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Generate synthetic data (replace with actual data if available)
def true_model(t, a, b):
    return np.exp(a * t) + b

# Generate noisy observations
np.random.seed(42) 
a_true, b_true = 0.5, 2.0
t = np.linspace(0, 10, 100)
y_true = true_model(t, a_true, b_true)
noise = np.random.normal(0, 0.5, y_true.shape)
y_noisy = y_true + noise

# Spline approximation (Choice 1: conventional collocation method)
def spline_approximation(t, c, knots):
    cs = CubicSpline(knots, c)
    return cs(t)

# Define the ODE residual term
def ode_residual(t, c, knots, a, b):
    cs = CubicSpline(knots, c)
    dydt = cs.derivative()(t)
    return dydt - (a * cs(t) + b)

# Objective function to minimize
def objective_function(params, t, y_noisy, knots, lambda_reg):
    a, b = params[:2]
    c = params[2:]
    
    # Calculate spline approximation
    y_estimated = spline_approximation(t, c, knots)
    
    # Data fitting term
    error = np.sum((y_noisy - y_estimated) ** 2) / len(y_noisy)
    
    # ODE residual term
    residual = lambda t: ode_residual(t, c, knots, a, b) ** 2
    ode_term, _ = quad(residual, t[0], t[-1])
    
    return error + lambda_reg * ode_term

# Initial guess for parameters
knots = np.linspace(0, 10, 10)  # Number of knots can be adjusted
initial_c = np.ones(len(knots))
initial_guess = np.array([1.0, 1.0] + list(initial_c))

# Regularization parameter
lambda_reg = 0.1

# Perform the optimization
result = minimize(objective_function, initial_guess, args=(t, y_noisy, knots, lambda_reg))
estimated_params = result.x

# Extract the estimated parameters
a_est, b_est = estimated_params[:2]
c_est = estimated_params[2:]

# Print the estimated parameters
print("Estimated parameters:")
print("a:", a_est)
print("b:", b_est)

# Plot the results
y_estimated = spline_approximation(t, c_est, knots)
plt.plot(t, y_true, label='True Data', color='blue')
plt.plot(t, y_noisy, 'o', label='Noisy Data', color='red')
plt.plot(t, y_estimated, label='Estimated Model', color='green')
plt.legend()
plt.xlabel('Time')
plt.ylabel('y')
plt.title('Parameter Estimation of ODE using Spline Approximation')
plt.show()
