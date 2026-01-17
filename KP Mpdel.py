import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

plt.style.use("dark_background")

# Parameters
P_init = 3 * np.pi / 2
a = 1.0
alpha_a = np.linspace(-8*np.pi, 8*np.pi, 20000)
alpha_a[alpha_a == 0] = 1e-6

def f_alpha(alpha_a, P):
    return P * np.sin(alpha_a) / alpha_a + np.cos(alpha_a)

def compute_allowed(P):
    f_vals = f_alpha(alpha_a, P)
    allowed = np.abs(f_vals) <= 1
    return allowed, f_vals

def compute_allowed_energies(P):
    allowed, _ = compute_allowed(P)
    energy = (alpha_a[allowed] / a)**2
    return energy

# --- Layout: two subplots side by side ---
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 6))
plt.subplots_adjust(bottom=0.25)

# --- Left plot: f(alpha a) vs alpha a ---
f_vals = f_alpha(alpha_a, P_init)
allowed_mask = np.abs(f_vals) <= 1

line_lhs, = ax_left.plot(alpha_a, f_vals, color='cyan', lw=2.5, label="f(αa)")
line_upper = ax_left.axhline(1, color='orange', linestyle='--', lw=2, visible=False)
line_lower = ax_left.axhline(-1, color='orange', linestyle='--', lw=2, visible=False)
fill_allowed_left = None

ax_left.set_xlim(-4*np.pi, 4*np.pi)
ax_left.set_ylim(-5, 10)
ax_left.set_xlabel(r"$\alpha a$", fontsize=14)
ax_left.set_ylabel(r"$f(\alpha a)$", fontsize=14)
ax_left.set_title("Kronig–Penney Band Formation", fontsize=16, fontweight='bold')
ax_left.grid(alpha=0.3)

xticks = np.arange(-4*np.pi, 4.1*np.pi, np.pi)
xtick_labels = [f"${int(t/np.pi)}\\pi$" if t != 0 else "0" for t in xticks]
ax_left.set_xticks(xticks)
ax_left.set_xticklabels(xtick_labels, fontsize=12)
ax_left.legend(loc='upper right', fontsize=12)

# --- Right plot: Allowed energy bands ---
bars = []
def plot_bands(energies):
    global bars
    for bar in bars:
        bar.remove()
    bars = []
    if len(energies) == 0:
        return
    energy_sorted = np.sort(energies)
    gaps = np.diff(energy_sorted) > 0.1
    band_edges = np.split(energy_sorted, np.where(gaps)[0]+1)
    for band in band_edges:
        if len(band) > 0:
            bar = ax_right.axhspan(band[0], band[-1], color='lime', alpha=0.6)
            bars.append(bar)

allowed_energy = compute_allowed_energies(P_init)
plot_bands(allowed_energy)

ax_right.set_xlim(0, 1)
ax_right.set_ylim(0, 200)
ax_right.set_xticks([])
ax_right.set_ylabel("Energy (arb. units)", fontsize=14)
ax_right.set_title("Allowed Energy Bands", fontsize=16, fontweight='bold')
ax_right.grid(alpha=0.3)

# --- Stage control for left plot ---
stage = [0]

def update_plot(P):
    global f_vals, allowed_mask, fill_allowed_left
    f_vals = f_alpha(alpha_a, P)
    allowed_mask = np.abs(f_vals) <= 1
    line_lhs.set_ydata(f_vals)
    if stage[0] >= 2:
        if fill_allowed_left:
            fill_allowed_left.remove()
        fill_allowed_left = ax_left.fill_between(alpha_a, -2, 6, where=allowed_mask,
                                                 color='lime', alpha=0.25, label='Allowed')
    # Update right plot
    energies = compute_allowed_energies(P)
    plot_bands(energies)
    fig.canvas.draw_idle()

def next_stage(event):
    global fill_allowed_left
    if stage[0] == 0:
        line_lhs.set_data(alpha_a, f_vals)
    elif stage[0] == 1:
        line_upper.set_visible(True)
        line_lower.set_visible(True)
    elif stage[0] == 2:
        if fill_allowed_left:
            fill_allowed_left.remove()
        fill_allowed_left = ax_left.fill_between(alpha_a, -2, 6, where=allowed_mask,
                                                 color='lime', alpha=0.25, label='Allowed')
        ax_left.legend(loc='upper right')
    stage[0] = min(stage[0] + 1, 2)
    fig.canvas.draw_idle()

def prev_stage(event):
    global fill_allowed_left
    if stage[0] == 2 and fill_allowed_left:
        fill_allowed_left.remove()
    if stage[0] == 1:
        line_upper.set_visible(False)
        line_lower.set_visible(False)
    if stage[0] == 0:
        line_lhs.set_data([], [])
    stage[0] = max(stage[0] - 1, 0)
    fig.canvas.draw_idle()

# --- Buttons ---
ax_next = plt.axes([0.8, 0.05, 0.1, 0.05], facecolor='dimgray')
btn_next = Button(ax_next, 'Next', color='darkgreen', hovercolor='green')
btn_next.on_clicked(next_stage)

ax_prev = plt.axes([0.68, 0.05, 0.1, 0.05], facecolor='dimgray')
btn_prev = Button(ax_prev, 'Back', color='darkred', hovercolor='red')
btn_prev.on_clicked(prev_stage)

# --- Slider for P ---
ax_slider = plt.axes([0.25, 0.1, 0.4, 0.03])
slider_P = Slider(ax_slider, 'Barrier Strength P', 0, 1000, valinit=P_init)
slider_P.on_changed(update_plot)

plt.show()
