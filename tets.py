import numpy as np
import matplotlib.pyplot as plt

# Definiera fältet för x- och y-värden
x_vals = np.linspace(0, 5, 20)
y_vals = np.linspace(0, 5, 20)
X, Y = np.meshgrid(x_vals, y_vals)

# Definiera differentialekvationen y' = 3 - y
dy = 3 - Y
dx = np.ones_like(dy)  # dx är alltid 1 för att få riktningsvektorer

# Normalisera vektorerna för bättre visualisering
length = np.sqrt(dx**2 + dy**2)
dx /= length
dy /= length

# Rita riktningsfältet
plt.figure(figsize=(8, 6))
plt.quiver(X, Y, dx, dy, angles="xy", scale_units="xy", scale=1, color="blue")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Riktningsfält för differentialekvationen $y' = 3 - y$")
plt.axhline(y=3, color="r", linestyle="--", label="Jämviktspunkt y=3")
plt.legend()
plt.grid()
plt.show()
