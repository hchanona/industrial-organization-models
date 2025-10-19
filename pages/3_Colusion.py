# pages/3_Colusion.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(layout="wide")
st.title("Colusión (grim) desde Cournot — simulador sin presets")

# ========================= Helpers =========================
def cournot_asym(a, b, cs_arr):
    N = len(cs_arr)
    S = cs_arr.sum()
    # Fórmula correcta: q_i^N = (a - (N+1)c_i + S) / ((N+1)b)
    qN = (a - (N+1)*cs_arr + S) / ((N+1)*b)
    qN = np.maximum(qN, 0.0)
    QN = qN.sum()
    PN = a - b*QN
    piN = np.maximum(PN - cs_arr, 0.0) * qN
    return qN, QN, PN, piN

def cartel_equal_split(a, b, cs_arr):
    N = len(cs_arr)
    cbar = cs_arr.mean()
    QC = max((a - cbar) / (2*b), 0.0)
    PC = a - b*QC
    qC = np.array([QC / N] * N)
    piC = np.maximum(PC - cs_arr, 0.0) * qC
    return qC, QC, PC, piC

def one_shot_deviation_against_cartel(a, b, cs_arr, QC):
    N = len(cs_arr)
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
    # Con P(Q)=a-bQ: CS = 0.5 * Q * (a - P)
    return 0.5 * Q * (a - P)

def parse_list_floats(txt):
    if not txt.strip():
        return []
    return [float(x.strip()) for x in txt.split(",") if x.strip()]

def parse_list_ints(txt):
    if not txt.strip():
        return []
    return [int(float(x.strip())) for x in txt.split(",") if x.strip()]

