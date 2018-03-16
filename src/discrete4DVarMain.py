#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 17:01:40 2017

@author: yk
"""

import numpy as np

import model4DVar
import experimentUtil

def main():
    N = 5
    M = 2
    lorenz = model4DVar.Lorenz96(N, M)

    true_p = np.array([8., 1.])
    obs_variance = 1.
    obs_iteration = 5
    dt = 0.01
    spinup = 1 * 365 * 0.2
    T = 1.
    generation_seed = 1
    obs_file = "../data/" + lorenz.__class__.__name__ + "/N_"\
           + str(N) + "/p_"  + "_".join(list(map(str, true_p)))\
           + "/obsvar_" + str(obs_variance) +  "/obsiter_" + str(obs_iteration) + "/dt_" + str(dt)\
           + "/spinup_" + str(spinup) + "/T_" + str(T) + "/seed_" + str(generation_seed) + "/observed.tsv"

    trials = 20
    #    bounds = ((None, None), (None, None), (None, None), (None, None), (None, None), (0, None), (None, None))
    bounds=None
    initial_guess_bounds = ((-10, 10), (-10, 10), (-10, 10), (-10, 10), (-10, 10), (0, 15), (0, 2))

    experimentUtil.assimilate(lorenz, obs_file, obs_variance, dt, trials, bounds, initial_guess_bounds, missing_values={'nan'})
    
#%%
if __name__ == "__main__":
    main()
