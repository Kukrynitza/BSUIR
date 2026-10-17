from __future__ import annotations

import numpy as np


def projection_weights(X: np.ndarray, delta: float = 0.0) -> np.ndarray:
    Q = X.shape[0]
    G = X @ X.T
    if delta > 0.0:
        A = G + delta * np.eye(Q)
        W = X.T @ np.linalg.solve(A, X)
    else:
        W = X.T @ np.linalg.pinv(G) @ X
    return 0.5 * (W + W.T)
