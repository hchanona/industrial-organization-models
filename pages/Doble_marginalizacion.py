# pages/Doble_Marginalizacion.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(layout="wide")
st.title("Doble marginalización — simulador (U–D con N minoristas)")

st.markdown(
    "[Consulta el código Python de esta página]"
    "(https://github.com/hchanona/industrial-organization-models/edit/main/pages/Doble_marginalizacion.py)"
)

# ========================= Helpers =========================
def _round2(x):
    return float(f"{x:.2f}")

def demand_price(a, b, Q):
    return a - b*Q

def cs_linear(a, b, P, Q):
    # Con P(Q)=a-bQ: CS = 0.5 * Q * (a - P)
    return 0.5 * Q * (a - P)

def regime_vi(a, b, cU, cD):
    # Integración vertical = monopolio con costo marginal cU + cD
    c = cU + cD
    p = (a + c)/2.0
    Q = (a - p)/b            # = (a - c)/(2b)
    P = p
    pi = (p - c)*Q
    CS = cs_linear(a, b, P, Q)
    PS = pi
    W = CS + PS
    return {
        "regimen": "VI",
        "N": 1,
        "w": None,
        "p": _round2(p), "P": _round2(P), "Q": _round2(Q),
        "pi_U": None, "pi_D": None, "pi_total": _round2(pi),
        "CS": _round2(CS), "PS": _round2(PS), "W": _round2(W)
    }

def dm_opt_w(a, b, cU, cD):
    # Óptimo de U con 1 minorista: 2w = a - cD + cU  => w* = (a - cD + cU)/2
    return (a - cD + cU)/2.0

def retailer_price_given_w(a, w, cD):
    # Minorista fija p sobre costo (w + cD): p = (a + w + cD)/2
    return (a + w + cD)/2.0

def dm_duopolio_p(a, b, cU, cD):
    # Caso N=1 (1 minorista): precio explícito p
    w = dm_opt_w(a, b, cU, cD)
    p = retailer_price_given_w(a, w, cD)
    Q = (a - p)/b
    P = p
    pi_D = (p - (w + cD)) * Q
    pi_U = (w - cU) * Q
    CS = cs_linear(a, b, P, Q)
    PS = pi_U + pi_D
    W = CS + PS
    return {
        "regimen": "DM",
        "N": 1,
        "w": _round2(w),
        "p": _round2(p), "P": _round2(P), "Q": _round2(Q),
        "pi_U": _round2(pi_U), "pi_D": _round2(pi_D), "pi_total": _round2(PS),
        "CS": _round2(CS), "PS": _round2(PS), "W": _round2(W)
    }

def dm_outcomes(a, b, cU, cD, N):
    # DM con N minoristas simétricos (Cournot abajo).
    # U elige w*; cada minorista compite en cantidades con costo marginal c_eff = w + cD
    w = dm_opt_w(a, b, cU, cD)
    c_eff = w + cD
    # Cournot con N firmas y demanda P=a-bQ: Q = N*(a - c_eff)/(b*(N+1))
    Q = N * (a - c_eff) / (b * (N + 1))
    P = demand_price(a, b, Q)
    margin_D = P - c_eff
    pi_D_total = margin_D * Q           # suma de minoristas
    pi_U = (w - cU) * Q
    CS = cs_linear(a, b, P, Q)
    PS = pi_U + pi_D_total
    W = CS + PS
    return {
        "regimen": "DM",
        "N": int(N),
        "w": _round2(w),
        "p": None, "P": _round2(P), "Q": _round2(Q),
        "pi_U": _round2(pi_U), "pi_D": _round2(pi_D_total), "pi_total": _round2(PS),
        "CS": _round2(CS), "PS": _round2(PS), "W": _round2(W)
    }

def regime_tpt(a, b, cU, cD, F=0.0):
    # Tarifa en dos partes: w = cU; reproduce VI en p y Q. F redistribuye rentas.
    vi = regime_vi(a, b, cU, cD)
    pi_total = vi["pi_total"]
    pi_U = F
    pi_D = pi_total - F
    out = dict(vi)
    out.update({
        "regimen": "TPT",
        "w": _round2(cU), "pi_U": _round2(pi_U), "pi_D": _round2(pi_D)
    })
    return out

