# pages/3_Colusion.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(layout="wide")
st.title("Colusión (gatillo) desde Cournot — simple")

# ------------------ Helpers ------------------
def cournot_asym(a, b, cs_arr):
    N = len(cs_arr)
    S = cs_arr.sum()
    # Fórmula correcta: q_i^N = (a - (N+1)c_i + S) / ((N+1)b)
    qN = (a - (N+1)*cs_arr + S) / ((N+1)*b)
    qN = np.maximum(qN, 0.0)  # respaldo esquinas
    QN = qN.sum()
    PN = a - b*QN
    piN = np.maximum(PN - cs_arr, 0.0) * qN
    return qN, QN, PN, piN

def cartel_equal_split(a, b, cs_arr):
    N = len(cs_arr)
    S = cs_arr.sum()
    cbar = S / N
    QC = max((a - cbar) / (2*b), 0.0)
    PC = a - b*QC
    qC = np.array([QC / N] * N)
    piC = np.maximum(PC - cs_arr, 0.0) * qC
    return qC, QC, PC, piC

def one_shot_deviation_against_cartel(a, b, cs_arr, QC, N):
    Q_others_C = QC * (N - 1) / N
    qD = np.maximum((a - cs_arr - b * Q_others_C) / (2*b), 0.0)
    PD = a - b * (qD + Q_others_C)
    piD = np.maximum(PD - cs_arr, 0.0) * qD
    return qD, PD, piD

def deltas_robust(piN, piC, piD):
    den = (piD - piN)  # π^D - π^N
    num = (piD - piC)  # π^D - π^C
    delta_i = np.zeros_like(den)
    eps = 1e-12
    mask_pos = den > eps
    delta_i[mask_pos] = np.clip(num[mask_pos] / den[mask_pos], 0.0, 1.0)
    mask_nonpos = ~mask_pos
    delta_i[mask_nonpos & (num <= 0)] = 0.0
    delta_i[mask_nonpos & (num > 0)] = 1.0
    delta_star = float(np.max(delta_i)) if len(delta_i) > 0 else 1.0
    binder_idx = int(np.argmax(delta_i)) if len(delta_i) > 0 else 0
    return delta_i, delta_star, binder_idx

def cs_linear(a, b, Q, P):
    # Con demanda P(Q)=a-bQ: CS = 0.5 * Q * (a - P)
    return 0.5 * Q * (a - P)

