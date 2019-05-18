#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 17:01:40 2017

@author: yk
"""

import numpy as np

import model4DVar
import experimentUtil

def lorenz96_x0_generating_func(N, params, rng):
    x0 = params[0] * np.ones(N)
    x0[rng.randint(N)] += 0.1 * rng.randn()
    return x0
    
def main():
    N = 5
    M = 2
    true_p = np.array([8., 1.])
    obs_variance = 1.
    obs_iteration = 5
    dt = 0.01
    
    year = 1
    day = 365 * year
    spinup = day * 0.2
    
    T = 1.
    generation_trials = 2
    trials = 1
    
    lorenz = model4DVar.Lorenz96(N, M)    

#    bounds = ((None, None), (None, None), (None, None), (None, None), (None, None), (0, None), (None, None))
    bounds=None
    initial_guess_bounds = ((-10, 10), (-10, 10), (-10, 10), (-10, 10), (-10, 10), (0, 15), (0, 2))

    experimentUtil.twin_experiment_with_data_generation_differentx0_iteration(lorenz, true_p, obs_variance, obs_iteration, dt, spinup, T, lorenz96_x0_generating_func, generation_trials, trials, bounds, initial_guess_bounds)

#%%
if __name__ == "__main__":
    main()
