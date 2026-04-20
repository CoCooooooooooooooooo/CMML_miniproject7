import numpy as np
import matplotlib.pyplot as plt

# file of model 1 (HAP-based), neuron 4, with and without DAP, at different PSP levels
files_no_dap = {
    250: 'model1_PSP250_kDAP0.00_20260416_110532.npz',
    275: 'model1_PSP275_kDAP0.00_20260416_110507.npz',
    300: 'model1_PSP300_kDAP0.00_20260415_234603.npz',
    325: 'model1_PSP325_kDAP0.00_20260416_110442.npz',
    350: 'model1_PSP350_kDAP0.00_20260416_110223.npz',
}

files_with_dap = {
    250: 'model1_PSP250_kDAP2.10_20260416_105953.npz',
    275: 'model1_PSP275_kDAP2.10_20260416_110022.npz',
    300: 'model1neuron4_PSP300_kDAP2.10_20260415_142203.npz',
    325: 'model1_PSP325_kDAP2.10_20260416_110048.npz',
    350: 'model1_PSP350_kDAP2.10_20260416_110155.npz',
}

psp_vals = [250, 275, 300, 325, 350]

freq_no_dap, freq_with_dap = [], []
plasma_no_dap, plasma_with_dap = [], []

for psp in psp_vals:
    f0 = np.load(files_no_dap[psp], allow_pickle=True)
    f1 = np.load(files_with_dap[psp], allow_pickle=True)

    freq_no_dap.append(float(f0['model_freq']))
    freq_with_dap.append(float(f1['model_freq']))
    plasma_no_dap.append(float(f0['secPlasma'].mean()))
    plasma_with_dap.append(float(f1['secPlasma'].mean()))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# --- left：F-I curve ---
ax = axes[0]
ax.plot(psp_vals, freq_no_dap,   'o-', color='#888780', linewidth=2, markersize=7, label='kDAP=0.00 (no DAP)')
ax.plot(psp_vals, freq_with_dap, 'o-', color='#3266ad', linewidth=2, markersize=7, label='kDAP=2.10 (with DAP)')
ax.set_xlabel('Input strength (PSP)', fontsize=12)
ax.set_ylabel('Firing frequency (Hz)', fontsize=12)
ax.set_title('F-I curve — model 1 (HAP-based), neuron 3', fontsize=13)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# --- right：Mean secretion vs input ---
ax = axes[1]
ax.plot(psp_vals, plasma_no_dap,   'o-', color='#888780', linewidth=2, markersize=7, label='kDAP=0.00 (no DAP)')
ax.plot(psp_vals, plasma_with_dap, 'o-', color='#3266ad', linewidth=2, markersize=7, label='kDAP=2.10 (with DAP)')
ax.set_xlabel('Input strength (PSP)', fontsize=12)
ax.set_ylabel('Mean plasma secretion (a.u.)', fontsize=12)
ax.set_title('Secretion vs input — model 1 (HAP-based), neuron 3', fontsize=13)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('FI_secretion_input.png', dpi=150)
plt.show()