"""
Data export script | Data Export Script
Called from OnModThreadComplete in spikemod.py:

    from export_data import export_data
    export_data(self)
"""

import numpy as np
import os
from datetime import datetime


def export_data(mod, label="run", out_dir=None):
    """
    Export current model data to a .npz file.

    Args:
        mod:     SpikeMod object (self)
        label:   Filename label used to distinguish different runs, e.g. "model1_dap" / "model2_nodap"
        out_dir: Output directory, defaults to exported_data/ under the module directory.

    Usage (manual command-line call):
        from export_data import export_data
        export_data(mod, label="model2_gNMDA02")
    """

    # Output directory
    if out_dir is None:
        base = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(base, "exported_data")
    os.makedirs(out_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(out_dir, f"{label}_{timestamp}.npz")

    # Get model hist/haz length
    try:
        model_hist_max = int(mod.modspike.hist5norm.xmax) + 1
    except Exception:
        model_hist_max = 500

    # Get cell hist/haz length (if cell data is available)
    if mod.cellspike.spikecount > 0:
        try:
            cell_hist_max = int(mod.cellspike.hist5norm.xmax) + 1
        except Exception:
            cell_hist_max = model_hist_max
    else:
        cell_hist_max = model_hist_max

    # Get secretion data length
    try:
        sec_nonzero = np.where(np.array(mod.secdata.secX) != 0)[0]
        sec_len = int(sec_nonzero[-1] + 1) if len(sec_nonzero) > 0 else 1000
        sec_len = min(sec_len, 1000000)
    except Exception:
        sec_len = 1000

    # Save data
    np.savez(filename,
        # Model spike analysis
        model_hist5norm  = np.array(mod.modspike.hist5norm[:model_hist_max]),
        model_haz5       = np.array(mod.modspike.haz5[:model_hist_max]),
        model_freq       = float(mod.modspike.freq),
        model_spikecount = int(mod.modspike.spikecount),

        # Cell spike analysis (may be zeros if no cell data loaded)
        cell_hist5norm   = np.array(mod.cellspike.hist5norm[:cell_hist_max]),
        cell_haz5        = np.array(mod.cellspike.haz5[:cell_hist_max]),
        cell_freq        = float(mod.cellspike.freq),
        cell_spikecount  = int(mod.cellspike.spikecount),

        # Secretion data
        secX             = np.array(mod.secdata.secX[:sec_len]),
        secPlasma        = np.array(mod.secdata.secPlasma[:sec_len]),
        datsample        = int(mod.datsample),

        # ISI x-axis (ms)
        isi_bins         = np.arange(model_hist_max) * 5 + 2.5,
        time_axis        = np.arange(sec_len) * int(mod.datsample),
    )

    print(f"✓ Data saved: {filename}")
    print(f"  model spikes: {mod.modspike.spikecount}, freq: {mod.modspike.freq:.2f} Hz")
    print(f"  model hist bins: {model_hist_max}")
    print(f"  secretion points: {sec_len}")
    return filename
