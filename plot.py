#%%
import xarray as xr
import neko_utils as nk
import os
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 300
import matplotlib.cm as cm
import numpy as np
from matplotlib.lines import Line2D

# Load data
case_dir = os.getcwd()
case_path = os.path.join(f"{case_dir}", "output_MOST_CPU")
case_path = "/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/output_MOST_CPU"

# Settings
savef = True
cmap_name = 'viridis'
batch_alpha = 0.6
mean_lw = 2.0
mean_color = 'black'

def get_metadata_str(data_full):
    # Calculate time metadata for the suptitle
    t_vals = data_full.time.values
    t_start = t_vals[0]
    t_end = t_vals[-1]
    
    if len(t_vals) > 1:
        # Calculate delta t between samples
        dt = np.mean(np.diff(t_vals))
    else:
        dt = 0.0
        
    return f"t_start: {t_start:.2f}s | t_end: {t_end:.2f}s | Batch size ($\Delta t$): {dt:.2f}s"

def add_custom_legend(ax, colors):
    # Create legend handles for the mean and the batch progression
    ax.legend(handles=[Line2D([0], [0], color=mean_color, lw=mean_lw, label='Mean')], loc='best', fontsize=8)

#%%

# Fluid plots
data_full = nk.csv_to_xr(f'{case_path}/fluid_stats0.csv')
data_mean = data_full.mean(dim="time")

n_times = data_full.sizes['time']
cmap = plt.get_cmap(cmap_name)
colors = cmap(np.linspace(0, 1, n_times))

fluid_vars = [('u', 'v', 'w'), ('uu',), ('vv',), ('ww',), ('uw',), ('uv',)]

fig, axes = plt.subplots(2, 3, figsize=(15, 12))
axes = axes.flatten()

metadata = get_metadata_str(data_full)
fig.suptitle(f"Fluid Statistics\n{metadata}", fontsize=14)

for idx, vars_to_plot in enumerate(fluid_vars):
    ax = axes[idx]
    ax.set_title(', '.join(vars_to_plot))
    
    for var in vars_to_plot:
        # Plot time batches
        for t_idx in range(n_times):
            batch_data = data_full[var].isel(time=t_idx)
            ax.plot(batch_data, data_full.z, color=colors[t_idx], alpha=batch_alpha)
        
        # Plot ensemble mean
        ax.plot(data_mean[var], data_mean.z, color=mean_color, linewidth=mean_lw)
    
    add_custom_legend(ax, colors)

plt.tight_layout()
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

fig, axes = plt.subplots(2, 3, figsize=(15, 12))
axes = axes.flatten()

metadata_t = get_metadata_str(data_t_full)
fig.suptitle(f"Temperature Statistics\n{metadata_t}", fontsize=14)

for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
    ax = axes[idx]
    ax.set_title(title)
    var_name = var[0]
    
    for t_idx in range(n_times_t):
        batch_data = data_t_full[var_name].isel(time=t_idx)
        ax.plot(batch_data, data_t_full.z, color=colors_t[t_idx], alpha=batch_alpha)
        
    ax.plot(data_t_mean[var_name], data_t_mean.z, color=mean_color, linewidth=mean_lw)
    add_custom_legend(ax, colors_t)

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
if savef:
    plt.savefig(f'{case_path}/temperature_stats.png')

#%%

# Passive scalar plots
scalar_files = [f for f in os.listdir(case_path) if f.startswith('scalar_stats_') \
                and f.endswith('0.csv') \
                and 'sgs' not in f \
                and 'temp' not in f
            ]

for scalar in scalar_files:
    fig, axes = plt.subplots(2, 3, figsize=(15, 12))
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
    
    metadata_s = get_metadata_str(data_s_full)
    fig.suptitle(f"Scalar: {scalar_name}\n{metadata_s}", fontsize=14)

    for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
        ax = axes[idx]
        ax.set_title(title)
        var_name = var[0]
        
        for t_idx in range(n_times_s):
            batch_data = data_s_full[var_name].isel(time=t_idx)
            ax.plot(batch_data, data_s_full.z, color=colors_s[t_idx], alpha=batch_alpha)
            
        ax.plot(data_s_mean[var_name], data_s_mean.z, color=mean_color, linewidth=mean_lw)
        add_custom_legend(ax, colors_s)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    if savef:
        plt.savefig(f'{case_path}/scalar_{scalar_name}_stats.png')
#%%
