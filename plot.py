#%%
import xarray as xr
import neko_utils as nk
import os
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 300
import matplotlib.cm as cm
import numpy as np

# Load data
base_paths = [
        "/cfs/klemming/projects/snic/abl-les-ldl/neko/shear_convection_abl/",
    ]
case_dict = {
    "output_MOST_CPU" : "MOST",
    "output_RL_CPU"   : "RL"
}

#%%
# Settings
savef = True
plot_sample_lines = True
batch_alpha = 0.7
mean_lw = 2.0
mean_color = 'black'
style_dict = {
    "-": "Blues",
    "--": "Reds",
    "-.": "Greens",
    ":": "Purples"
}
img_path = base_paths[0]

#%%
# Utility functions

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

def add_custom_legend(ax):
    ax.legend(loc='best', fontsize=8)

case_paths = [os.path.join(
    base_paths[i],
    case_dir
) for i,case_dir in enumerate(case_dict.keys())] if len(base_paths) == len(case_dict) \
                                                    else [
                                                        os.path.join(
                                                            base_paths[0], 
                                                            case_dir
                                                            ) for case_dir in case_dict.keys()
                                                    ]
case_labels = list(case_dict.values())
linestyles = list(style_dict.keys())
cmaps = [plt.get_cmap(cmap_name) for cmap_name in list(style_dict.values())]
#%%


# Fluid plots
fluid_vars = [('u', 'v', 'w'), ('uu',), ('vv',), ('ww',), ('uw',), ('uv',)]
fig, axes = plt.subplots(2, 3, figsize=(15, 12))
axes = axes.flatten()
fig.suptitle(f"Fluid Statistics\ncases: {', '.join(case_labels)}", fontsize=14)

for idx, vars_to_plot in enumerate(fluid_vars):
    ax = axes[idx]
    ax.set_title(', '.join(vars_to_plot))
    
    for case_idx, case_path in enumerate(case_paths):
        case_label = f"{case_labels[case_idx]}"
        data_full = nk.csv_to_xr(f'{case_path}/fluid_stats0.csv')
        data_mean = data_full.mean(dim="time")
        n_times = data_full.sizes['time']
        cmap = cmaps[case_idx % len(cmaps)]
        linestyle = linestyles[case_idx % len(linestyles)]
        colors = cmap(np.linspace(0, 1, n_times))
        
        for var in vars_to_plot:
            if plot_sample_lines:
                for t_idx in range(n_times):
                    batch_data = data_full[var].isel(time=t_idx)
                    ax.plot(batch_data, data_full.z, color=colors[t_idx], alpha=batch_alpha, linewidth=0.8, ls=linestyle)
            
            label = case_label if var == vars_to_plot[0] else None
            ax.plot(
                data_mean[var], data_mean.z,
                color=mean_color,
                linewidth=mean_lw,
                linestyle=linestyle,
                label=label
            )
    add_custom_legend(ax)

plt.tight_layout()
if savef:
    plt.savefig(f'{img_path}/fluid_stats.png')

#%% 

# Temperature plots
temp_vars = [('s',), ('ss',), ('us',), ('vs',), ('ws',)]
temp_titles = ['t', 'tt', 'tu', 'tv', 'tw']
fig, axes = plt.subplots(2, 3, figsize=(15, 12))
axes = axes.flatten()
fig.suptitle(f"Temperature Statistics\ncases: {', '.join(case_labels)}", fontsize=14)

for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
    ax = axes[idx]
    ax.set_title(title)
    var_name = var[0]
    
    for case_idx, case_path in enumerate(case_paths):
        case_label = f"{case_labels[case_idx]}"
        data_t_full = nk.csv_to_xr(
            f'{case_path}/scalar_stats_temperature0.csv',
            type="scalar", basic=True, height="z",
            fluid_csv=f'{case_path}/fluid_stats0.csv'
        )
        data_t_mean = data_t_full.mean(dim="time")
        n_times_t = data_t_full.sizes['time']
        cmap = cmaps[case_idx % len(cmaps)]
        colors_t = cmap(np.linspace(0, 1, n_times_t))
        linestyle = linestyles[case_idx % len(linestyles)]
        
        if plot_sample_lines:
            for t_idx in range(n_times_t):
                batch_data = data_t_full[var_name].isel(time=t_idx)
                ax.plot(batch_data, data_t_full.z, color=colors_t[t_idx], alpha=batch_alpha, linewidth=0.8, ls=linestyle)
        
        label = case_label
        ax.plot(
            data_t_mean[var_name], data_t_mean.z,
            color=mean_color,
            linewidth=mean_lw,
            linestyle=linestyle,
            label=label
        )
    add_custom_legend(ax)

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
if savef:
    plt.savefig(f'{img_path}/temperature_stats.png')

#%%

# Passive scalar plots
scalar_files = [
    f for f in os.listdir(case_paths[0])
    if f.startswith('scalar_stats_')
    and f.endswith('0.csv')
    and 'sgs' not in f
    and 'temp' not in f
]