# ========================= Sidebar =========================
with st.sidebar:
    st.header("Parámetros (ajústalos libremente)")
    a = st.number_input("Intercepto a", value=100.0, step=1.0, min_value=0.0, format="%.2f")
    b = st.number_input("Pendiente b (>0)", value=1.0, step=0.1, min_value=0.0001, format="%.4f")
    N = st.number_input("Número de firmas N", value=2, min_value=2, max_value=20, step=1)

    st.subheader("Costos marginales por firma")
    cs = []
    # todos parten en 20.0; el/la estudiante los mueve
    for i in range(int(N)):
        cs.append(st.number_input(f"c{i+1}", value=20.0, step=1.0, min_value=0.0, format="%.2f", key=f"c{i+1}"))

    st.divider()
    st.subheader("Chequeo de sostenibilidad")
    delta_user = st.slider("δ (factor de descuento)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

# ========================= Cálculo base =========================
cs_arr = np.array(cs, dtype=float)
qN, QN, PN, piN = cournot_asym(a, b, cs_arr)
qC, QC, PC, piC = cartel_equal_split(a, b, cs_arr)
qD, PD, piD = one_shot_deviation_against_cartel(a, b, cs_arr, QC)
delta_i, delta_star, binder_idx = deltas_robust(piN, piC, piD)

sostenible = (delta_user + 1e-12) >= delta_star

# Welfare
CS_N = cs_linear(a, b, QN, PN); PS_N = float(np.sum(piN)); W_N = CS_N + PS_N
CS_C = cs_linear(a, b, QC, PC); PS_C = float(np.sum(piC)); W_C = CS_C + PS_C

# ========================= UI principal =========================
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("δ* (umbral cartel)", f"{delta_star:.2f}")
c2.metric("Qᴺ", f"{QN:.2f}")
c3.metric("Pᴺ", f"{PN:.2f}")
c4.metric("Qᶜ", f"{QC:.2f}")
c5.metric("¿Sostenible con δ?", "Sí ✅" if sostenible else "No ❌", help="Se sostiene si δ ≥ δ* (castigo grim).")

st.caption(r"Fórmula: $\delta_i^* = \frac{\pi_i^D - \pi_i^C}{\pi_i^D - \pi_i^N}$, con manejo robusto de bordes.")
st.write(f"**Firma que fija δ***: i={binder_idx+1}")

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

# ========================= Snapshots para la PPT =========================
st.divider()
st.subheader("Capturas de escenario (para tu PPT)")
if "snapshots" not in st.session_state:
    st.session_state.snapshots = []

colS1, colS2 = st.columns([2,1])
with colS1:
    snap_name = st.text_input("Nombre corto del escenario (ej. 'Base', 'b=1.8', 'N=3, asim')", value="")
with colS2:
    if st.button("Guardar captura actual", use_container_width=True):
        if snap_name.strip():
            st.session_state.snapshots.append({
                "escenario": snap_name.strip(),
                "a": round(a,2), "b": round(b,2), "N": int(N),
                "c": ", ".join([f"{x:.2f}" for x in cs_arr]),
                "QN": round(QN,2), "PN": round(PN,2), "QC": round(QC,2),
                "delta*": round(delta_star,2), "binder": int(binder_idx+1),
                "CS_N": round(CS_N,2), "PS_N": round(PS_N,2), "W_N": round(W_N,2),
                "CS_C": round(CS_C,2), "PS_C": round(PS_C,2), "W_C": round(W_C,2),
            })
            # límite suave para no crecer infinito
            if len(st.session_state.snapshots) > 10:
                st.session_state.snapshots = st.session_state.snapshots[-10:]
        else:
            st.warning("Ponle un nombre a la captura antes de guardar.")

if st.session_state.snapshots:
    df_snaps = pd.DataFrame(st.session_state.snapshots)
    st.dataframe(df_snaps, use_container_width=True)
    if st.button("Borrar última captura"):
        st.session_state.snapshots = st.session_state.snapshots[:-1]

# ========================= Barridos personalizados (sin escenarios fijos) =========================
st.divider()
st.subheader("Barridos personalizados (elige tus propios valores)")

# ----- Barrido de costos (elige una firma y valores de c_i) -----
with st.expander("Barrido de costos (elige firma y lista de valores)", expanded=False):
    colC1, colC2, colC3 = st.columns([1,2,1])
    with colC1:
        i_firma = st.number_input("Firma a barrer (i)", min_value=1, max_value=int(N), value=1, step=1)
    with colC2:
        c_values_txt = st.text_input("Valores de costo para esa firma (coma-separados, p. ej. 15,18,20,22)", value="")
    with colC3:
        run_cost_sweep = st.button("Ejecutar barrido de costos", use_container_width=True, key="btn_costsweep")
    if run_cost_sweep:
        vals = parse_list_floats(c_values_txt)
        rows = []
        for v in vals:
            cs_tmp = cs_arr.copy()
            cs_tmp[int(i_firma)-1] = v
            qN_e, QN_e, PN_e, piN_e = cournot_asym(a, b, cs_tmp)
            qC_e, QC_e, PC_e, piC_e = cartel_equal_split(a, b, cs_tmp)
            qD_e, PD_e, piD_e = one_shot_deviation_against_cartel(a, b, cs_tmp, QC_e)
            _, dstar_e, bind_e = deltas_robust(piN_e, piC_e, piD_e)
            rows.append({
                "c_i": round(v,2),
                "δ*": round(dstar_e,2),
                "binder": int(bind_e+1)
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ----- Barrido de elasticidad (lista de b) -----
with st.expander("Barrido de elasticidad (lista de b)", expanded=False):
    colB1, colB2 = st.columns([3,1])
    with colB1:
        b_values_txt = st.text_input("Valores de b (coma-separados, p. ej. 0.6,1.0,1.8)", value="", key="bvals")
    with colB2:
        run_b_sweep = st.button("Ejecutar barrido de b", use_container_width=True, key="btn_bsweep")
    if run_b_sweep:
        b_vals = parse_list_floats(b_values_txt)
        rows = []
        for b_v in b_vals:
            qN_e, QN_e, PN_e, piN_e = cournot_asym(a, b_v, cs_arr)
            qC_e, QC_e, PC_e, piC_e = cartel_equal_split(a, b_v, cs_arr)
            qD_e, PD_e, piD_e = one_shot_deviation_against_cartel(a, b_v, cs_arr, QC_e)
            _, dstar_e, bind_e = deltas_robust(piN_e, piC_e, piD_e)
            rows.append({
                "b": round(b_v,2),
                "Q^N": round(QN_e,2),
                "P^N": round(PN_e,2),
                "δ*": round(dstar_e,2),
                "binder": int(bind_e+1)
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ----- Barrido de entrada (lista de N) -----
with st.expander("Barrido de entrada (lista de N)", expanded=False):
    colN1, colN2, colN3 = st.columns([2,2,1])
    with colN1:
        N_values_txt = st.text_input("Valores de N (coma-separados, p. ej. 2,3,4)", value="", key="Nvals")
    with colN2:
        c_new = st.number_input("c para firmas adicionales (si N supera el actual)", value=float(cs_arr.mean()), step=1.0, min_value=0.0, format="%.2f")
    with colN3:
        run_N_sweep = st.button("Ejecutar barrido de N", use_container_width=True, key="btn_Nsweep")
    if run_N_sweep:
        Ns = parse_list_ints(N_values_txt)
        rows = []
        for NN in Ns:
            if NN <= len(cs_arr):
                cs_tmp = cs_arr[:NN].copy()
            else:
                extra = np.full(NN - len(cs_arr), c_new, dtype=float)
                cs_tmp = np.concatenate([cs_arr, extra])
            qN_e, QN_e, PN_e, piN_e = cournot_asym(a, b, cs_tmp)
            qC_e, QC_e, PC_e, piC_e = cartel_equal_split(a, b, cs_tmp)
            qD_e, PD_e, piD_e = one_shot_deviation_against_cartel(a, b, cs_tmp, QC_e)
            _, dstar_e, bind_e = deltas_robust(piN_e, piC_e, piD_e)
            rows.append({
                "N": int(NN),
                "δ*": round(dstar_e,2),
                "binder": int(bind_e+1)
            })
        if rows:
            dfN = pd.DataFrame(rows)
            st.dataframe(dfN, use_container_width=True)
            # pequeña gráfica opcional
            try:
                figN, axN = plt.subplots()
                axN.plot(dfN["N"], dfN["δ*"], marker="o")
                axN.set_xlabel("N"); axN.set_ylabel("δ*"); axN.set_ylim(0,1)
                axN.set_title("δ* vs N (con tus costos)")
                st.pyplot(figN)
            except Exception:
                pass

# ========================= Notas =========================
st.caption("Nota: el 'cartel simple' reparte Q^C por igual. En costos asimétricos, no es el cartel eficiente; aquí se usa por transparencia pedagógica.")
