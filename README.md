# NOSIDUA

NOnlinear dynamical System IDentification with Uncertainty Assessment

## Algorithm
See algorithm.pdf.

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

## Codes in src directory
* model4DVar.py

ODE system with parameters.

* discrete4DVar.py

Core Adjoint class for initial states (x_0^((0)),…,x_(N-1)^((0))) and parameters (p_0, p_1) estimation.

* discrete4DVarMain.py

Estimate initial states (x_0^((0)),…,x_(N-1)^((0))) and parameters (p_0, p_1) given observed data file.

* twinExperiment.py

First, generate observed data using given model, true initial states, and parameters with white noise. Then estimate initial states (x_0^((0)),…,x_(N-1)^((0))) and parameters (p_0, p_1) given generated observed data. Estimated result is shown compared to the true initial state and parameters.

* twinExperimentGivenData.py

Estimate initial states (x_0^((0)),…,x_(N-1)^((0) )) and parameters (p_0, p_1) given generated observed data file. Estimated result is shown compared to the true initial state and parameters.

* twinExperimentIteration.py

Same as twinExperiment.py, but iteratively conduct estimation using randomly selected initial states.

* util.py

Plotting utilities.

## Demo
You can run demo in the jupyternotes/demo.ipynb

## Usage
$ cd src

$ ./twinExperiment.py

