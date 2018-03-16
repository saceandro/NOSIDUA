#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 17:16:51 2018

@author: konta
"""
import numpy as np
import math
import sys
import pathlib

import util
import discrete4DVar

def twin_experiment_given_data(model, true_params, tob, obs, obs_variance, dt, trials=10, bounds=None, initial_guess_bounds=None):
    """
    Conduct twin experiment given true parameters (true_params), true orbit (tob), and observation (obs)
    """
    __N = model.N
    __steps = len(tob)
    __t = np.array([dt*i for i in range(__steps)])
    
    if __N >= 3:
        __obs_mask = np.array(list(map(np.isnan, obs)))
        __obs_mask_row = [all(~__obs_mask[i,:3]) for i in range(__steps)]
        util.plot_orbit2_3d(tob, obs[__obs_mask_row], "true orbit", "observed")
    
    __rng = np.random.RandomState(0)
    __scheme = discrete4DVar.Adjoint(model, dt, __t, obs_variance, obs, __rng)
    __true_cost = __scheme.cost(np.concatenate((tob[0], true_params)))
    
    __minres = __scheme.twin_experiment(__true_cost, tob[0], true_params, trials, bounds, initial_guess_bounds)
    if (__minres == None):
        return
    
    if __minres.success:
        print('\n\nCost minimization succeeded.\n', file=sys.stderr)
    else:
        print('\n\nCost minimization failed.\n', file=sys.stderr)
    print('Cause of the minimizer termination:\t', __minres.message, file=sys.stderr)
    print('final jacobian:\t', __minres.jac, file=sys.stderr)
    print('optimal cost:\t', __minres.fun, file=sys.stderr)
    print('true cost:\t', __true_cost, file=sys.stderr)
    
    print('estiamted initial state:\t', __minres.x[:__N])
    print('true initial state:\t', tob[0])
    print('1 sigma confidence interval:\t', __scheme.sigma[:__N])
    print('\nestimated parameters:\t', __minres.x[__N:])
    print('true parameters:\t', true_params)
    print('1 sigma confidence interval:\t', __scheme.sigma[__N:])
    print("\ninitial state and parameter covariance:\n", __scheme.cov)
    
    util.plot_orbit3_1d(__t, tob, __scheme.x, obs)
    util.plot_orbit2_3d(tob, __scheme.x, 'true orbit', 'assimilated')
    util.plot_RMSE(__t, tob, __scheme.x)
    print ("mean RMSE around interval center: ", util.calc_RMSE(__t, tob, __scheme.x), file=sys.stderr)


def twin_experiment_given_data_file(model, true_params, true_orbit_file, observed_file, obs_variance, dt, T, trials=10, bounds=None, initial_guess_bounds=None, missing_values={'NA', 'nan'}):
    """
    Conduct twin experiment given true parameters (true_params), true_orbit_file, and observation_file
    """
    __steps = int(T/dt) + 1
    __tob = np.genfromtxt(true_orbit_file, max_rows=__steps)
    __obs = np.genfromtxt(observed_file, missing_values=missing_values, max_rows=__steps)
    twin_experiment_given_data(model, true_params, __tob, __obs, obs_variance, dt, trials, bounds, initial_guess_bounds)


def twin_experiment_with_data_generation(model, true_params, obs_variance, obs_iteration, dt, spinup, T, x0_generating_func, generation_seed, trials=10, bounds=None, initial_guess_bounds=None):
    """
    Conduct twin experiment given true parameters (true_params) with generating observation data.
    spinup is the duration required for model spin-up.
    T is the data generating duration.
    x0_generating_func(N, true_params, rng) is a function to generate x[0] preceding spin-up.
    """
    __N = model.N
    __spinup_steps = int(spinup/dt)
    __total_T = spinup + T
    __t = np.concatenate((np.arange(0., __total_T, dt), np.array([__total_T])))
    __steps = len(__t)
    
    __rng = np.random.RandomState(generation_seed)
    __scheme = discrete4DVar.Adjoint(model, dt, __t, obs_variance, np.zeros((__steps, __N)), __rng)
    __scheme.p = true_params    
    __scheme.x[0] = x0_generating_func(__N, true_params, __rng)
    __true_orbit = __scheme.orbit()[__spinup_steps:]
    __observed = __true_orbit + math.sqrt(obs_variance) * __rng.randn(__steps-__spinup_steps, __N)

    # simulate sparse observation and missing values
    for __i in range(0, __steps-__spinup_steps-1, obs_iteration):
        __mask = __rng.randint(__N, size=__N)
        for __j in range(__N):
            if __mask[__j] == 0:
                __observed[__i, __j] = np.nan
        for __k in range(1, obs_iteration):
            __observed[__i+__k] = np.nan

    __path = "../data/" + model.__class__.__name__ + "/N_"\
           + str(__N) + "/p_"  + "_".join(list(map(str, true_params)))\
           + "/obsvar_" + str(obs_variance) +  "/obsiter_" + str(obs_iteration) + "/dt_" + str(dt)\
           + "/spinup_" + str(spinup) + "/T_" + str(T) + "/seed_" + str(generation_seed) + "/"
    pathlib.Path(__path).mkdir(parents=True, exist_ok=True)
    np.savetxt(__path + "true.tsv", __true_orbit, delimiter='\t')
    np.savetxt(__path + "observed.tsv", __observed, delimiter='\t')
    
    twin_experiment_given_data(model, true_params, __true_orbit, __observed, obs_variance, dt, trials, bounds, initial_guess_bounds)


def twin_experiment_with_data_generation_differentx0_iteration(model, true_params, obs_variance, obs_iteration, dt, spinup, T, x0_generating_func, generation_trials=10, trials=10, bounds=None, initial_guess_bounds=None):
    """
    Conduct twin experiment given true parameters (true_params) with generating observation data 'generation_trials' times.
    Observation data is generated for different initial x[0] every time.
    See twin_experiment_with_data_generation for the details.
    """
    for __i in range(generation_trials):
        print("data: ", __i)
        twin_experiment_with_data_generation(model, true_params, obs_variance, obs_iteration, dt, spinup, T, x0_generating_func, __i, trials, bounds, initial_guess_bounds)


def __twin_experiment_given_data_accum_minres(model, true_params, tob, obs, obs_variance, dt, x0_p_acc, cov_acc, trials=10, bounds=None, initial_guess_bounds=None):
    __N = model.N
    __M = model.M
    __steps = len(tob)
    __t = np.array([dt*i for i in range(__steps)])
    
    if __N >= 3:
        __obs_mask = np.array(list(map(np.isnan, obs)))
        __obs_mask_row = [all(~__obs_mask[i,:3]) for i in range(__steps)]
        util.plot_orbit2_3d(tob, obs[__obs_mask_row], "true orbit", "observed")
    
    __rng = np.random.RandomState(0)
    __scheme = discrete4DVar.Adjoint(model, dt, __t, obs_variance, obs, __rng)
    __true_cost = __scheme.cost(np.concatenate((tob[0], true_params)))
    
    __minres = __scheme.twin_experiment(__true_cost, tob[0], true_params, trials, bounds, initial_guess_bounds)

    if __minres != None and __minres.success:
        x0_p_acc = np.concatenate((x0_p_acc, __minres.x.reshape(1, __N + __M)))
        cov_acc  = np.concatenate((cov_acc , np.reshape(__scheme.cov, (1, __N + __M, __N + __M))))
    return x0_p_acc, cov_acc    

def twin_experiment_with_data_generation_samex0_iteration(model, x0, true_params, obs_variance, obs_iteration, dt, spinup, T, generation_trials=10, trials=10, bounds=None, initial_guess_bounds=None):
    """
    Conduct twin experiment given true parameters (true_params) with generating observation data.
    spinup is the duration required for model spin-up.
    T is the data generating duration.
    x0_generating_func(N, true_params, rng) is a function to generate x[0] preceding spin-up.
    Observation data is generated 'generation_trials' times.
    x[0] is the same through every observation data.
    Experimental sample covariance and mean second order adjoint covariance is reported.
    """
    __N = model.N
    __M = model.M
    __spinup_steps = int(spinup/dt)
    __total_T = spinup + T
    __t = np.concatenate((np.arange(0., __total_T, dt), np.array([__total_T])))
    __steps = len(__t)
    
    __rng_onetime = np.random.RandomState(0)
    __scheme = discrete4DVar.Adjoint(model, dt, __t, obs_variance, np.zeros((__steps, __N)), __rng_onetime)
    __scheme.p = true_params    
    __scheme.x[0] = x0
    __true_orbit = __scheme.orbit()[__spinup_steps:]
    __maskall = __rng_onetime.randint(__N, size=(__steps, __N))

    __x0_p_acc = np.empty((0, __N + __M))
    __cov_acc  = np.empty((0, __N + __M, __N + __M))
    
    for __obs_variation_seed in range(generation_trials):
        print("obs_variation_seed:", __obs_variation_seed)
        __rng = np.random.RandomState(__obs_variation_seed)
        __observed = __true_orbit + math.sqrt(obs_variance) * __rng.randn(__steps-__spinup_steps, __N)

        # simulate sparse observation and missing values
        for __i in range(0, __steps-__spinup_steps-1, obs_iteration):
            for __j in range(__N):
                if __maskall[__i, __j] == 0:
                    __observed[__i, __j] = np.nan
            for __k in range(1, obs_iteration):
                __observed[__i+__k] = np.nan
    
        __path = "../data/" + model.__class__.__name__ + "/N_"\
               + str(__N) + "/p_"  + "_".join(list(map(str, true_params)))\
               + "/obsvar_" + str(obs_variance) +  "/obsiter_" + str(obs_iteration) + "/dt_" + str(dt)\
               + "/spinup_" + str(spinup) + "/T_" + str(T) + "/seed_0/obsvarseed_" + str(__obs_variation_seed) + "/"
        pathlib.Path(__path).mkdir(parents=True, exist_ok=True)
        np.savetxt(__path + "true.tsv", __true_orbit, delimiter='\t')
        np.savetxt(__path + "observed.tsv", __observed, delimiter='\t')
        
        __x0_p_acc, __cov_acc = __twin_experiment_given_data_accum_minres(model, true_params, __true_orbit, __observed, obs_variance, dt, __x0_p_acc, __cov_acc, trials, bounds, initial_guess_bounds)
        
    __cov_exp = np.cov(__x0_p_acc.transpose())
    print("experimental sample (x0, p) covariance:\n", __cov_exp)
    __cov_mean = np.mean(__cov_acc, axis=0)
    print("\nmean second order adjoint (x0, p) covariance:\n", __cov_mean)
    print("absolute error:", __cov_mean - __cov_exp)
    print("relative error:", (__cov_mean - __cov_exp)/__cov_exp)
    

#%%
def assimilate(model, observed_file, obs_variance, dt, trials=10, bounds=None, initial_guess_bounds=None, missing_values={'NA', 'nan'}):
    """
    Conduct data assimilation given observation_file (row: each time (every dt) observed x[t]).
    Missing data appear as string in missing_values in the observed_file.
    """
    __N = model.N
    __obs = np.genfromtxt(observed_file, missing_values=missing_values)
    __steps = len(__obs)
    __t = np.array([dt*i for i in range(__steps)])
        
    __rng = np.random.RandomState(0)

    __scheme = discrete4DVar.Adjoint(model, dt, __t, obs_variance, __obs, __rng)
    
    __minres = __scheme.assimilate(trials, bounds, initial_guess_bounds)
    if (__minres == None):
        return
    
    if __minres.success:
        print('\n\nCost minimization succeeded.\n', file=sys.stderr)
    else:
        print('\n\nCost minimization failed.\n', file=sys.stderr)
    print('Cause of the minimizer termination:\t', __minres.message, file=sys.stderr)
    print('final jacobian:\t', __minres.jac, file=sys.stderr)
    print('optimal cost:\t', __minres.fun, file=sys.stderr)
    
    print('estiamted initial state:', __minres.x[:__N])
    print('1 sigma confidence interval:\t', __scheme.sigma[:__N])
    print('\nestimated parameters:\t', __minres.x[__N:])
    print('1 sigma confidence interval:\t', __scheme.sigma[__N:])
    print("\ninitial state and parameter covariance:\n", __scheme.cov)
    
    util.plot_orbit2_1d(__t, __scheme.x, __obs)
    if __N >= 3:
        __obs_mask = np.array(list(map(np.isnan, __obs)))
        __obs_mask_row = [all(~__obs_mask[i,:3]) for i in range(__steps)]
        util.plot_orbit2_3d(__scheme.x, __obs[__obs_mask_row], 'assimilated', 'observed')