# ------------------ Sidebar ------------------
with st.sidebar:
    st.header("Casos (presets)")
    # Claves para inputs
    if "a" not in st.session_state: st.session_state.a = 100.0
    if "b" not in st.session_state: st.session_state.b = 1.0
    if "N" not in st.session_state: st.session_state.N = 2
    # UNA clave por costo
    def ensure_cost_keys(N):
        for i in range(N):
            key = f"c{i+1}"
            if key not in st.session_state:
                st.session_state[key] = 20.0

    ensure_cost_keys(st.session_state.N)

    preset = st.selectbox(
        "Selecciona un caso",
        ["(Ninguno)", "Caso A: Simétrico", "Caso B: Disruptor eficiente",
         "Caso C: N=3 simétrico", "Caso D: Demanda más inelástica"],
        index=0
    )

    # Aplicar preset
    if preset != "(Ninguno)":
        if preset == "Caso A: Simétrico":
            st.session_state.a = 100.0; st.session_state.b = 1.0; st.session_state.N = 2
            ensure_cost_keys(2)
            st.session_state.c1 = 20.0; st.session_state.c2 = 20.0
        elif preset == "Caso B: Disruptor eficiente":
            st.session_state.a = 100.0; st.session_state.b = 1.0; st.session_state.N = 2
            ensure_cost_keys(2)
            st.session_state.c1 = 15.0; st.session_state.c2 = 25.0
        elif preset == "Caso C: N=3 simétrico":
            st.session_state.a = 100.0; st.session_state.b = 1.0; st.session_state.N = 3
            ensure_cost_keys(3)
            st.session_state.c1 = 20.0; st.session_state.c2 = 20.0; st.session_state.c3 = 20.0
        elif preset == "Caso D: Demanda más inelástica":
            st.session_state.a = 100.0; st.session_state.b = 2.0; st.session_state.N = 2
            ensure_cost_keys(2)
            st.session_state.c1 = 20.0; st.session_state.c2 = 20.0

    st.header("Demanda")
    a = st.number_input("Intercepto a", value=float(st.session_state.a), step=1.0, min_value=0.0, format="%.2f", key="a")
    b = st.number_input("Pendiente b (>0)", value=float(st.session_state.b), step=0.1, min_value=0.0001, format="%.4f", key="b")

    st.header("Mercado")
    N = st.number_input("Número de firmas N", value=int(st.session_state.N), min_value=2, max_value=20, step=1, key="N")
    st.subheader("Costos marginales por firma")
    cs = []
    for i in range(int(N)):
        key = f"c{i+1}"
        default_c = st.session_state.get(key, 20.0)
        ci = st.number_input(f"c{i+1}", value=float(default_c), step=1.0, min_value=0.0, format="%.2f", key=key)
        cs.append(ci)

    st.divider()
    st.subheader("Chequeo de sostenibilidad")
    delta_user = st.slider("δ (factor de descuento)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

# ------------------ Cálculos principales ------------------
cs_arr = np.array(cs, dtype=float)
qN, QN, PN, piN = cournot_asym(a, b, cs_arr)
qC, QC, PC, piC = cartel_equal_split(a, b, cs_arr)
qD, PD, piD = one_shot_deviation_against_cartel(a, b, cs_arr, QC, int(N))
delta_i, delta_star, binder_idx = deltas_robust(piN, piC, piD)

# Sostenibilidad con δ del usuario (grim: δ ≥ δ*)
sostenible = (delta_user + 1e-12) >= delta_star

# Welfare simple
CS_N = cs_linear(a, b, QN, PN)
PS_N = float(np.sum(piN))
W_N  = CS_N + PS_N

CS_C = cs_linear(a, b, QC, PC)
PS_C = float(np.sum(piC))
W_C  = CS_C + PS_C

# ------------------ UI: métricas ------------------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("δ* (umbral cartel)", f"{delta_star:.2f}")
c2.metric("Qᴺ", f"{QN:.2f}")
c3.metric("Pᴺ", f"{PN:.2f}")
c4.metric("Qᶜ", f"{QC:.2f}")
c5.metric("¿Sostenible con δ?", "Sí ✅" if sostenible else "No ❌", help="Regla: la colusión con grim se sostiene si δ ≥ δ*.")

st.caption("Castigo = Cournot para siempre. δ_i* = (π_i^D − π_i^C) / (π_i^D − π_i^N), con manejo robusto de bordes.")
st.write(f"**Firma que ata δ***: i={binder_idx+1}")

# ------------------ Tabla por firma ------------------
df = pd.DataFrame({
    "Firma": [f"i={i+1}" for i in range(int(N))],
    "c_i": np.round(cs_arr, 2),
    "q_i^N": np.round(qN, 2),
    "π_i^N": np.round(piN, 2),
    "q_i^C": np.round(qC, 2),
    "π_i^C": np.round(piC, 2),
    "q_i^D": np.round(qD, 2),
    "π_i^D": np.round(piD, 2),
    "δ_i*": np.round(delta_i, 2),
})
st.dataframe(df, use_container_width=True)

# ------------------ Gráficos ------------------
g1, g2 = st.columns(2)
with g1:
    fig1, ax1 = plt.subplots()
    ax1.bar(np.arange(1, int(N)+1), delta_i)
    ax1.set_xlabel("Firma i"); ax1.set_ylabel("δ_i*"); ax1.set_ylim(0, 1)
    ax1.set_title("Umbrales individuales δ_i*")
    st.pyplot(fig1)

with g2:
    width = 0.35
    idx = np.arange(1, int(N)+1)
    fig2, ax2 = plt.subplots()
    ax2.bar(idx - width/2, piN, width, label="π_i^N")
    ax2.bar(idx + width/2, piC, width, label="π_i^C")
    ax2.set_xlabel("Firma i"); ax2.set_ylabel("Utilidad")
    ax2.set_title("Utilidades: Cournot vs Cartel")
    ax2.legend()
    st.pyplot(fig2)

st.divider()
st.subheader("Bienestar (comparativo)")
cW1, cW2, cW3 = st.columns(3)
cW1.metric("CS Cournot", f"{CS_N:.2f}")
cW2.metric("PS Cournot (∑π)", f"{PS_N:.2f}")
cW3.metric("W Cournot", f"{W_N:.2f}")
cW1, cW2, cW3 = st.columns(3)
cW1.metric("CS Cartel", f"{CS_C:.2f}")
cW2.metric("PS Cartel (∑π)", f"{PS_C:.2f}")
cW3.metric("W Cartel", f"{W_C:.2f}")

# ------------------ Mini–experimento: δ* vs N (simétrico) ------------------
st.divider()
with st.expander("Mini–experimento (simétrico): δ* vs N", expanded=False):
    cex1, cex2, cex3, cex4 = st.columns(4)
    a_exp = cex1.number_input("a (exp)", value=float(a), step=1.0, min_value=0.0, format="%.2f")
    b_exp = cex2.number_input("b (exp)", value=float(b), step=0.1, min_value=0.0001, format="%.4f")
    c_exp = cex3.number_input("c común (exp)", value=20.0, step=1.0, min_value=0.0, format="%.2f")
    N_min = cex4.number_input("N min", value=2, min_value=2, max_value=20, step=1)
    N_max = cex4.number_input("N max", value=6, min_value=int(N_min), max_value=20, step=1)

    Ns = list(range(int(N_min), int(N_max)+1))
    deltas = []
    for NN in Ns:
        cs_sym = np.full(NN, c_exp, dtype=float)
        qN_e, QN_e, PN_e, piN_e = cournot_asym(a_exp, b_exp, cs_sym)
        qC_e, QC_e, PC_e, piC_e = cartel_equal_split(a_exp, b_exp, cs_sym)
        qD_e, PD_e, piD_e = one_shot_deviation_against_cartel(a_exp, b_exp, cs_sym, QC_e, NN)
        di_e, dstar_e, _ = deltas_robust(piN_e, piC_e, piD_e)
        deltas.append(dstar_e)

    df_exp = pd.DataFrame({"N": Ns, "δ*": np.round(deltas, 4)})
    st.dataframe(df_exp, use_container_width=True)
    fig_exp, ax_exp = plt.subplots()
    ax_exp.plot(Ns, deltas, marker="o")
    ax_exp.set_xlabel("N"); ax_exp.set_ylabel("δ*"); ax_exp.set_ylim(0, 1)
    ax_exp.set_title("δ* vs N (simétrico)")
    st.pyplot(fig_exp)
