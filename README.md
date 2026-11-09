# Climate-driven dengue transmission in Rio de Janeiro

**UCLouvain · LBRTI2102 — Process-based Modelling in Bioscience Engineering**  
**Authors:** Adam Malila & Augustin Van Ingelgem

This is an initial, **unvalidated student project scaffold**, not a biological research study or an epidemiological forecast. The question is whether adding measured temperature and rainfall to a reduced SEIR model improves the simulation of weekly dengue cases in Rio de Janeiro.

## Modelling choices

State variables S (susceptible), E (exposed/latent), I (infectious), R (removed) are human counts; N=S+E+I+R is conserved. The auxiliary state C counts E→I transitions and is **not** part of N.

```text
dS/dt = - beta(t)*S*I/N
dE/dt = + beta(t)*S*I/N - sigma*E
dI/dt = + sigma*E - gamma*I
dR/dt = + gamma*I
dC/dt = + sigma*E
```

The weather model is `beta(t) = beta0 * exp(theta_T*zT(t-lag) + theta_P*zP(t-lag))`, compared against the constant-beta baseline (`theta_T=theta_P=0`). The vector/mosquito component is **implicit in beta**. The model does not simulate mosquitoes or spatial transport.

`beta0`, `sigma`, `gamma`: day⁻¹; `lag`: days/weeks; `theta_T`, `theta_P`: dimensionless; `rho`: assumed reporting fraction (0–1]. The predicted weekly notified cases are approximated by `rho*(C_week_end-C_week_start)`, **not** the instantaneous count I(t). This is a simplified observation model.

## Run the first code

Python 3.10+, then:

```bash
pip install -r requirements.txt
python scripts/demo.py
python -m unittest discover -s tests -v
```

The demo creates `outputs/synthetic_demo.png` from **invented test inputs**. It does not measure, calibrate or validate the actual Rio dengue outbreak. Initial values in the demo exist solely to test numerical integration and population conservation.

## Plan for real data

1. Obtain weekly probable cases `casprov` from [InfoDengue](https://info.dengue.mat.br/services/api/doc/) for Rio municipality **3304557**, plus weekly temperature `temp_med_avg` and rainfall `precip_tot_sum` from [Mosqlimate](https://api.mosqlimate.org/docs/datastore/GET/climate-weekly/), corrected rain `precip_fixed=true`.
2. Audit date coverage, epidemic week keys, duplicates, missingness, changed case definitions and municipality code.
3. Select **one** coherent wave and record all assumptions. Use population from [IBGE](https://www.ibge.gov.br/cidades-e-estados/rj/rio-de-janeiro.html).
4. Standardize meteorological inputs using only **training weeks**, and select the lag using only training data.
5. Solve with SciPy RK45; calibrate a limited set (`beta0`, `theta_T`, `theta_P`) with fixed literature-based `sigma`/`gamma` and explicit assumptions on immunity/ascertainment.
6. Evaluate both models on later held-out weeks, without refitting; compare RMSE, MAE, peak date and cumulative totals; perform sensitivity analysis.
7. Discuss multiple serotypes, identifiability, immunity, surveillance biases, implicit vector transmission and lack of spatial processes. Illustrate *hypothetical* climate scenarios; do not claim causal projections.

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) and [scripts/prepare_data.py](scripts/prepare_data.py). The two uploaded ZIPs could not be directly extracted in this session; implementation methods instead follow the available course SEIR and inverse-modelling script examples, with new code written for this project. Original course files were not republished.

**Report and source-code deadline:** 4 January 2027, 08:00.
