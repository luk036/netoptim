# Figures Demo

Auto-generated figures demonstrating netoptim functionality.

## Network Flow Graph

```{plot} examples/plot_network_flow.py
```

## Network Oracle Example

```{plot} examples/plot_network_oracle.py
```

### Inline Plot Example

```{plot}
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 100)
plt.plot(x, np.sin(x))
plt.title("Simple Sine Wave")
plt.grid(True, alpha=0.3)
```
