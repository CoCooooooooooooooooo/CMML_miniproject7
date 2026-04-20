import numpy as np
import matplotlib.pyplot as plt

f = np.load('model2neuron6_PSP320_kDAP0.00_20260415_164650.npz', allow_pickle=True)

isi_bins   = f['isi_bins']
model_hist = f['model_hist5norm']
cell_hist  = f['cell_hist5norm']
model_haz  = f['model_haz5']
cell_haz   = f['cell_haz5']

cell_bins = np.array([2.5 + 5 * i for i in range(len(cell_hist))])

mask_model     = isi_bins  <= 500
mask_cell      = cell_bins <= 500
mask_model_haz = isi_bins  <= 2000
mask_cell_haz  = cell_bins <= 2000

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

# --- left：ISI histogram ---
ax = axes[0]
ax.plot(isi_bins[mask_model], model_hist[mask_model],
        color='#3266ad', linewidth=1.5,
        label=f'Model (n={int(f["model_spikecount"])}, {float(f["model_freq"]):.2f} Hz)')
ax.fill_between(isi_bins[mask_model], model_hist[mask_model],
                alpha=0.12, color='#3266ad')
ax.plot(cell_bins[mask_cell], cell_hist[mask_cell],
        color='#d85a30', linewidth=1.5, linestyle='--',
        label=f'Cell (n={int(f["cell_spikecount"])}, {float(f["cell_freq"]):.2f} Hz)')
ax.fill_between(cell_bins[mask_cell], cell_hist[mask_cell],
                alpha=0.10, color='#d85a30')
ax.set_xlabel('ISI (ms)', fontsize=12)
ax.set_ylabel('Normalized count (spikes/s/bin)', fontsize=12)
ax.set_title('ISI Histogram — model_2 vs cell (0–500 ms)', fontsize=13)
ax.legend(fontsize=11)
ax.set_xlim(0, 500)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# --- right：Hazard function ---
ax = axes[1]
ax.plot(isi_bins[mask_model_haz], model_haz[mask_model_haz],
        color='#3266ad', linewidth=1.5,
        label=f'Model (n={int(f["model_spikecount"])}, {float(f["model_freq"]):.2f} Hz)')
ax.fill_between(isi_bins[mask_model_haz], model_haz[mask_model_haz],
                alpha=0.12, color='#3266ad')
ax.plot(cell_bins[mask_cell_haz], cell_haz[mask_cell_haz],
        color='#d85a30', linewidth=1.5, linestyle='--',
        label=f'Cell (n={int(f["cell_spikecount"])}, {float(f["cell_freq"]):.2f} Hz)')
ax.fill_between(cell_bins[mask_cell_haz], cell_haz[mask_cell_haz],
                alpha=0.10, color='#d85a30')
ax.set_xlabel('ISI (ms)', fontsize=12)
ax.set_ylabel('Hazard rate (spikes/s)', fontsize=12)
ax.set_title('Hazard Function — model_2 vs cell (0–2000 ms)', fontsize=13)
ax.legend(fontsize=11)
ax.set_xlim(0, 2000)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('ISI_haz_0_500ms.png', dpi=150)
plt.show()