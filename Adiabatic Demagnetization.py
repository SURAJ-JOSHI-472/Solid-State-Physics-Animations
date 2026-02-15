import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from scipy.optimize import brentq

plt.style.use("dark_background")

# Constants
kB = 1.0
muB = 1.0
gJ = 2.0
alpha = 0.05

mJ = np.array([-0.5, 0.5])

n_spins = 64
rows, cols = 8, 8
# Increase spacing multiplier to spread arrows apart
spacing = 4.0
x_positions, y_positions = np.meshgrid(np.arange(cols)*spacing, np.arange(rows)*spacing)
x_positions, y_positions = x_positions.flatten(), y_positions.flatten()

states = ["a: Random spins (high T & Low Field)",
          "b: Isothermal Magnetization (Field ON)",
          "c: Adiabatic Demagnetization (Field OFF, S=constant)"]
current_state = 0

# --- Entropy calculation with clipping ---
def entropy(B, T):
    if T <= 0:
        return 0.0
    x = np.clip(mJ * gJ * muB * B / (kB * T), -700, 700)
    Z = np.sum(np.exp(x))
    p = np.exp(x) / Z
    p = np.clip(p, 1e-12, 1.0)
    S_spin = -kB * np.sum(p * np.log(p))
    S_lattice = alpha * T**3
    return S_spin + S_lattice

def sample_spins(B, T):
    if T <= 0:
        return np.ones(n_spins) * 0.5
    probs = np.exp(mJ * gJ * muB * B / (kB * T))
    probs /= probs.sum()
    spins = np.random.choice(mJ, size=n_spins, p=probs)
    return spins

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
plt.subplots_adjust(bottom=0.3)

# Adjust quiver scale so arrows are longer
quiver = ax1.quiver(x_positions, y_positions,
                    np.zeros_like(x_positions), np.ones_like(y_positions),
                    angles='xy', scale_units='xy', scale=0.5, color="orange",
                    headwidth=3, headlength=4, headaxislength=3)
ax1.set_xlim(-spacing, cols*spacing)
ax1.set_ylim(-spacing, rows*spacing)
ax1.set_aspect('equal')
ax1.axis("off")

T_vals = np.linspace(0.0, 3, 1000)
B_values = [0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0]
colors = plt.cm.plasma(np.linspace(0, 1, len(B_values)))

for B, c in zip(B_values, colors):
    S_vals = [entropy(B, Ti) for Ti in T_vals]
    ax2.plot(T_vals, S_vals, color=c, label=f"B={B:.2f}")

dot, = ax2.plot([], [], "bo", markersize=8)
ax2.set_xlabel("Temperature (T)")
ax2.set_ylabel("Entropy (S)")
ax2.set_title("Cooling Path")
ax2.legend()

Ti = 2.0
Bb = 3.0

path_a, = ax2.plot([], [], "--", color="cyan", linewidth=2)
path_b, = ax2.plot([], [], "--", color="yellow", linewidth=2)

labels = []

def update_plot():
    global current_state, Ti, Bb, path_a, path_b, labels

    Si = entropy(0.01, Ti)
    Sb = entropy(Bb, Ti)
    Tf = brentq(lambda T: entropy(0.01, T) - Sb, 0.01, Ti)
    Sc = entropy(0.01, Tf)

    path_a.set_data([Ti, Ti], [Si, Sb])
    path_b.set_data([Ti, Tf], [Sb, Sb])

    for lbl in labels:
        lbl.remove()
    labels.clear()

    labels.append(ax2.text(Ti+0.1, Si, "a", fontsize=12))
    labels.append(ax2.text(Ti+0.1, Sb, "b", fontsize=12))
    labels.append(ax2.text(Tf+0.1, Sb, "c", fontsize=12))

    if current_state == 0:
        spins = sample_spins(B=0.01, T=Ti)
        dot.set_data([Ti], [Si])
    elif current_state == 1:
        spins = sample_spins(B=Bb, T=Ti)
        dot.set_data([Ti], [Sb])
    elif current_state == 2:
        spins = sample_spins(B=0.01, T=Tf)
        dot.set_data([Tf], [Sb])

    u = np.zeros_like(spins)
    v = np.where(spins > 0, 1, -1)
    quiver.set_UVC(u, v)

    ax1.set_title(states[current_state])
    fig.canvas.draw_idle()

def next_state(event):
    global current_state
    current_state = (current_state + 1) % len(states)
    update_plot()

def prev_state(event):
    global current_state
    current_state = (current_state - 1) % len(states)
    update_plot()

axprev = plt.axes([0.3, 0.05, 0.1, 0.075])
axnext = plt.axes([0.6, 0.05, 0.1, 0.075])
bnext = Button(axnext, 'Next', color='darkred', hovercolor='red')
bprev = Button(axprev, 'Previous', color='darkblue', hovercolor='blue')
bnext.on_clicked(next_state)
bprev.on_clicked(prev_state)

axbox_Ti = plt.axes([0.15, 0.25, 0.1, 0.05], facecolor="lightgray")
text_box_Ti = TextBox(axbox_Ti, '$T_i$', initial=str(Ti))
text_box_Ti.text_disp.set_color("black")
def submit_Ti(text):
    global Ti
    Ti = float(text)
    update_plot()
text_box_Ti.on_submit(submit_Ti)

axbox_Bb = plt.axes([0.35, 0.25, 0.1, 0.05], facecolor="lightgray")
text_box_Bb = TextBox(axbox_Bb, '$B_b$', initial=str(Bb))
text_box_Bb.text_disp.set_color("black")
def submit_Bb(text):
    global Bb
    Bb = float(text)
    update_plot()
text_box_Bb.on_submit(submit_Bb)

update_plot()
plt.show()
