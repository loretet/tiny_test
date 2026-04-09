#%%

import xarray as xr
import neko_utils as nk
import matplotlib.pyplot as plt

# Load data
cases = {
    'ri_cpu': '/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/output_Ri_CPU',
    'most_cpu': '/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/output_MOST_CPU',
    'rl_cpu': '/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/output_RL_CPU',
    'ri_gpu': '/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/output_Ri_GPU',
    'most_gpu': '/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/output_MOST_GPU',
    'rl_gpu': '/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/output_RL_GPU',
}

data = {}
for case, path in cases.items():
    data[case] = nk.csv_to_xr(f'{path}/fluid_stats0.csv').mean(dim="time")

# Fluid plots
fluid_vars = [('u', 'v', 'w'), ('uu',), ('vv',), ('ww',), ('uw',), ('uv',)]
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for idx, vars_to_plot in enumerate(fluid_vars):
    axes[idx].set_title(', '.join(vars_to_plot))
    for v,var in enumerate(vars_to_plot):
        for case, obj in data.items():
            if "ri" in case:
                color, model = "tab:blue", "Richardson"
            elif "most" in case:
                color, model = "tab:orange", "MOST"
            else:
                color, model = "tab:green", "RL"
            ls = "--" if "gpu" in case else "-"
            label = f"{model} {'GPU' if 'gpu' in case else 'CPU'}"
            axes[idx].plot(obj[var], obj.z, c=color, ls=ls, label=label if v ==0 else None)
    axes[idx].legend()

# Temperature data
data_t = {}
for case, path in cases.items():
    data_t[case] = nk.csv_to_xr(
        f'{path}/scalar_stats_temperature0.csv',
        type="scalar", basic=True, height="z",
        fluid_csv=f'{path}/fluid_stats0.csv'
    ).mean(dim="time")

# Temperature plots
temp_vars = [('s',), ('ss',), ('us',), ('vs',), ('ws',)]
temp_titles = ['t', 'tt', 'tu', 'tv', 'tw']

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
    axes[idx].set_title(title)
    for case, obj in data_t.items():
        if "ri" in case:
            color, model = "tab:blue", "Richardson"
        elif "most" in case:
            color, model = "tab:orange", "MOST"
        else:
            color, model = "tab:green", "RL"
        ls = "--" if "gpu" in case else "-"
        label = f"{model} {'GPU' if 'gpu' in case else 'CPU'}"
        axes[idx].plot(obj[var[0]], obj.z, c=color, ls=ls, label=label)
    axes[idx].legend()

# %%
