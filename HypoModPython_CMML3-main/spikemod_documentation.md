# SpikeModel Documentation

## Overview

`spikemod.py` implements a **computational neuron spike model** combined with a **hormone secretion model**, designed to simulate and analyze the firing behaviour of neuroendocrine cells (e.g., hypothalamic vasopressin or oxytocin neurons). The model is built on top of the `HypoModPy` framework and uses a `wxPython` GUI for interactive parameter control and visualization.

The simulation runs in **millisecond time steps** and generates:
- Synthetic spike trains for statistical comparison against recorded cell data
- Intracellular calcium dynamics
- Hormone secretion and plasma concentration time series

---

## File Structure

```
spikemod.py       — Main simulation module (GUI, model loop)
export_data.py    — Save model output to .npz files
celldata.py       — Load recorded cell spike data and compute ISI / hazard
fitting.py        — Plot model vs cell ISI histogram and hazard function
diffinput.py      — F-I curve and secretion vs input strength comparison
secretion.py      — Plasma secretion time series across NMDA parameter conditions
```

## Architecture (`spikemod.py`)

```
spikemod.py
├── SecData         — Data container for secretion model outputs
├── SpikeMod        — Main module class (GUI, data management, plot setup)
│   ├── PlotData()      — Defines all available plots
│   ├── DefaultPlots()  — Sets default panel views
│   ├── NeuroData()     — Loads and analyses recorded cell spike data
│   ├── ModelData()     — Analyses model-generated spike data
│   ├── RunModel()      — Launches the model in a background thread
│   └── OnModThread*()  — Thread event handlers (progress, completion)
└── SpikeModel      — Background thread that runs the simulation
    ├── run()           — Thread entry point
    └── Model()         — Core simulation loop
```

---

## Classes

### `SecData(size)`

A data container holding time-series arrays for all secretion model variables.

| Attribute | Description |
|-----------|-------------|
| `secP` | Releasable vesicle pool size |
| `secR` | Reserve vesicle pool size |
| `secX` | Instantaneous secretion rate |
| `secPlasma` | Hormone plasma concentration |
| `secE` | Fast calcium (`[Ca²⁺]_fast`) |
| `secC` | Slow calcium (`[Ca²⁺]_slow`) |
| `secB` | Spike broadening variable |

---

### `SpikeMod(mainwin, tag)`

The top-level module class. Inherits from `Mod` (HypoModPy base class). Manages the GUI toolboxes, data stores, and plot definitions.

**Key responsibilities:**
- Initialises GUI panels: `SpikeBox`, `SecBox`, `GridBox`, `SpikeDataBox`
- Stores spike data for both recorded cell (`cellspike`) and model output (`modspike`)
- Defines all visualization plots via `PlotData()`
- Launches the model thread via `RunModel()`

**Key methods:**

#### `PlotData()`
Registers all available plots with the plot base. Plots include:
- Inter-spike interval (ISI) histograms at 5 ms bins (raw and normalised)
- Hazard functions at 5 ms bins
- Spike rate (1-second bins)
- Index of Dispersion (IoD) scatter plots
- Secretion model variables: pool sizes, secretion rate, plasma concentration, calcium signals

#### `NeuroData()`
Loads the currently selected recorded cell's spike times, converts units from seconds to milliseconds if necessary, runs statistical analysis (`SpikeDat.Analysis()`), and updates the display.

#### `ModelData()`
Runs statistical analysis on the model-generated spike train and updates the display panels.

#### `RunModel()`
Collects parameters from the GUI panels and launches a `SpikeModel` thread. Prevents double-running via `runflag`.

---

### `SpikeModel(mod, params)`

Background thread (inherits `ModThread`) that performs the actual simulation.

#### `run()`
Entry point for the thread. Sets the random seed based on `randomflag` (fixed seed `0` for reproducibility, or time-based for stochastic runs), then calls `Model()`.

#### `Model()`
The core simulation loop. Runs for `runtime` seconds at 1 ms time steps.

---

## Model Description

### Spiking Sub-model

The membrane potential `V` is updated each millisecond:

```
V = Vrest + tPSP + [DAP term] − tHAP − tAHP
```

