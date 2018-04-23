**4D-Var (Adjoint and Second order adjoint method)**
---
## Requirements
Python3
Scipy, Numpy, Matplotlib

## Write your model
Edit src/model4DVar.py and fill in the blanks of calc_dxdt, calc_jacobian, and calc_hessian methods in the Model class.

## Assimilate your model with data
Use experimentUtil.assimilate to assimilate your model with data.
In this method, 'bounds' is the initial state bounds followed by parameter bounds used for L-BFGS-B minimizer.
Furthermore, you can use initial_guess_bounds to restrict the initial guess.
Then, initial guesses for initial state and parameters will be generated using uniform distribution within initial_guess_bounds in each trials.
An example of Lorenz96 data assimilation can be seen in src/discrete4DVarMain.py.