def compare_regimes(a, b, cU, cD, N, F):
    dm = dm_duopolio_p(a, b, cU, cD) if N == 1 else dm_outcomes(a, b, cU, cD, N)
    vi = regime_vi(a, b, cU, cD)
    tpt = regime_tpt(a, b, cU, cD, F)
    return dm, vi, tpt

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
    cU = st.number_input("Costo marginal upstream c_U", value=10.0, step=1.0, min_value=0.0, format="%.2f")
    cD = st.number_input("Costo marginal downstream c_D", value=10.0, step=1.0, min_value=0.0, format="%.2f")
    N = st.number_input("Número de minoristas N", value=1, min_value=1, max_value=30, step=1)
    st.subheader("Tarifa en dos partes (opcional)")
    F = st.number_input("Cuota fija F (solo redistribuye rentas en TPT)", value=0.0, step=10.0, min_value=0.0, format="%.2f")

# ========================= Cálculo base =========================
dm, vi, tpt = compare_regimes(a, b, cU, cD, int(N), F)

# ========================= UI principal =========================
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("P (DM)", f"{dm['P']:.2f}")
c2.metric("Q (DM)", f"{dm['Q']:.2f}")
c3.metric("W (DM)", f"{dm['W']:.2f}")
c4.metric("P (VI/TPT)", f"{vi['P']:.2f}")
c5.metric("Q (VI/TPT)", f"{vi['Q']:.2f}")
c6.metric("∆W (DM−VI)", f"{(dm['W'] - vi['W']):.2f}")

st.caption("En TPT con w=c_U se recupera el nivel de VI (misma P y Q). F sólo redistribuye π entre U y D.")

# Tabla resumen por régimen
def row_from(d):
    return {
        "Régimen": d["regimen"],
        "N": d["N"] if "N" in d and d["N"] is not None else 1,
        "w*": d["w"] if d.get("w") is not None else np.nan,
        "p (si N=1)": d["p"] if d.get("p") is not None else np.nan,
        "P": d["P"], "Q": d["Q"],
        "π_U": d["pi_U"] if d.get("pi_U") is not None else np.nan,
        "π_D (∑ si N>1)": d["pi_D"] if d.get("pi_D") is not None else np.nan,
        "π_total": d["pi_total"],
        "CS": d["CS"], "PS": d["PS"], "W": d["W"]
    }

df = pd.DataFrame([row_from(dm), row_from(vi), row_from(tpt)])
st.dataframe(df, use_container_width=True)

# Gráfico único: Bienestar por régimen
figW, axW = plt.subplots()
vals = [dm["W"], vi["W"], tpt["W"]]
labs = ["DM", "VI", "TPT"]
axW.bar(labs, vals)
axW.set_ylabel("W")
axW.set_title("Bienestar por régimen")
st.pyplot(figW)

# ========================= Snapshots para la PPT =========================
st.divider()
st.subheader("Capturas de escenario (para tu PPT)")
if "dm_snapshots" not in st.session_state:
    st.session_state.dm_snapshots = []

colS1, colS2 = st.columns([2,1])
with colS1:
    snap_name = st.text_input("Nombre corto del escenario (ej. 'Base', 'b=1.8', 'N=3, asim')", value="")
with colS2:
    if st.button("Guardar captura actual", use_container_width=True):
        if snap_name.strip():
            st.session_state.dm_snapshots.append({
                "escenario": snap_name.strip(),
                "a": _round2(a), "b": _round2(b), "N": int(N),
                "cU": _round2(cU), "cD": _round2(cD), "F": _round2(F),
                "P_DM": dm["P"], "Q_DM": dm["Q"], "W_DM": dm["W"],
                "P_VI": vi["P"], "Q_VI": vi["Q"], "W_VI": vi["W"],
                "∆W(DM−VI)": _round2(dm["W"] - vi["W"]),
                "w*": dm["w"] if dm.get("w") is not None else None,
                "p_DM (N=1)": dm["p"] if dm.get("p") is not None else None
            })
            if len(st.session_state.dm_snapshots) > 10:
                st.session_state.dm_snapshots = st.session_state.dm_snapshots[-10:]
        else:
            st.warning("Ponle un nombre a la captura antes de guardar.")

if st.session_state.dm_snapshots:
    df_snaps = pd.DataFrame(st.session_state.dm_snapshots)
    st.dataframe(df_snaps, use_container_width=True)
    if st.button("Borrar última captura"):
        st.session_state.dm_snapshots = st.session_state.dm_snapshots[:-1]

# ========================= Barridos personalizados =========================
st.divider()
st.subheader("Barridos personalizados (elige tus propios valores)")

