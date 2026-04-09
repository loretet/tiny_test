# %%
import re
import xarray as xr
# %%
path = "/cfs/klemming/projects/supr/kthmech/linnealh/neko_runs/april_tests/GPU"
logfile = f"{path}/logfiles/most_gpu.log"
outfile = f"{path}/wall_model_diagnostics.nc"

# -------------------------------------------------
# Regex patterns (Neko-specific)
# -------------------------------------------------
step_time_re = re.compile(
    r"Step\s*=\s*(\d+)\s+t\s*=\s*([0-9.E+-]+)"
)
diag_start_re = re.compile(r"Wall model diagnostics")
diag_line_re = re.compile(
    r"^\s*(\w+):\s+([0-9.E+-]+)\s+([0-9.E+-]+)\s+([0-9.E+-]+)"
)

steps = []
times = []
data = {}  # dict of lists, filled dynamically

with open(logfile, "r") as f:
    lines = f.readlines()

current_step = None
current_time = None
i = 0

while i < len(lines):
    line = lines[i]

    # Step and time
    m = step_time_re.search(line)
    if m:
        current_step = int(m.group(1))
        current_time = float(m.group(2))

    # Wall model diagnostics block
    if diag_start_re.search(line):
        steps.append(current_step)
        times.append(current_time)

        i += 1
        while i < len(lines):
            l = lines[i].strip()
            if not l:
                break

            m = diag_line_re.match(l)
            if m:
                name = m.group(1)
                mean, vmin, vmax = map(float, m.groups()[1:])

                for stat, value in zip(
                    ("mean", "min", "max"),
                    (mean, vmin, vmax),
                ):
                    key = f"{name}_{stat}"
                    data.setdefault(key, []).append(value)

            i += 1
    i += 1

# -------------------------------------------------
# Build xarray Dataset
# -------------------------------------------------
coords = {
    "time": ("time", times, {
        "long_name": "simulation time",
        # "units": "seconds",
    })
}


ds = xr.Dataset(coords=coords)

# Step as data variable (indexed by time)
ds["step"] = ("time", steps, {
    "long_name": "Neko timestep number",
})

# Wall-model diagnostics
for varname, values in data.items():
    ds[varname] = ("time", values, {
        "long_name": f"Wall-model diagnostic ({varname})",
    })

# -------------------------------------------------
# Write NetCDF
# -------------------------------------------------
ds.to_netcdf(outfile)

print(f"Wrote {outfile}")
# %%
