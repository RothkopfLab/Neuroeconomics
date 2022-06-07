import numpy as np
from scipy.optimize import minimize
import scipy.stats

diff_lognormal_cdf = np.loadtxt("./data/cdf_diff_lognormal_0_10_0.001")

def cdf_lognormal(values):
    idxs = np.minimum(np.abs(values) / 0.001, 10000).astype(int)
    cdf_vals = diff_lognormal_cdf[idxs]
    return np.where(values >= 0, cdf_vals, 1-cdf_vals)

class Agent(object):
    def __init__(self, dw, abs_angle_ws, rel_angle_w, noise_dist="normal"):
        self.dw = dw
        self.abs_angle_ws = abs_angle_ws
        self.abs_angle_edges = np.linspace(0, 360, len(abs_angle_ws), endpoint=False)
        self.abs_angle_edges += self.abs_angle_edges[1] / 2
        self.rel_angle_w = rel_angle_w
        self.noise_dist = noise_dist

    def _get_value_for_points(self, ps):
        v = self.dw * (ps[0]/412)
        v += np.interp(ps[1], self.abs_angle_edges, self.abs_angle_ws, period=360)
        v += (np.abs(ps[2] - 180)/180) * self.rel_angle_w
        return v

    def _get_values(self, points):
        chosen_vals = self._get_value_for_points(points[:3, :])
        not_chosen_vals = self._get_value_for_points(points[3:, :])
        return chosen_vals, not_chosen_vals
    
    def _get_value_diffs(self, points):
        chosen_vals, not_chosen_vals = self._get_values(points)
        return chosen_vals - not_chosen_vals

    def decisions(self, points):
        diffs = self._get_value_diffs(points)
        #diffs += np.random.normal(0, self.sigma, points.shape[1])
        return np.where(diffs > 0, 0, 1)
    
    def likelihoods(self, points):
        if self.noise_dist == "normal":
            diffs = self._get_value_diffs(points)
            return scipy.stats.norm.cdf(diffs, 0, 1)
        elif self.noise_dist == "logistic":
            chosen_vals, not_chosen_vals = self._get_values(points) 
            return np.exp(chosen_vals) / (np.exp(chosen_vals) + np.exp(not_chosen_vals))
        elif self.noise_dist == "lognormal":
            diffs = self._get_value_diffs(points)
            return cdf_lognormal(diffs)
    
    def perc_correct(self, points):
        diffs = self._get_value_diffs(points)
        return np.mean(diffs > 0)


def obj(params, points, noise_dist):
    if len(params) == 8:
        a = Agent(params[0], params[1:7], params[7], noise_dist)
    elif len(params) == 7:
        a = Agent(params[0], params[1:7], 0, noise_dist)
    elif len(params) == 1:
        a = Agent(params[0], [0]*6, 0, noise_dist)
    likelihoods = a.likelihoods(points)
    return -np.sum(np.log(likelihoods))


def estimate_parameters_from(points, x0=None, method="L-BFGS-B", noise_dist="normal"):
    if x0 is None:
        x0 = [-1]+[1]*7
    return minimize(obj, x0, method=method, args=(points,noise_dist))

