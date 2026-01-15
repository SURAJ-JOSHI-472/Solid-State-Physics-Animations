import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

# Parameters
N = 20          # number of atoms
a = 1.0         # lattice spacing
K = 1.0         # spring constant
M1, M2 = 1.0, 1e-3   # initial masses

# Atom positions
x = np.arange(N) * a

# Dispersion relation for diatomic lattice
def omega_branches(k, M1, M2, K=K, a=a):
    term = K*(M1+M2)/(M1*M2)
    discr = term**2 - (4*K**2/(M1*M2)) * (np.sin(k*a/2)**2)
    omega2_plus = term + np.sqrt(np.maximum(discr,0))
    omega2_minus = term - np.sqrt(np.maximum(discr,0))
    return np.sqrt(np.maximum(omega2_minus,0)), np.sqrt(np.maximum(omega2_plus,0))

# k values
k_vals = np.linspace(-np.pi/a, np.pi/a, 200)

# Initial dispersion
omega_acoustic, omega_optical = omega_branches(k_vals, M1, M2)

# Current k and branch selection
k_current = [np.pi/4]
branch_current = ["acoustic"]  # "acoustic" or "optical"

# Figure setup
plt.rcParams["font.family"] = "Times New Roman"
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
plt.subplots_adjust(bottom=0.25)

# Left subplot: lattice vibrations
ax1 = axes[0]
scat = ax1.scatter([], [], s=[], c=[])  # scatter with variable sizes and colors
ax1.set_xlim(-1, N*a)
ax1.set_ylim(-1, 1)
ax1.set_title("Diatomic lattice vibrations", fontsize=14)
ax1.set_xlabel("Atom index", fontsize=12)
ax1.set_ylabel("Displacement", fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.6)

# Right subplot: dispersion relation
ax2 = axes[1]
line_acoustic, = ax2.plot(k_vals*a/np.pi, omega_acoustic, color='black', label="Acoustic")
line_optical, = ax2.plot(k_vals*a/np.pi, omega_optical, color='red', label="Optical")
dot, = ax2.plot([k_current[0]*a/np.pi], [omega_branches(k_current[0], M1, M2)[0]], 'ro', markersize=8)
ax2.set_title("Dispersion relation ω(k)", fontsize=14)
ax2.set_xlabel("Wavevector k (units of π/2a)", fontsize=12)
ax2.set_ylabel("Frequency ω", fontsize=12)
ax2.set_xlim(-1.1, 1.1)
ax2.set_ylim(0, max(omega_optical)+1)
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.6)

# --- Mouse interaction: select branch ---
def on_click(event):
    if event.inaxes == ax2:
        k_new = event.xdata * np.pi / a
        if -np.pi/a <= k_new <= np.pi/a:
            k_current[0] = k_new
            w_ac, w_op = omega_branches(k_new, M1, M2)
            if abs(event.ydata - w_ac) < abs(event.ydata - w_op):
                branch_current[0] = "acoustic"
                dot.set_data([event.xdata], [w_ac])
            else:
                branch_current[0] = "optical"
                dot.set_data([event.xdata], [w_op])
            fig.canvas.draw_idle()

fig.canvas.mpl_connect("button_press_event", on_click)

# --- Slider for one mass (M2) ---
ax_slider = plt.axes([0.05, 0.01, 0.05, 0.03])
slider_M2 = Slider(ax_slider, 'Mass M2', 0.5, 5.0, valinit=M2)

def update_slider(val):
    global M2, omega_acoustic, omega_optical
    M2 = slider_M2.val
    omega_acoustic, omega_optical = omega_branches(k_vals, M1, M2)
    line_acoustic.set_ydata(omega_acoustic)
    line_optical.set_ydata(omega_optical)
    ax2.set_ylim(0, max(omega_optical)+1)
    fig.canvas.draw_idle()

slider_M2.on_changed(update_slider)

# --- Animation update ---
def update(frame):
    k = k_current[0]
    w_ac, w_op = omega_branches(k, M1, M2)
    t = frame / 10
    y = np.zeros_like(x)
    sizes = []
    colors = []
    if branch_current[0] == "acoustic":
        for n in range(N):
            y[n] = 0.3*np.sin(k*x[n] - w_ac*t)
            sizes.append(100*M1 if n % 2 == 0 else 100*M2)
            colors.append('black' if n % 2 == 0 else 'red')
        dot.set_data([k*a/np.pi], [w_ac])
    else:
        for n in range(N):
            if n % 2 == 0:
                y[n] = 0.3*np.sin(k*x[n] - w_op*t)
                sizes.append(100*M1)
                colors.append('black')
            else:
                y[n] = -0.3*np.sin(k*x[n] - w_op*t)  # opposite phase
                sizes.append(100*M2)
                colors.append('red')
        dot.set_data([k*a/np.pi], [w_op])
    scat.set_offsets(np.c_[x, y])
    scat.set_sizes(sizes)
    scat.set_color(colors)
    return scat, dot

ani = animation.FuncAnimation(fig, update, frames=200, interval=50, blit=True)

plt.tight_layout()
plt.show()