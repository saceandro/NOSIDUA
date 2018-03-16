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
    generation_trials = 20
    trials = 20
    
    lorenz = model4DVar.Lorenz96(N, M)
    x0 = lorenz96_x0_generating_func(N, true_p, np.random.RandomState(0))

#    bounds = ((None, None), (None, None), (None, None), (None, None), (None, None), (0, None), (None, None))
    bounds=None
    initial_guess_bounds = ((-10, 10), (-10, 10), (-10, 10), (-10, 10), (-10, 10), (0, 15), (0, 2))
    
    experimentUtil.twin_experiment_with_data_generation_samex0_iteration(lorenz, x0, true_p, obs_variance, obs_iteration, dt, spinup, T, generation_trials, trials, bounds, initial_guess_bounds)
#%%
if __name__ == "__main__":
    main()
