import re
import xarray as xr
import numpy as np

# ------------------------------------------------------
# Parser
# ------------------------------------------------------
def parse_neko_log(filename):

    step_re = re.compile(
    r"Step\s*=\s*(\d+)\s+t\s*=\s*([0-9.E+-]+)"
    )

    cfl_dt_re = re.compile(
        r"CFL:\s*([0-9.E+-]+)\s+dt:\s*([0-9.E+-]+)"
    )

    diag_var_re = re.compile(
        r"^\s*([A-Za-z0-9_]+):\s+(.+)$"
    )
    records = []

    with open(filename, "r") as f:
        lines = f.readlines()

    current = None
    in_wall_diag = False

    for line in lines:
        # --- Step & time ---
        m = step_re.search(line)
        if m:
            if current is not None:
                records.append(current)

            current = {
                "step": int(m.group(1)),
                "time": float(m.group(2)),
            }
            in_wall_diag = False
            continue

        if current is None:
            continue

        # --- CFL and dt ---
        m = cfl_dt_re.search(line)
        if m:
            current["CFL"] = float(m.group(1))
            current["dt"]  = float(m.group(2))
            continue

        # --- Wall model diagnostics start/end ---
        if "----Wall model diagnostics----" in line:
            in_wall_diag = True
            continue

        if in_wall_diag and "KSP solver" in line:
            in_wall_diag = False
            continue

        # --- Parse diagnostics variables ---
        if in_wall_diag:
            m = diag_var_re.match(line)
            if m:
                var = m.group(1)
                values = m.group(2).split()

                # single value (e.g. bc_value)
                if len(values) == 1:
                    current[var] = float(values[0])
                # three values: sum, min, max
                elif len(values) == 3:
                    current[f"{var}_sum"] = float(values[0])
                    current[f"{var}_min"] = float(values[1])
                    current[f"{var}_max"] = float(values[2])

    # append last record
    if current is not None:
        records.append(current)

    return records


# ------------------------------------------------------
# Convert to xarray and save NetCDF
# ------------------------------------------------------
def records_to_xarray(records, outfile="wall_model_diagnostics.nc"):
    times = np.array([r["time"] for r in records])

    data_vars = {}
    exclude_keys = {"time"}

    all_keys = set().union(*(r.keys() for r in records))
    for key in all_keys - exclude_keys:
        data = np.array([r.get(key, np.nan) for r in records])
        data_vars[key] = xr.DataArray(data, dims=("time",))

    ds = xr.Dataset(
        data_vars=data_vars,
        coords={"time": times},
        attrs={"source": "Neko log file"}
    )

    ds.to_netcdf(outfile)
    return ds


# ------------------------------------------------------
#  MAIN
# ------------------------------------------------------

records = parse_neko_log(logfile)
ds = records_to_xarray(records, outfile=outfile)

 
