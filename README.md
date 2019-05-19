# NOSIDUA

NOnlinear dynamical System IDentification with Uncertainty Assessment

## Formulation and algorithm
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

Core Adjoint class for initial states and parameters estimation.

* discrete4DVarMain.py

Estimate initial states and parameters given observed data file.

* twinExperiment.py

First, generate observed data using given model, true initial states, and parameters with white noise. Then estimate initial states and parameters given generated observed data. Estimated result is shown compared to the true initial state and parameters.

* twinExperimentGivenData.py

Estimate initial states and parameters given generated observed data file. Estimated result is shown compared to the true initial state and parameters.

* twinExperimentIteration.py

Same as twinExperiment.py, but iteratively conduct estimation using randomly selected initial states.

* util.py

Plotting utilities.

## Demo
You can run demo in the jupyternotes/demo.ipynb

## Usage
$ cd src

$ ./twinExperiment.py

## Extract from Output
<pre>
estiamted initial state:	 [ 1.43098772  4.78592118  2.83295792 -3.17975449 -0.29395921]
true initial state:	 [ 1.23733235  4.84913358  3.32737079 -2.91346056 -0.66036993]
1 sigma confidence interval:	 [0.48049188 0.41684461 0.41306967 0.52146088 0.22912386]

estimated parameters:	 [8.08144432 0.95417444]
true parameters:	 [8. 1.]
1 sigma confidence interval:	 [0.39461939 0.0413528 ]

initial state and parameter covariance:
 [[ 0.23087245 -0.10594872  0.09820673  0.08257987 -0.00864176 -0.01539146
  -0.00323906]
 [-0.10594872  0.17375943 -0.06010525  0.00440559  0.04264048 -0.0341914
  -0.00690069]
 [ 0.09820673 -0.06010525  0.17062655  0.06527976 -0.0561734   0.02362571
   0.00402759]
 [ 0.08257987  0.00440559  0.06527976  0.27192145 -0.02736121 -0.12720691
   0.00510177]
 [-0.00864176  0.04264048 -0.0561734  -0.02736121  0.05249774 -0.02942388
  -0.00448569]
 [-0.01539146 -0.0341914   0.02362571 -0.12720691 -0.02942388  0.15572446
  -0.0050174 ]
 [-0.00323906 -0.00690069  0.00402759  0.00510177 -0.00448569 -0.0050174
   0.00171005]]
mean RMSE around interval center:  0.1860385076639236
</pre>
