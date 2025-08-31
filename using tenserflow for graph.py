import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# Training data (force float32 for TensorFlow)
xx = np.array([15, 30, 45, 60, 75], dtype=np.float32)
yy = np.array([25, 50, 75, 100, 125], dtype=np.float32)

# Variables for slope and intercept (also float32)
sl = tf.Variable(0.0, dtype=tf.float32)
intc = tf.Variable(0.0, dtype=tf.float32)

# Optimizer
opt = tf.optimizers.SGD(learning_rate=0.001)

# Training loop
for i in range(5000):
    with tf.GradientTape() as t:
        yp = sl * xx + intc
        l = tf.reduce_mean((yy - yp) ** 2)
    dsl, dint = t.gradient(l, [sl, intc])
    opt.apply_gradients([(dsl, sl), (dint, intc)])

    if i % 1000 == 0:
        print(f"Step {i}: loss={l.numpy():.4f}, m={sl.numpy():.4f}, c={intc.numpy():.4f}")

# Results
print("Final slope (m):", sl.numpy())
print("Final intercept (c):", intc.numpy())

# Prediction
p = sl.numpy() * 60 + intc.numpy()
print("Prediction for x=60 → y:", p)

# Plot
plt.figure(figsize=(8,6))
plt.scatter(xx, yy, color="blue", label="Data points")

x_line = np.linspace(10, 80, 100, dtype=np.float32)
y_line = sl.numpy() * x_line + intc.numpy()

plt.plot(x_line, y_line, color="red", linewidth=2, label="Fitted line")
plt.legend()
plt.xlabel("X values")
plt.ylabel("Y values")
plt.title("Linear Regression using TensorFlow")
plt.grid(True)
plt.show()
