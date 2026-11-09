"""Simple inverse modelling with a chronological train/validation split."""
import numpy as np
from scipy.optimize import least_squares
from .model import simulate_weekly

def metrics(obs,pred):
    obs,pred=np.asarray(obs,float),np.asarray(pred,float)
    if obs.shape!=pred.shape or len(obs)==0:
        raise ValueError("mismatched/nonexistent observations")
    return {"MAE":float(np.mean(np.abs(obs-pred))),
            "RMSE":float(np.sqrt(np.mean((obs-pred)**2)))}

def calibrate(params,y0,zT,zP,observed,train_weeks,climate=False):
    obs=np.asarray(observed,float)
    if not (5 <= train_weeks < len(obs)) or len(zT)!=len(obs) or len(zP)!=len(obs):
        raise ValueError("training and series dimensions invalid")
    if not np.isfinite(obs).all() or np.any(obs < 0):
        raise ValueError("observations must be finite nonnegative")
    def residual(x):
        beta=np.exp(x[0])
        tt,tp=(x[1],x[2]) if climate else (0.,0.)
        _,cases,_=simulate_weekly(params,y0,beta,zT[:train_weeks],zP[:train_weeks],tt,tp)
        return np.log1p(np.maximum(cases,0))-np.log1p(obs[:train_weeks])
    x0=[np.log(.35)]+([0.,0.] if climate else [])
    lo=[np.log(.005)]+([-2.,-2.] if climate else [])
    hi=[np.log(3.)]+([2.,2.] if climate else [])
    fit=least_squares(residual,x0,bounds=(lo,hi),max_nfev=150)
    b=float(np.exp(fit.x[0]))
    tt,tp=(float(fit.x[1]),float(fit.x[2])) if climate else (0.,0.)
    states,pred,beta=simulate_weekly(params,y0,b,zT,zP,tt,tp)
    return {"beta0":b,"theta_T":tt,"theta_P":tp,"success":bool(fit.success),
            "train":metrics(obs[:train_weeks],pred[:train_weeks]),
            "validation":metrics(obs[train_weeks:],pred[train_weeks:]),
            "prediction":pred,"states":states,"beta_weekly":beta}
