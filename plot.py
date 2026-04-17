#%%
import xarray as xr
import neko_utils as nk
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Load data
case_dir = os.getcwd()
case_path = os.path.join(f"{case_dir}", "output_MOST_CPU")
case_path = "/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/output_MOST_CPU"

# Settings
savef = True

# Helper variables for plotting
cmap_name = 'viridis'
batch_alpha = 0.6
mean_lw = 2
mean_color = 'black'

#%%

# Fluid plots
data_full = nk.csv_to_xr(f'{case_path}/fluid_stats0.csv')
data_mean = data_full.mean(dim="time")

n_times = data_full.sizes['time']
cmap = cm.get_cmap(cmap_name)
colors = cmap(np.linspace(0, 1, n_times))

fluid_vars = [('u', 'v', 'w'), ('uu',), ('vv',), ('ww',), ('uw',), ('uv',)]

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for idx, vars_to_plot in enumerate(fluid_vars):
    axes[idx].set_title(', '.join(vars_to_plot))
    for v, var in enumerate(vars_to_plot):
        # Plot individual time batches
        for t_idx in range(n_times):
            batch_data = data_full[var].isel(time=t_idx)
            axes[idx].plot(batch_data, data_full.z, color=colors[t_idx], alpha=batch_alpha)
        
        # Plot time-averaged mean
        axes[idx].plot(data_mean[var], data_mean.z, color=mean_color, linewidth=mean_lw)

if savef:
    plt.savefig(f'{case_path}/fluid_stats.png')

#%% 

# Temperature plots
data_t_full = nk.csv_to_xr(
        f'{case_path}/scalar_stats_temperature0.csv',
        type="scalar", basic=True, height="z",
        fluid_csv=f'{case_path}/fluid_stats0.csv'
        )
data_t_mean = data_t_full.mean(dim="time")

n_times_t = data_t_full.sizes['time']
colors_t = cmap(np.linspace(0, 1, n_times_t))

temp_vars = [('s',), ('ss',), ('us',), ('vs',), ('ws',)]
temp_titles = ['t', 'tt', 'tu', 'tv', 'tw']

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
    axes[idx].set_title(title)
    var_name = var[0]
    
    # Plot individual time batches
    for t_idx in range(n_times_t):
        batch_data = data_t_full[var_name].isel(time=t_idx)
        axes[idx].plot(batch_data, data_t_full.z, color=colors_t[t_idx], alpha=batch_alpha)
        
    # Plot time-averaged mean
    axes[idx].plot(data_t_mean[var_name], data_t_mean.z, color=mean_color, linewidth=mean_lw)

if savef:
    plt.savefig(f'{case_path}/temperature_stats.png')

#%%

# Passive scalar plots
scalar_files = [f for f in os.listdir(case_path) if f.startswith('scalar_stats_') \
                and f.endswith('0.csv') \
                and 'sgs' not in f \
                and 'temp' not in f
            ]
num_scalars = len(scalar_files)

temp_vars = [('s',), ('ss',), ('us',), ('vs',), ('ws',)]
temp_titles = ['s', 'ss', 'su', 'sv', 'sw']

for scalar in scalar_files:
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    data_s_full = nk.csv_to_xr(
        f'{case_path}/{scalar}',
        type="scalar", basic=True, height="z",
        fluid_csv=f'{case_path}/fluid_stats0.csv'
        )
    data_s_mean = data_s_full.mean(dim="time")
    
    n_times_s = data_s_full.sizes['time']
    colors_s = cmap(np.linspace(0, 1, n_times_s))
    
    scalar_name = scalar.split('_')[2].split('0.csv')[0] 

    for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
        axes[idx].set_title(title)
        var_name = var[0]
        
        # Plot individual time batches
        for t_idx in range(n_times_s):
            batch_data = data_s_full[var_name].isel(time=t_idx)
            axes[idx].plot(batch_data, data_s_full.z, color=colors_s[t_idx], alpha=batch_alpha)
            
        # Plot time-averaged mean
        axes[idx].plot(data_s_mean[var_name], data_s_mean.z, color=mean_color, linewidth=mean_lw)
        
    fig.suptitle("Scalar: " + scalar_name)
    if savef:
        plt.savefig(f'{case_path}/scalar_{scalar_name}_stats.png')

# %%