| Variable | Description |
|----------|-------------|
| `Vrest` | Resting membrane potential (mV) |
| `tPSP` | Postsynaptic potential accumulator |
| `tHAP` | Hyperpolarising afterpotential (fast) |
| `tDAP` | Depolarising afterpotential (simple model) |
| `tAHP` | Afterhyperpolarisation (slow) |

A spike is fired when `V > Vthresh` and the time since the last spike exceeds the absolute refractory period (`absref = 2 ms`).

**PSP input** is generated stochastically: excitatory and inhibitory PSPs arrive as Poisson processes with rates `psprate` and `psprate × pspratio` respectively. Each PSP has magnitude `pspmag`.

---

### DAP Models (`DAP_model` parameter)

Three DAP (Depolarising AfterPotential) modes are available:

| Value | Mode | Description |
|-------|------|-------------|
| `0` | No DAP | No depolarising afterpotential |
| `1` | Simple DAP | Exponential decay; spike-driven increment `kDAP` |
| `2` | NMDA-based DAP | Biophysically detailed; uses NMDA receptor gating and Mg²⁺ block |

**NMDA DAP model details (`DAP_model == 2`):**
- Synaptic glutamate variable `x_NMDA` decays with time constant `tau_x_NMDA` and increases with each EPSP
- NMDA gating variable `s_NMDA` follows a two-state kinetic model (opening rate `alpha_NMDA`, closing rate `beta_NMDA`)
- Voltage-dependent Mg²⁺ block is computed using the Woodhull model (Jahr & Stevens 1990):
  ```
  Mg_block = 1 / (1 + (Mg_conc / 3.57) × exp(−0.062 × V))
  ```
- NMDA current: `I_NMDA = gNMDA × s_NMDA × Mg_block × (V − E_NMDA)`
- Ca²⁺ influx through NMDA channels contributes to the fast calcium variable `tE`

---

### Secretion Sub-model

Calcium and secretion dynamics are computed each millisecond:

| Variable | Description |
|----------|-------------|
| `tB` | Spike broadening (decays with `tauB`; incremented by `kB` per spike) |
| `tE` | Fast calcium (decays with `tauE`; incremented by `kE × CaEnt` per spike) |
| `tC` | Slow calcium (decays with `tauC`; incremented by `kC × CaEnt` per spike) |

**Calcium entry** per spike:
```
CaEnt = Einh × Cinh × (tB + Bbase)
```
where `Einh` and `Cinh` are inhibitory sigmoidal functions of `tE` and `tC`, modelling calcium-dependent inactivation.

**Secretion rate**:
```
secX = tE^n × alpha × tP
```
where `n = 3` (oxytocin) or `n = 2` (vasopressin), `alpha` is the rate constant, and `tP` is the releasable pool size.

**Pool dynamics:**
- Releasable pool `tP` is depleted by secretion and refilled from reserve store `tR`
- Reserve store `tR` is depleted as it fills the releasable pool

**Plasma concentration:**
```
tPlasma = tPlasma + secX − tPlasma × tauClear
```
Concentration is reported as `tPlasma / VolPlasma`.

---

## Key Parameters

### Spike Parameters (`spikeparams`)

| Parameter | Description | Units |
|-----------|-------------|-------|
| `runtime` | Simulation duration | seconds |
| `hstep` | Integration time step | ms |
| `Vthresh` | Spike threshold | mV |
| `Vrest` | Resting potential | mV |
| `pspmag` | PSP magnitude | mV |
| `psprate` | Excitatory PSP rate | Hz |
| `pspratio` | Inhibitory/excitatory PSP ratio | — |
| `halflifeMem` | Membrane PSP decay half-life | ms |
| `kHAP` / `halflifeHAP` | HAP amplitude / half-life | mV / ms |
| `kDAP` / `halflifeDAP` | DAP amplitude / half-life (simple model) | mV / ms |
| `kAHP` / `halflifeAHP` | AHP amplitude / half-life | mV / ms |
| `DAP_model` | DAP mode: 0=none, 1=simple, 2=NMDA | — |
| `gNMDA` | NMDA conductance | mS/cm² |
| `tau_NMDA_rise` | NMDA rise time constant | ms |
| `tau_NMDA_decay` | NMDA decay time constant | ms |
| `tau_x_NMDA` | Glutamate decay time constant | ms |
| `Mg_conc` | Extracellular Mg²⁺ concentration | mM |
| `E_NMDA` | NMDA reversal potential | mV |
| `NMDA_Ca_fraction` | Fraction of NMDA current as Ca²⁺ | — |

