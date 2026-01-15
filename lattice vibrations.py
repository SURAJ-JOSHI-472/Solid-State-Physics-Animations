import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Parameters
N = 30          # number of atoms
a = 1.0         # lattice spacing
K = 1.0         # spring constant
M = 1.0         # mass

# Atom positions
x = np.arange(N) * a

# Dispersion relation
def omega(k):
    return 2*np.sqrt(K/M)*np.abs(np.sin(k*a/2))

# k values across Brillouin zone
k_vals = np.linspace(-4*np.pi/a, 4*np.pi/a, 1000)
omega_vals = omega(k_vals)

# Initial k
k_current = [np.pi/4]

# Figure setup
plt.rcParams["font.family"] = "Times New Roman"
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left subplot: lattice vibrations
ax1 = axes[0]
points, = ax1.plot([], [], 'o-', color='blue')
ax1.set_xlim(-1, N*a)
ax1.set_ylim(-1, 1)
ax1.set_title("Lattice vibrations", fontsize=14)
ax1.set_xlabel("Atom index", fontsize=12)
ax1.set_ylabel("Displacement", fontsize=12)

# Right subplot: dispersion relation
ax2 = axes[1]
ax2.plot(k_vals*a/np.pi, omega_vals, color='black')
ax1.grid(True)   # adds grid to subplot ax1
ax2.grid(True)   # adds grid to subplot ax2
dot, = ax2.plot([k_current[0]*a/np.pi], [omega(k_current[0])], 'ro', markersize=8)
ax2.set_title("Dispersion relation ω(k)", fontsize=14)
ax2.set_xlabel("Wavevector k (units of π/a)", fontsize=12)
ax2.set_ylabel("Frequency ω", fontsize=12)
ax2.set_xlim(-4, 4)
ax2.set_ylim(0, 2*np.sqrt(K/M)+0.5)

# --- Mouse interaction ---
def on_click(event):
    # Only respond if click is inside dispersion subplot
    if event.inaxes == ax2:
        # Convert x back to k (units π/a → radians)
        k_new = event.xdata * np.pi / a
        # Clamp to Brillouin zone
        if -4*np.pi/a <= k_new <= 4*np.pi/a:
            k_current[0] = k_new
            # Move dot immediately
            dot.set_data([event.xdata], [omega(k_new)])
            fig.canvas.draw_idle()

fig.canvas.mpl_connect("button_press_event", on_click)

# --- Animation update ---
def update(frame):
    k = k_current[0]
    w = omega(k)
    t = frame / 10
    y = 0.3 * np.sin(k*x - w*t)
    points.set_data(x, y)
    dot.set_data([k*a/np.pi], [w])
    return points, dot

ani = animation.FuncAnimation(fig, update, frames=200, interval=50, blit=True)

plt.tight_layout()
plt.show()