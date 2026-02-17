import numpy as np

def scale_measurements(weights=np.array([1, 5, 10, 20, 50, 100, 200, 300, 400, 500]),
                       reps_per_weight=2,
                       mean=0.0,
                       variance=0.05,
                       seed=None):
    seed = seed or 0
    x = np.repeat(weights, reps_per_weight)
    y = np.random.default_rng(seed=seed).normal(x*(1+mean), x*np.sqrt(variance))
    return x, y
