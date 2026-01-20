import numpy as np
import pandas as pd
import streamlit as st
from src.ahp import sanitize_reciprocal

def matrix_editor_upper(labels, A_current: np.ndarray, key: str, help_text: str):
    n = len(labels)
    A_current = sanitize_reciprocal(A_current)

    inp = np.full((n, n), np.nan, dtype=float)
    for i in range(n):
        inp[i, i] = 1.0
    for i in range(n):
        for j in range(i + 1, n):
            inp[i, j] = A_current[i, j]

    df_in = pd.DataFrame(inp, index=labels, columns=labels)
    st.info(help_text)

    df_out = st.data_editor(
        df_in,
        use_container_width=True,
        key=key,
        num_rows="fixed"
    )

    A_new = np.ones((n, n), dtype=float)
    for i in range(n):
        A_new[i, i] = 1.0
    for i in range(n):
        for j in range(i + 1, n):
            v = df_out.iloc[i, j]
            if pd.isna(v):
                v = A_current[i, j]
            try:
                v = float(v)
            except Exception:
                v = A_current[i, j]
            if not np.isfinite(v) or v <= 0:
                v = 1.0
            A_new[i, j] = v
            A_new[j, i] = 1.0 / v

    return sanitize_reciprocal(A_new)
