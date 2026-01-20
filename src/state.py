import numpy as np
import streamlit as st
from src.config import DEFAULT_CRITERIA, DEFAULT_ALTS, DEFAULT_SCENARIOS
from src.ahp import sanitize_reciprocal

def build_empty_scenario():
    return {
        "crit_matrix": np.ones((len(DEFAULT_CRITERIA), len(DEFAULT_CRITERIA)), dtype=float),
        "alt_matrices": {c: np.ones((len(DEFAULT_ALTS), len(DEFAULT_ALTS)), dtype=float) for c in DEFAULT_CRITERIA}
    }

def normalize_scenario_sizes(name: str):
    criteria = st.session_state.criteria
    alts = st.session_state.alts
    scen = st.session_state.scenarios[name]

    n = len(criteria)
    A = np.array(scen.get("crit_matrix", np.ones((n, n))), dtype=float)
    if A.shape != (n, n):
        A = np.ones((n, n), dtype=float)
    scen["crit_matrix"] = sanitize_reciprocal(A)

    m = len(alts)
    alt_mats = scen.get("alt_matrices", {})
    fixed = {}
    for c in criteria:
        A2 = np.array(alt_mats.get(c, np.ones((m, m))), dtype=float)
        if A2.shape != (m, m):
            A2 = np.ones((m, m), dtype=float)
        fixed[c] = sanitize_reciprocal(A2)

    scen["alt_matrices"] = fixed
    st.session_state.scenarios[name] = scen

def reset_scenario(name: str):
    n = len(st.session_state.criteria)
    m = len(st.session_state.alts)
    st.session_state.scenarios[name] = {
        "crit_matrix": np.ones((n, n), dtype=float),
        "alt_matrices": {c: np.ones((m, m), dtype=float) for c in st.session_state.criteria}
    }

def ensure_state():
    if "criteria" not in st.session_state:
        st.session_state.criteria = DEFAULT_CRITERIA.copy()
    if "alts" not in st.session_state:
        st.session_state.alts = DEFAULT_ALTS.copy()
    if "scenarios" not in st.session_state:
        st.session_state.scenarios = {s: build_empty_scenario() for s in DEFAULT_SCENARIOS}
    if "active_scenario" not in st.session_state:
        st.session_state.active_scenario = DEFAULT_SCENARIOS[0]

    if st.session_state.active_scenario not in st.session_state.scenarios:
        st.session_state.active_scenario = list(st.session_state.scenarios.keys())[0]

    for s in st.session_state.scenarios:
        normalize_scenario_sizes(s)

def add_scenario():
    names = list(st.session_state.scenarios.keys())
    new_name = f"Scenario {len(names)+1}"
    st.session_state.scenarios[new_name] = build_empty_scenario()
    normalize_scenario_sizes(new_name)
    st.session_state.active_scenario = new_name

def delete_active_scenario():
    del st.session_state.scenarios[st.session_state.active_scenario]
    st.session_state.active_scenario = list(st.session_state.scenarios.keys())[0]

def copy_active_scenario():
    src = st.session_state.active_scenario
    dst = f"{src} (Copy)"
    s = st.session_state.scenarios[src]
    st.session_state.scenarios[dst] = {
        "crit_matrix": np.array(s["crit_matrix"], dtype=float).copy(),
        "alt_matrices": {k: np.array(v, dtype=float).copy() for k, v in s["alt_matrices"].items()}
    }
    st.session_state.active_scenario = dst

def reset_active_scenario():
    reset_scenario(st.session_state.active_scenario)
