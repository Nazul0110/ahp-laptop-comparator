import io, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.config import RI_TABLE

def fmt_pct(x): return f"{x*100:.2f}%"

def ahp_weights(A: np.ndarray) -> np.ndarray:
    col_sum = A.sum(axis=0)
    col_sum[col_sum == 0] = 1e-12
    norm = A / col_sum
    w = norm.mean(axis=1)
    s = w.sum()
    return (w / s) if s != 0 else np.ones(len(w)) / len(w)

def ahp_consistency(A: np.ndarray, w: np.ndarray):
    n = A.shape[0]
    if n <= 2:
        return float(n), 0.0, 0.0
    Aw = A @ w
    with np.errstate(divide="ignore", invalid="ignore"):
        lam = np.where(w != 0, Aw / w, np.nan)
    lambda_max = float(np.nanmean(lam))
    CI = (lambda_max - n) / (n - 1)
    RI = RI_TABLE.get(n, 1.59)
    CR = 0.0 if RI == 0 else (CI / RI)
    return lambda_max, float(CI), float(CR)

def sanitize_reciprocal(A: np.ndarray) -> np.ndarray:
    A = np.array(A, dtype=float)
    n = A.shape[0]
    for i in range(n):
        A[i, i] = 1.0
    for i in range(n):
        for j in range(i + 1, n):
            v = A[i, j]
            if not np.isfinite(v) or v <= 0:
                v = 1.0
            A[i, j] = float(v)
            A[j, i] = 1.0 / float(v)
    return A

def inconsistency_pairs(A: np.ndarray, w: np.ndarray, labels, top_k=8):
    A = np.array(A, dtype=float)
    w = np.array(w, dtype=float)
    n = A.shape[0]
    rows = []
    eps = 1e-12
    for i in range(n):
        for j in range(i + 1, n):
            aij = max(A[i, j], eps)
            ratio = max(w[i] / max(w[j], eps), eps)
            conflict = abs(math.log(aij) - math.log(ratio))
            rows.append((labels[i], labels[j], aij, ratio, conflict))
    rows.sort(key=lambda x: x[-1], reverse=True)
    return pd.DataFrame(rows[:top_k], columns=["Item i", "Item j", "A[i,j]", "w_i/w_j", "Konflik (log-dev)"])

def plot_heatmap(A: np.ndarray, labels, title: str):
    fig = plt.figure()
    ax = plt.gca()
    im = ax.imshow(A, aspect="auto")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    ax.set_title(title)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    return fig

def fig_to_png_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf
