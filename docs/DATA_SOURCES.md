# Sources and QA requirements

- Weekly dengue: https://info.dengue.mat.br/services/api/doc/ — use Rio 3304557, probable reported cases `casprov`, dates `data_iniSE`, and epidemiological week `SE`.
- Climate: https://api.mosqlimate.org/docs/datastore/GET/climate-weekly/ — Rio 3304557, temperature `temp_med_avg`, rain `precip_tot_sum`; confirm corrected rain `precip_fixed=true`.
- Population: https://www.ibge.gov.br/cidades-e-estados/rj/rio-de-janeiro.html

Do not merge weekly datasets by row order. Join on municipality, year and epidemiological-week key. Reject duplicates, missing weeks and negative case/rain counts. Standardize on training data only; preserve a later block untouched for validation. Do not commit API keys or raw data.
