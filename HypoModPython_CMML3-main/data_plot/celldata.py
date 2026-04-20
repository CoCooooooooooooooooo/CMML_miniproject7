import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Read Excel
# =========================
# Update this path to your actual Excel file path.
FILE = r"D:\path\to\oxydata dap cells.xlsx"
SHEET = 0
CELL_NAME = "CBA1R18A"   # Change to the cell name

df = pd.read_excel(FILE, sheet_name=SHEET, header=0)

raw = {}
for col in df.columns:
    vals = pd.to_numeric(df[col], errors='coerce').dropna().values
    if len(vals) > 2:
        raw[str(col)] = np.sort(vals)

if CELL_NAME not in raw:
    raise ValueError(f"{CELL_NAME} is not in the sheet. Available: {list(raw.keys())}")

spikes = np.sort(raw[CELL_NAME])

# =========================
# Normalize units: convert to ms
# Keep consistent with your earlier code
# =========================
force_seconds = True

if force_seconds:
    spikes_ms = spikes * 1000.0
else:
    spikes_ms = spikes.copy()

spikes_ms = np.asarray(spikes_ms, dtype=float)
spikes_ms = spikes_ms[np.isfinite(spikes_ms)]
spikes_ms = np.sort(spikes_ms)

if len(spikes_ms) < 2:
    raise ValueError("Too few spikes to compute ISI")

print(f"Cell: {CELL_NAME}")
print(f"N spikes = {len(spikes_ms)}")

# =========================
# Parameters: only adjust the x-axis range
# =========================
BIN_MS = 5
HIST_XMAX = 250
HAZ_XMAX = 500
HISTSIZE = 20000   # Align with HypoMod histsize

# =========================
# Calculate using the same logic as HypoMod Analysis()
# =========================
spikecount = len(spikes_ms)
isicount = spikecount - 1

# 1 ms histogram
hist1 = np.zeros(HISTSIZE + 1, dtype=float)
isis = np.diff(spikes_ms)

# In HypoMod, int(self.isis[i]) is used to determine the bin
for isi in isis:
    if isi >= HISTSIZE:
        continue
    if isi < 0:
        continue
    hist1[int(isi)] += 1

# Find hist1.xmax
nonzero_hist1 = np.where(hist1 > 0)[0]
hist1_xmax = int(nonzero_hist1.max()) if len(nonzero_hist1) > 0 else 0

# 5 ms histogram: aggregate the 1 ms histogram
hist5 = np.zeros(HISTSIZE + 1, dtype=float)
hist5_xmax = 0
for i in range(hist1_xmax + 1):
    bin_idx = int(i / BIN_MS)
    if bin_idx > hist5_xmax:
        hist5_xmax = bin_idx
    if bin_idx < HISTSIZE:
        hist5[bin_idx] += hist1[i]

# 1 ms hazard
haz1 = np.zeros(HISTSIZE + 1, dtype=float)
hazcount = 0
for i in range(hist1_xmax + 1):
    denom = spikecount - hazcount   # Note: the original source uses spikecount, not isicount
    if denom > 0:
        haz1[i] = hist1[i] / denom
    else:
        haz1[i] = 0
    hazcount += hist1[i]

# 5 ms hazard: accumulate 1 ms hazard directly into 5 ms bins
haz5 = np.zeros(HISTSIZE + 1, dtype=float)
for i in range(hist1_xmax + 1):
    haz5[int(i / BIN_MS)] += haz1[i]

# scale to percentage
haz1 *= 100
haz5 *= 100

# =========================
# Clip display range
# Only change the x-axis range, not the algorithm
# =========================
hist5_display_maxbin = int(HIST_XMAX / BIN_MS)
haz5_display_maxbin = int(HAZ_XMAX / BIN_MS)

hist_x = np.arange(hist5_display_maxbin + 1) * BIN_MS
hist_y = hist5[:hist5_display_maxbin + 1]

haz_x = np.arange(haz5_display_maxbin + 1) * BIN_MS
haz_y = haz5[:haz5_display_maxbin + 1]

# =========================
# Plot
# Keep your original simple style
# =========================
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

# Top: Hist5ms
ax = axes[0]
ax.plot(hist_x, hist_y, lw=1.5)
ax.set_xlim(0, HIST_XMAX)
ax.set_xlabel("ISI (ms)")
ax.set_ylabel("Count")
ax.set_title("Cell Hist5ms")
ax.spines[['top', 'right']].set_visible(False)

# Bottom: Haz5ms
ax = axes[1]
ax.plot(haz_x, haz_y, lw=1.5)
ax.set_xlim(0, HAZ_XMAX)
ax.set_xlabel("ISI (ms)")
ax.set_ylabel("Haz5ms (%)")
ax.set_title("Cell Haz5ms")
ax.spines[['top', 'right']].set_visible(False)

plt.tight_layout()
plt.show()