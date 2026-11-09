"""Executable SYNTHETIC demo, not a fit to Rio data."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np
import matplotlib.pyplot as plt
from dengue_rio.model import SEIRParameters, simulate_weekly

p=SEIRParameters(N=100000,sigma=.2,gamma=.2,rho=.4)
y0=[74973,15,12,25000,0]
weeks=np.arange(32)
zT=np.sin(2*np.pi*weeks/24)
zP=np.cos(2*np.pi*weeks/18)
states,cases,beta=simulate_weekly(p,y0,.42,zT,zP,.28,.16)
assert np.allclose(states[:,:4].sum(axis=1),p.N,atol=1e-4)
out=Path("outputs");out.mkdir(exist_ok=True)
fig,ax=plt.subplots(figsize=(8,4))
ax.plot(weeks,cases,label="Synthetic weekly expected reports")
ax.set(xlabel="Week",ylabel="Cases/week",title="SYNTHETIC DEMO — not Rio observations")
ax.legend();fig.tight_layout();fig.savefig(out/"synthetic_demo.png",dpi=150)
print("Population conserved; figure:",out/"synthetic_demo.png")