### Secretion Parameters (`secparams`)

| Parameter | Description | Units |
|-----------|-------------|-------|
| `halflifeB` | Spike broadening half-life | ms |
| `halflifeE` | Fast Ca²⁺ half-life | ms |
| `halflifeC` | Slow Ca²⁺ half-life | ms |
| `Eth` / `Cth` | Fast/slow Ca²⁺ inhibition thresholds | — |
| `Bbase` | Baseline broadening | — |
| `alpha` | Secretion rate constant | s⁻¹ |
| `kB` / `kE` / `kC` | Per-spike increments for B, E, C | — |
| `Pmax` | Maximum releasable pool size | — |
| `Rinit` | Initial reserve pool size | — |
| `beta` | Refilling rate from reserve to releasable | — |
| `Rmax` | Maximum reserve pool size | — |
| `secExp` | Secretion Ca²⁺ exponent (2=oxy, 3=vaso) | — |
| `VolPlasma` | Plasma volume (for concentration) | — |
| `halflifeClear` | Plasma clearance half-life | s |

---

## Output Data

After a model run completes, the following are available:

- **`mod.modspike`** — `SpikeDat` object containing spike times, ISI histograms, hazard functions, IoD data, and mean firing rate
- **`mod.secdata`** — `SecData` object with time-series arrays for all secretion variables (sampled at `datsample` ms intervals)

---

## Data Export (`export_data.py`)

`export_data()` saves the current model run to a `.npz` file for offline analysis and plotting.

### Usage

```python
# Called automatically at end of run, or manually from the console:
from export_data import export_data
export_data(mod, label='model1_dap')
```

### Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mod` | `SpikeMod` | required | The running module object (`self` in `spikemod.py`) |
| `label` | `str` | `"run"` | Filename label to distinguish runs (e.g. `"model2_gNMDA02"`) |
| `out_dir` | `str` | `None` | Output directory; defaults to `exported_data/` next to the script |

Files are saved as: `{label}_{YYYYMMDD_HHMMSS}.npz`

### Saved Data Fields

| Key | Description |
|-----|-------------|
| `model_hist5norm` | Model normalised ISI histogram (5 ms bins) |
| `model_haz5` | Model hazard function (5 ms bins) |
| `model_freq` | Model mean firing frequency (Hz) |
| `model_spikecount` | Total model spike count |
| `cell_hist5norm` | Cell normalised ISI histogram (zeros if no cell loaded) |
| `cell_haz5` | Cell hazard function |
| `cell_freq` | Cell mean firing frequency (Hz) |
| `cell_spikecount` | Cell spike count |
| `secX` | Secretion rate time series |
| `secPlasma` | Plasma hormone concentration time series |
| `datsample` | Sampling interval (ms) |
| `isi_bins` | ISI bin centres in ms (for plotting) |
| `time_axis` | Time axis in ms (for secretion plots) |

---

## Analysis Scripts

### `celldata.py` — Cell Spike Data Analysis

Loads recorded electrophysiology data from an Excel file and computes ISI histograms and hazard functions using the same algorithm as `HypoMod Analysis()`, enabling direct comparison with model output.

**Configuration (edit at top of file):**

```python
FILE = r"D:\path\to\oxydata dap cells.xlsx"   # Path to Excel file
SHEET = 0                                      # Sheet index
CELL_NAME = "CBA1R18A"                         # Column name for target cell
```

**Key parameters:**

| Variable | Description |
|----------|-------------|
| `BIN_MS` | Histogram bin width (default: 5 ms) |
| `HIST_XMAX` | Display range for ISI histogram (default: 250 ms) |
| `HAZ_XMAX` | Display range for hazard function (default: 500 ms) |
| `force_seconds` | If `True`, multiplies spike times by 1000 to convert s → ms |

**Output:** Two-panel figure showing the ISI histogram (top) and hazard function (bottom) for the selected cell.

---

### `fitting.py` — Model vs Cell Comparison

Loads a single `.npz` export file and overlays model and cell ISI histograms and hazard functions side-by-side. Used to visually assess how well the model matches recorded cell firing statistics.