# ----- Barrido de c_U -----
with st.expander("Barrido de c_U (lista de valores)", expanded=False):
    colU1, colU2 = st.columns([3,1])
    with colU1:
        cU_values_txt = st.text_input("Valores de c_U (ej. 5,10,15,20)", value="", key="cU_vals")
    with colU2:
        run_cU = st.button("Ejecutar barrido c_U", use_container_width=True, key="btn_cU")
    if run_cU:
        vals = parse_list_floats(cU_values_txt)
        rows = []
        for v in vals:
            dm_v, vi_v, _ = compare_regimes(a, b, v, cD, int(N), F)
            rows.append({
                "c_U": _round2(v),
                "P_DM": dm_v["P"], "Q_DM": dm_v["Q"], "W_DM": dm_v["W"],
                "P_VI": vi_v["P"], "Q_VI": vi_v["Q"], "W_VI": vi_v["W"],
                "∆W(DM−VI)": _round2(dm_v["W"] - vi_v["W"])
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ----- Barrido de c_D -----
with st.expander("Barrido de c_D (lista de valores)", expanded=False):
    colD1, colD2 = st.columns([3,1])
    with colD1:
        cD_values_txt = st.text_input("Valores de c_D (ej. 5,10,15,20)", value="", key="cD_vals")
    with colD2:
        run_cD = st.button("Ejecutar barrido c_D", use_container_width=True, key="btn_cD")
    if run_cD:
        vals = parse_list_floats(cD_values_txt)
        rows = []
        for v in vals:
            dm_v, vi_v, _ = compare_regimes(a, b, cU, v, int(N), F)
            rows.append({
                "c_D": _round2(v),
                "P_DM": dm_v["P"], "Q_DM": dm_v["Q"], "W_DM": dm_v["W"],
                "P_VI": vi_v["P"], "Q_VI": vi_v["Q"], "W_VI": vi_v["W"],
                "∆W(DM−VI)": _round2(dm_v["W"] - vi_v["W"])
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ----- Barrido de b (elasticidad) -----
with st.expander("Barrido de elasticidad (lista de b)", expanded=False):
    colB1, colB2 = st.columns([3,1])
    with colB1:
        b_values_txt = st.text_input("Valores de b (ej. 0.6,1.0,1.8)", value="", key="b_vals_dm")
    with colB2:
        run_b = st.button("Ejecutar barrido b", use_container_width=True, key="btn_b_dm")
    if run_b:
        vals = parse_list_floats(b_values_txt)
        rows = []
        for v in vals:
            dm_v, vi_v, _ = compare_regimes(a, v, cU, cD, int(N), F)
            rows.append({
                "b": _round2(v),
                "P_DM": dm_v["P"], "Q_DM": dm_v["Q"], "W_DM": dm_v["W"],
                "P_VI": vi_v["P"], "Q_VI": vi_v["Q"], "W_VI": vi_v["W"],
                "∆W(DM−VI)": _round2(dm_v["W"] - vi_v["W"])
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ----- Barrido de N (entrada minorista) -----
with st.expander("Barrido de N (lista de valores)", expanded=False):
    colN1, colN2 = st.columns([3,1])
    with colN1:
        N_values_txt = st.text_input("Valores de N (ej. 1,2,3,5)", value="", key="N_vals_dm")
    with colN2:
        run_N = st.button("Ejecutar barrido N", use_container_width=True, key="btn_N_dm")
    if run_N:
        Ns = parse_list_ints(N_values_txt)
        rows = []
        for NN in Ns:
            NN = int(NN)
            dm_v, vi_v, _ = compare_regimes(a, b, cU, cD, NN, F)
            rows.append({
                "N": int(NN),
                "P_DM": dm_v["P"], "Q_DM": dm_v["Q"], "W_DM": dm_v["W"],
                "P_VI": vi_v["P"], "Q_VI": vi_v["Q"], "W_VI": vi_v["W"],
                "∆W(DM−VI)": _round2(dm_v["W"] - vi_v["W"])
            })
        if rows:
            dfN = pd.DataFrame(rows)
            st.dataframe(dfN, use_container_width=True)
            # pequeña gráfica lineal de Q_DM vs N
            figN, axN = plt.subplots()
            axN.plot(dfN["N"], dfN["Q_DM"], marker="o")
            axN.set_xlabel("N"); axN.set_ylabel("Q bajo DM")
            axN.set_title("Q (DM) vs N")
            st.pyplot(figN)

# ========================= Notas =========================
st.caption("Notas: (i) Bajo TPT con w=c_U se elimina la distorsión de DM y se recupera VI en P y Q. (ii) Con N minoristas en Cournot, la DM se atenúa al aumentar N.")

