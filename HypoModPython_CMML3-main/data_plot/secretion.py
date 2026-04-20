import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# File list — modify according to your actual filenames
files = {
    'kNMDA=0.00': 'model2_PSP320_kNMDA0.00_20260415_234827.npz',
    'kNMDA=0.005': 'model2_PSP320_kNMDA0.05_20260415_234957.npz',
    'kNMDA=0.10': 'model2neuron2_PSP330_kDAP0.00_20260415_165341.npz',
    'kNMDA=0.15': 'model2_PSP320_kNMDA0.15_20260415_235042.npz',
    'kNMDA=0.20': 'model2_PSP320_kNMDA0.20_20260415_235132.npz',
}

colors = ['#888780', '#85b7eb', '#3266ad', '#d85a30', '#993c1d']

N = 10000
window = 200  # Moving average window size; adjustable

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

for (label, fname), color in zip(files.items(), colors):
    f = np.load(fname, allow_pickle=True)
    t = f['time_axis'][:N]
    plasma = f['secPlasma'][:N]
    secX   = f['secX'][:N]
    freq   = float(f['model_freq'])

    secX_smooth = pd.Series(secX).rolling(window, center=True).mean()

    axes[0].plot(t, plasma, color=color, linewidth=2.0, label=f'{label} ({freq:.2f} Hz)')
    axes[1].plot(t, secX_smooth, color=color, linewidth=1.5, label=label)

axes[0].set_ylabel('Plasma secretion (a.u.)', fontsize=12)
axes[0].set_title('Effect of kNMDA on secretion — model 2 (NMDA-based), neuron 2', fontsize=13)
axes[0].legend(fontsize=10)
axes[0].spines['top'].set_visible(False)
axes[0].spines['right'].set_visible(False)

axes[1].set_xlabel('Time (ms)', fontsize=12)
axes[1].set_ylabel('Secretion variable X — smoothed (a.u.)', fontsize=12)
axes[1].legend(fontsize=10)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('kNMDA_secretion_comparison.png', dpi=150)
plt.show()