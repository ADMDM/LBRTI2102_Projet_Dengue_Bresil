"""Human SEIR with an auxiliary case counter and weekly weather forcing.

N=S+E+I+R is constant. C counts E→I transitions, not an extra population.
Weather transmission is effective/implicit; mosquito states are not modelled.
Units: time days, beta/sigma/gamma 1/day, population states people.
"""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp

@dataclass(frozen=True)
class SEIRParameters:
    N: float
    sigma: float
    gamma: float
    rho: float = 1.0

    def __post_init__(self):
        if min(self.N,self.sigma,self.gamma) <= 0 or not (0 < self.rho <= 1):
            raise ValueError("N, sigma, gamma > 0; reporting fraction rho in (0,1]")

def derivatives(t, y, beta, params):
    S,E,I,R,C = y
    infection = beta*S*I/params.N
    progression = params.sigma*E
    recovery = params.gamma*I
    return [-infection, infection-progression, progression-recovery, recovery, progression]

def simulate_weekly(params, y0, beta0, zT, zP, theta_T=0., theta_P=0.):
    """Integrate each 7-day week with piecewise-constant externally supplied climate.

    zT and zP are already standardized using training-only moments.
    The delay/lag is applied before calling this function.
    Returns (states at week boundaries, expected reported weekly cases, beta series).
    """
    zT,zP=np.asarray(zT,float),np.asarray(zP,float)
    y=np.asarray(y0,float)
    if y.shape != (5,) or np.any(y < 0) or not np.isclose(y[:4].sum(),params.N):
        raise ValueError("y0 must be nonnegative [S,E,I,R,C] with S+E+I+R=N")
    if zT.ndim != 1 or zT.shape != zP.shape or len(zT)==0 or not np.isfinite(zT).all() or not np.isfinite(zP).all():
        raise ValueError("weather inputs must be matching finite 1-D arrays")
    if beta0 <= 0:
        raise ValueError("beta0 must be positive")
    beta=beta0*np.exp(np.clip(theta_T*zT+theta_P*zP,-20,20))
    states=[y]
    for b in beta:
        sol=solve_ivp(derivatives,(0,7),states[-1],args=(float(b),params),
                      method="RK45",rtol=1e-8,atol=1e-9,t_eval=[7.],max_step=1.)
        if not sol.success:
            raise RuntimeError(sol.message)
        states.append(sol.y[:,-1])
    states=np.asarray(states)
    reports=params.rho*np.diff(states[:,4])
    return states,reports,beta