for scalar in scalar_files:
    fig, axes = plt.subplots(2, 3, figsize=(15, 12))
    axes = axes.flatten()
    scalar_name = scalar.split('_')[2].split('0.csv')[0]
    fig.suptitle(f"Scalar: {scalar_name}\ncases: {', '.join(case_labels)}", fontsize=14)

    for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
        ax = axes[idx]
        ax.set_title(title)
        var_name = var[0]

        for case_idx, case_path in enumerate(case_paths):
            case_label = f"{case_labels[case_idx]}"
            data_s_full = nk.csv_to_xr(
                f'{case_path}/{scalar}',
                type="scalar", basic=True, height="z",
                fluid_csv=f'{case_path}/fluid_stats0.csv'
            )
            data_s_mean = data_s_full.mean(dim="time")
            n_times_s = data_s_full.sizes['time']
            cmap = cmaps[case_idx % len(cmaps)]
            colors_s = cmap(np.linspace(0, 1, n_times_s))
            linestyle = linestyles[case_idx % len(linestyles)]

            if plot_sample_lines:
                for t_idx in range(n_times_s):
                    batch_data = data_s_full[var_name].isel(time=t_idx)
                    ax.plot(batch_data, data_s_full.z, color=colors_s[t_idx], alpha=batch_alpha, linewidth=0.8, ls=linestyle)

            label = case_label
            ax.plot(
                data_s_mean[var_name], data_s_mean.z,
                color=mean_color,
                linewidth=mean_lw,
                linestyle=linestyle,
                label=label
            )
        add_custom_legend(ax)

    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    if savef:
        plt.savefig(f'{img_path}/scalar_{scalar_name}_stats.png')
#%%        case_label = f"{case_labels[case_idx]}"
        data_full = nk.csv_to_xr(f'{case_path}/fluid_stats0.csv')
        data_mean = data_full.mean(dim="time")
        n_times = data_full.sizes['time']
        cmap = cmaps[case_idx % len(cmaps)]
        linestyle = linestyles[case_idx % len(linestyles)]
        colors = cmap(np.linspace(0, 1, n_times))
        
        for var in vars_to_plot:
            if plot_sample_lines:
                for t_idx in range(n_times):
                    batch_data = data_full[var].isel(time=t_idx)
                    ax.plot(batch_data, data_full.z, color=colors[t_idx], alpha=batch_alpha, linewidth=0.8, ls=linestyle)
            
            label = case_label if var == vars_to_plot[0] else None
            ax.plot(
                data_mean[var], data_mean.z,
                color=mean_color,
                linewidth=mean_lw,
                linestyle=linestyle,
                label=label
            )
    add_custom_legend(ax)

plt.tight_layout()
if savef:
    plt.savefig(f'{img_path}/fluid_stats.png')

#%% 

# Temperature plots
temp_vars = [('s',), ('ss',), ('us',), ('vs',), ('ws',)]
temp_titles = ['t', 'tt', 'tu', 'tv', 'tw']
fig, axes = plt.subplots(2, 3, figsize=(15, 12))
axes = axes.flatten()
fig.suptitle(f"Temperature Statistics\ncases: {', '.join(case_labels)}", fontsize=14)

for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
    ax = axes[idx]
    ax.set_title(title)
    var_name = var[0]
    
    for case_idx, case_path in enumerate(case_paths):
        case_label = f"{case_labels[case_idx]}"
        data_t_full = nk.csv_to_xr(
            f'{case_path}/scalar_stats_temperature0.csv',
            type="scalar", basic=True, height="z",
            fluid_csv=f'{case_path}/fluid_stats0.csv'
        )
        data_t_mean = data_t_full.mean(dim="time")
        n_times_t = data_t_full.sizes['time']
        cmap = cmaps[case_idx % len(cmaps)]
        colors_t = cmap(np.linspace(0, 1, n_times_t))
        linestyle = linestyles[case_idx % len(linestyles)]
        
        if plot_sample_lines:
            for t_idx in range(n_times_t):
                batch_data = data_t_full[var_name].isel(time=t_idx)
                ax.plot(batch_data, data_t_full.z, color=colors_t[t_idx], alpha=batch_alpha, linewidth=0.8, ls=linestyle)
        
        label = case_label
        ax.plot(
            data_t_mean[var_name], data_t_mean.z,
            color=mean_color,
            linewidth=mean_lw,
            linestyle=linestyle,
            label=label
        )
    add_custom_legend(ax)

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
if savef:
    plt.savefig(f'{img_path}/temperature_stats.png')

#%%

# Passive scalar plots
scalar_files = [
    f for f in os.listdir(case_paths[0])
    if f.startswith('scalar_stats_')
    and f.endswith('0.csv')
    and 'sgs' not in f
    and 'temp' not in f
]

for scalar in scalar_files:
    fig, axes = plt.subplots(2, 3, figsize=(15, 12))
    axes = axes.flatten()
    scalar_name = scalar.split('_')[2].split('0.csv')[0]
    fig.suptitle(f"Scalar: {scalar_name}\ncases: {', '.join(case_labels)}", fontsize=14)

    for idx, (var, title) in enumerate(zip(temp_vars, temp_titles)):
        ax = axes[idx]
        ax.set_title(title)
        var_name = var[0]

        for case_idx, case_path in enumerate(case_paths):
            case_label = f"{case_labels[case_idx]}"
            data_s_full = nk.csv_to_xr(
                f'{case_path}/{scalar}',
                type="scalar", basic=True, height="z",
                fluid_csv=f'{case_path}/fluid_stats0.csv'
            )
            data_s_mean = data_s_full.mean(dim="time")
            n_times_s = data_s_full.sizes['time']
            cmap = cmaps[case_idx % len(cmaps)]
            colors_s = cmap(np.linspace(0, 1, n_times_s))
            linestyle = linestyles[case_idx % len(linestyles)]

            if plot_sample_lines:
                for t_idx in range(n_times_s):
                    batch_data = data_s_full[var_name].isel(time=t_idx)
                    ax.plot(batch_data, data_s_full.z, color=colors_s[t_idx], alpha=batch_alpha, linewidth=0.8, ls=linestyle)

            label = case_label
            ax.plot(
                data_s_mean[var_name], data_s_mean.z,
                color=mean_color,
                linewidth=mean_lw,
                linestyle=linestyle,
                label=label
            )
        add_custom_legend(ax)

    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    if savef:
        plt.savefig(f'{img_path}/scalar_{scalar_name}_stats.png')
#%%