**Configuration (edit at top of file):**

```python
f = np.load('model2neuron6_PSP320_kDAP0.00_20260415_164650.npz', allow_pickle=True)
```

**Output:** Two-panel figure saved as `ISI_haz_0_500ms.png`:
- Left: Normalised ISI histogram (0–500 ms), model (blue) vs cell (orange dashed)
- Right: Hazard function (0–2000 ms), model (blue) vs cell (orange dashed)

Each trace is labelled with spike count and mean firing frequency.

---

### `diffinput.py` — F-I Curve and Secretion vs Input Strength

Loads paired `.npz` files across a range of PSP input strengths, with and without DAP, and plots the F-I (frequency–input) curve and mean plasma secretion vs input.

**Configuration:** Edit the `files_no_dap` and `files_with_dap` dictionaries to point to your exported files at each PSP level:

```python
files_no_dap = {
    250: 'model1_PSP250_kDAP0.00_...npz',
    300: 'model1_PSP300_kDAP0.00_...npz',
    ...
}
files_with_dap = {
    250: 'model1_PSP250_kDAP2.10_...npz',
    ...
}
psp_vals = [250, 275, 300, 325, 350]   # Must match dictionary keys
```

**Output:** Two-panel figure saved as `FI_secretion_input.png`:
- Left: Firing frequency (Hz) vs PSP input strength — with and without DAP
- Right: Mean plasma secretion (a.u.) vs PSP input strength — with and without DAP

---

### `secretion.py` — Secretion Time Series Across NMDA Conditions

Loads multiple `.npz` files (one per NMDA parameter condition) and plots plasma secretion and smoothed secretion rate over time, allowing comparison of how `kNMDA` affects secretion dynamics.

**Configuration:**

```python
files = {
    'kNMDA=0.00':  'model2_PSP320_kNMDA0.00_...npz',
    'kNMDA=0.005': 'model2_PSP320_kNMDA0.05_...npz',
    ...
}
N = 10000       # Number of time points to plot
window = 200    # Moving average window (ms) for smoothing secX
```

**Output:** Two-panel figure saved as `kNMDA_secretion_comparison.png`:
- Top: Plasma hormone concentration over time for each condition
- Bottom: Smoothed instantaneous secretion rate over time

---

## Typical Workflow

```
1. Run spikemod.py in HypoMod GUI
   → Set parameters in SpikeBox / SecBox panels
   → Click Run

2. Export results
   from export_data import export_data
   export_data(mod, label='model1_PSP300_kDAP2.1')

3. Load recorded cell data
   → Edit FILE, SHEET, CELL_NAME in celldata.py
   → Run celldata.py to inspect cell ISI / hazard

4. Compare model to cell
   → Edit filename in fitting.py
   → Run fitting.py → saves ISI_haz_0_500ms.png

5. Sweep input strength
   → Run model at multiple PSP levels with/without DAP
   → Edit file lists in diffinput.py
   → Run diffinput.py → saves FI_secretion_input.png

6. Compare secretion across NMDA conditions
   → Run model at multiple kNMDA values
   → Edit file list in secretion.py
   → Run secretion.py → saves kNMDA_secretion_comparison.png
```

---

## Dependencies

| Module | Used in | Purpose |
|--------|---------|---------|
| `wx` | `spikemod.py` | GUI framework |
| `numpy` | all | Array operations |
| `random`, `math` | `spikemod.py` | Stochastic PSP generation, time constants |
| `HypoModPy` | `spikemod.py` | Base classes for modules, parameters, data, grids, spikes |
| `spikepanels` | `spikemod.py` | GUI panel definitions (`SpikeBox`, `SecBox`) |
| `export_data` | `spikemod.py` | Data export utility |
| `matplotlib` | `celldata.py`, `fitting.py`, `diffinput.py`, `secretion.py` | Plotting |
| `pandas` | `celldata.py`, `secretion.py` | Excel reading, rolling average |

---

## References

- Jahr, C.E. & Stevens, C.F. (1990). Voltage dependence of NMDA-activated macroscopic conductances predicted by single-channel kinetics. *Journal of Neuroscience*, 10(9), 3178–3182.
- Woodhull, A.M. (1973). Ionic blockage of sodium channels in nerve. *Journal of General Physiology*, 61(6), 687–708.
