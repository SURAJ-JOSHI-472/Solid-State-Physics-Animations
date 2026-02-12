import matplotlib.pyplot as plt
import numpy as np
from fractions import Fraction
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.style.use('dark_background')

def format_value(val):
    frac = Fraction(val).limit_denominator()
    if frac.denominator == 1:
        return f"{frac.numerator}"
    else:
        return f"{frac.numerator}/{frac.denominator}"

class CouplingAnimation:
    def __init__(self, root):
        self.root = root
        self.root.title("Angular Momentum Coupling Animation")
        self.root.configure(bg="#1e1e1e")  # dark background

        # Input fields with dark theme
        label_style = {"bg":"#1e1e1e", "fg":"#00ffff", "font":("Arial", 12, "bold")}
        entry_style = {"bg":"#2d2d2d", "fg":"#ffffff", "insertbackground":"white",
                       "font":("Consolas", 12), "relief":"flat"}

        tk.Label(root, text="Enter L:", **label_style).pack(pady=(10,0))
        self.L_entry = tk.Entry(root, **entry_style, width=10)
        self.L_entry.pack(pady=5)

        tk.Label(root, text="Enter S:", **label_style).pack(pady=(10,0))
        self.S_entry = tk.Entry(root, **entry_style, width=10)
        self.S_entry.pack(pady=5)

        # Buttons with dark theme
        btn_style = {"bg":"#333333", "fg":"#00ff00", "activebackground":"#444444",
                     "activeforeground":"#ffffff", "font":("Arial", 11, "bold"),
                     "relief":"flat", "width":10, "height":1}

        tk.Button(root, text="Start", command=self.start, **btn_style).pack(pady=10)
        self.prev_button = tk.Button(root, text="Previous", command=self.prev_step, state=tk.DISABLED, **btn_style)
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=10)
        self.next_button = tk.Button(root, text="Next", command=self.next_step, state=tk.DISABLED, **btn_style)
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=10)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10,7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.step = 0

    def start(self):
        try:
            self.L = int(self.L_entry.get())
            self.S = float(self.S_entry.get())
        except:
            return

        self.step = 0
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)
        self.update_plot()

    def next_step(self):
        self.step += 1
        self.prev_button.config(state=tk.NORMAL)
        if self.step >= 3:
            self.next_button.config(state=tk.DISABLED)
        self.update_plot()

    def prev_step(self):
        self.step -= 1
        self.next_button.config(state=tk.NORMAL)
        if self.step <= 0:
            self.prev_button.config(state=tk.DISABLED)
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.ax.set_title(f"Coupling Scheme (L={self.L}, S={format_value(self.S)})", fontsize=14, color='cyan')
        theta = np.deg2rad(135)

        # Rectangle
        m_L_values = np.arange(-self.L, self.L+1, 1)
        m_S_values = np.arange(-self.S, self.S+1, 1)
        X, Y = np.meshgrid(m_L_values, m_S_values)
        X_rot = X*np.cos(theta) - Y*np.sin(theta)
        Y_rot = X*np.sin(theta) + Y*np.cos(theta)

        if self.step >= 1:
            for i in range(len(m_S_values)):
                for j in range(len(m_L_values)):
                    mL, mS = m_L_values[j], m_S_values[i]
                    self.ax.plot(X_rot[i,j], Y_rot[i,j], 'yo', markersize=8, markeredgecolor='white')
                    self.ax.text(X_rot[i,j], Y_rot[i,j]+0.25, f"{mL},{format_value(mS)}",
                                 ha='center', va='bottom', fontsize=9, color='lightgreen')

        # Vertical lines
        J_values = np.arange(abs(self.L-self.S), self.L+self.S+1, 1)
        mj_all = np.arange(-self.L-self.S, self.L+self.S+1, 1)
        y_offset = -self.S-12
        pyramid_bottom = y_offset - (len(J_values)-1)*2

        if self.step >= 2:
            for j in range(len(m_L_values)):
                for i in range(len(m_S_values)):
                    x_val = X_rot[i,j]
                    self.ax.plot([x_val, x_val], [np.max(Y_rot)+1, pyramid_bottom-1], 'w--', alpha=0.4)

        # Pyramid
        if self.step >= 3:
            for row, J in enumerate(J_values):
                for mj in mj_all:
                    if -J <= mj <= J:
                        x_rot = mj*np.cos(theta)
                        y = y_offset - row*2
                        self.ax.plot(x_rot, y, 'ro', markersize=8)
                        self.ax.text(x_rot, y-0.4, f"{format_value(mj)}",
                                     ha='center', va='top', color='orange', fontsize=9)
                self.ax.text(np.min(X_rot)-2.0, y_offset - row*2, f"J={format_value(J)}",
                             ha='right', va='center', color='lightblue', fontsize=11)

            # m_J labels below pyramid
            for mj in mj_all:
                x_rot = mj*np.cos(theta)
                self.ax.text(x_rot, pyramid_bottom-2, f"{format_value(mj)}",
                             ha='center', va='top', color='lightgreen', fontsize=10)
            self.ax.text(0, pyramid_bottom-3.5, "$m_J$", ha='center', color='cyan', fontsize=12)

        self.ax.axis('off')
        self.canvas.draw()

# Run GUI
root = tk.Tk()
app = CouplingAnimation(root)
root.mainloop()
