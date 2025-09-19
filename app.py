# app.py
# IO Lab — Cournot (dos firmas, solución interior) con:
# 1) Cruce de mejores respuestas (matplotlib) + bisectriz y regiones q1≶q2
# 2) Demanda inversa con triángulo de excedente del consumidor (matplotlib)
# 3) Dinámica de mejor respuesta (Altair) con trayectoria iterada y slider
#
# Requisitos (requirements.txt):
# streamlit==1.36.0
# numpy==1.26.4
# matplotlib==3.8.4
# pandas==2.2.2
# altair==5.3.0

import numpy as np
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import streamlit as st

# -----------------------------
# Configuración general
# -----------------------------
st.set_page_config(page_title="IO Lab — Cournot", layout="wide")
st.title("IO Lab — Cournot (dos firmas)")

# -----------------------------
# Fórmulas (usa st.latex para que se vean bien)
# -----------------------------
st.markdown("**Modelo:** demanda inversa lineal y costos marginales constantes.")
st.latex(r"P(Q)=a-bQ,\quad Q=q_1+q_2")
st.latex(r"\text{CM}_1=c_1,\quad \text{CM}_2=c_2")
st.markdown("**Equilibrio (interior):**")
st.latex(
    r"""
    q_1^\*=\frac{a-2c_1+c_2}{3b},\qquad
    q_2^\*=\frac{a-2c_2+c_1}{3b},\qquad
    Q^\*=\frac{2a-(c_1+c_2)}{3b},\qquad
    P^\*=a-bQ^\*.
    """
)

# -----------------------------
# Parámetros (sidebar)
# -----------------------------
with st.sidebar:
    st.header("Parámetros")
    a  = st.number_input("Intercepto de demanda a", value=100.0, step=1.0, min_value=0.0, format="%.2f", key="a")
    b  = st.number_input("Pendiente de demanda b (>0)", value=1.0,  step=0.1, min_value=0.0001, format="%.4f", key="b")
    c1 = st.number_input("Costo marginal firma 1 (c1)", value=20.0,   step=1.0, min_value=0.0, format="%.2f", key="c1")
    c2 = st.number_input("Costo marginal firma 2 (c2)", value=30.0,   step=1.0, min_value=0.0, format="%.2f", key="c2")
    st.caption("Ejemplo sugerido (interior): a=100, b=1, c1=20, c2=30.")

# -----------------------------
# Funciones
# -----------------------------
def cournot_interior(a: float, b: float, c1: float, c2: float):
    """Equilibrio interior (no trata esquinas)."""
    q1 = (a - 2*c1 + c2) / (3*b)
    q2 = (a - 2*c2 + c1) / (3*b)
    Q  = q1 + q2
    P  = a - b*Q
    return q1, q2, Q, P

def br1(q2: np.ndarray, a: float, b: float, c1: float):
    """Mejor respuesta 1: q1(q2) = (a - c1 - b q2) / (2b) (interior)."""
    return (a - c1 - b*q2) / (2*b)

def br2(q1: np.ndarray, a: float, b: float, c2: float):
    """Mejor respuesta 2: q2(q1) = (a - c2 - b q1) / (2b) (interior)."""
    return (a - c2 - b*q1) / (2*b)

def cs_linear(a: float, P: float, Q: float):
    """Excedente del consumidor con demanda lineal."""
    if Q <= 0 or P >= a:
        return 0.0
    return 0.5 * (a - P) * Q

# -----------------------------
# Cálculo del equilibrio
# -----------------------------
q1s, q2s, Qs, Ps = cournot_interior(a, b, c1, c2)
CS = cs_linear(a, Ps, Qs)

# -----------------------------
# Tabs principales
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    "Gráficas (matplotlib)",
    "Demanda & EC (matplotlib)",
    "Dinámica (Altair)"
])

# -----------------------------
# (1) Cruce de mejores respuestas + bisectriz y regiones (matplotlib)
# -----------------------------
with tab1:
    st.subheader("1) Cruce de mejores respuestas (BR) + bisectriz y regiones q₁≶q₂")
    # Rango para ejes
    q_sum_star = max(q1s + q2s, 1.0)
    q_max = max(1.5*q_sum_star, a / max(b, 1e-9) * 0.9, 1.0)

    fig1, ax1 = plt.subplots(figsize=(6.6, 5.4))

    q1_grid = np.linspace(0, q_max, 400)
    q2_grid = np.linspace(0, q_max, 400)

    # BR2: y = q2(q1); BR1: x = q1(q2)
    ax1.plot(q1_grid, br2(q1_grid, a, b, c2), label="BR firma 2: q₂(q₁)")
    ax1.plot(br1(q2_grid, a, b, c1), q2_grid, label="BR firma 1: q₁(q₂)")

    # Bisectriz q2 = q1
    ax1.plot([0, q_max], [0, q_max], linestyle=":", linewidth=1.2, label="Bisectriz: q₂=q₁")

    # Punto de equilibrio
    ax1.scatter([q1s], [q2s], zorder=5)
    ax1.annotate(fr"({q1s:.2f}, {q2s:.2f})", (q1s, q2s), textcoords="offset points", xytext=(8, 6))

    # Regiones q1<q2 y q1>q2
    ax1.text(0.72*q_max, 0.86*q_max, "q₁ < q₂", fontsize=11, alpha=0.85)
    ax1.text(0.86*q_max, 0.72*q_max, "q₁ > q₂", fontsize=11, alpha=0.85)

    ax1.set_xlabel("q₁")
    ax1.set_ylabel("q₂")
    ax1.set_xlim(0, q_max)
    ax1.set_ylim(0, q_max)
    ax1.grid(True, linewidth=0.5, alpha=0.5)
    ax1.legend(loc="best")
    st.pyplot(fig1)

# -----------------------------
# (2) Demanda inversa + triángulo de EC, P* y Q* (matplotlib)
# -----------------------------
with tab2:
    st.subheader("2) Demanda inversa con triángulo de EC, P* y Q*")
    fig2, ax2 = plt.subplots(figsize=(6.6, 5.4))

    Qmax = max(1.2*Qs, a / max(b, 1e-9), 1.0)
    Q_line = np.linspace(0, Qmax, 400)
    P_line = np.maximum(a - b*Q_line, 0.0)

    ax2.plot(Q_line, P_line, label="Demanda inversa: P(Q)=a−bQ")

    # Triángulo del EC: entre P(Q) y P* en [0, Q*]
    if Qs > 0 and Ps < a:
        Q_fill = np.linspace(0, Qs, 200)
        P_fill = a - b*Q_fill
        ax2.fill_between(Q_fill, P_fill, Ps, alpha=0.2, label="Excedente del consumidor")

    # Líneas y punto de equilibrio
    ax2.axvline(Qs, linestyle="--")
    ax2.axhline(Ps, linestyle="--")
    ax2.scatter([Qs], [Ps], zorder=5)

    ax2.annotate(fr"Q^\*={Qs:.2f}", (Qs, 0), textcoords="offset points", xytext=(5, 6))
    ax2.annotate(fr"P^\*={Ps:.2f}", (0, Ps), textcoords="offset points", xytext=(5, 6))

    ax2.set_xlabel("Q")
    ax2.set_ylabel("P")
    ax2.set_xlim(0, max(Qmax, Qs*1.1))
    ax2.set_ylim(0, max(a*1.05, Ps*1.2 + 1.0))
    ax2.grid(True, linewidth=0.5, alpha=0.5)
    ax2.legend(loc="best")
    st.pyplot(fig2)

# -----------------------------
# (3) Dinámica de mejores respuestas (Altair)
# -----------------------------
with tab3:
    st.subheader("3) Dinámica de mejores respuestas (Altair)")
    colA, colB, colC = st.columns(3)
    with colA:
        q1_0 = st.number_input("q₁ inicial", value=0.0, step=1.0, format="%.2f", key="q1_init")
    with colB:
        q2_0 = st.number_input("q₂ inicial", value=0.0, step=1.0, format="%.2f", key="q2_init")
    with colC:
        T = st.slider("Pasos de iteración", 1, 50, 20, key="steps_altair")

    # Trayectoria (Gauss–Seidel): primero actualiza q1 con q2^t, luego q2 con q1^{t+1}
    path = [(0, q1_0, q2_0)]
    q1_t, q2_t = q1_0, q2_0
    for t in range(1, T + 1):
        q1_next = br1(q2_t, a, b, c1)
        q2_next = br2(q1_next, a, b, c2)
        path.append((t, float(q1_next), float(q2_next)))
        q1_t, q2_t = q1_next, q2_next

    df_path = pd.DataFrame(path, columns=["step", "q1", "q2"])

    # Curvas de BR y bisectriz para contexto
    qmax_guess = max(1.5*(q1s + q2s), a / max(b, 1e-9) * 0.9, 1.0)
    qgrid = np.linspace(0, qmax_guess, 400)

    df_br1 = pd.DataFrame({"q1": br1(qgrid, a, b, c1), "q2": qgrid, "which": "BR 1: q₁(q₂)"})
    df_br2 = pd.DataFrame({"q1": qgrid, "q2": br2(qgrid, a, b, c2), "which": "BR 2: q₂(q₁)"})
    df_br = pd.concat([df_br1, df_br2], ignore_index=True)
    df_bis = pd.DataFrame({"q1": [0, qmax_guess], "q2": [0, qmax_guess]})

    # Slider para recortar la trayectoria visible
    max_step = int(df_path["step"].max())
    step_sel = st.slider("Mostrar hasta el paso", 1, max_step, max_step, key="show_until")
    df_path_vis = df_path[df_path["step"] <= step_sel]

    # Capas Altair
    base = alt.Chart().properties(width=560, height=430)

    chart_br = base.mark_line().encode(
        x=alt.X("q1:Q", title="q₁", scale=alt.Scale(domain=[0, qmax_guess])),
        y=alt.Y("q2:Q", title="q₂", scale=alt.Scale(domain=[0, qmax_guess])),
        detail="which:N"
    ).transform_lookup(
        lookup="which", from_=alt.LookupData(df_br, "which", ["q1", "q2", "which"])
    ).properties(title="Dinámica de mejores respuestas")

    chart_bis = base.mark_line(strokeDash=[4, 4]).encode(
        x="q1:Q", y="q2:Q"
    ).transform_lookup(
        lookup="q1", from_=alt.LookupData(df_bis, "q1", ["q1", "q2"])
    )

    chart_path = base.mark_line(point=True).encode(
        x="q1:Q", y="q2:Q", order="step:Q", tooltip=["step:Q", "q1:Q", "q2:Q"]
    ).transform_lookup(
        lookup="step", from_=alt.LookupData(df_path_vis, "step", ["q1", "q2", "step"])
    )

    chart_equil = base.mark_point(size=70).encode(
        x="q1:Q", y="q2:Q", tooltip=alt.value([f"q1*={q1s:.2f}", f"q2*={q2s:.2f}"])
    ).transform_calculate(q1=f"{q1s}", q2=f"{q2s}").encode(x="q1:Q", y="q2:Q")

    st.altair_chart(chart_br + chart_bis + chart_path + chart_equil, use_container_width=False)
    st.caption("Actualización Gauss–Seidel. Para Jacobi (simultánea), usa q₁ᵗ en BR2 en lugar de q₁ᵗ⁺¹.")

# -----------------------------
# Métricas resumen
# -----------------------------
st.markdown("---")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("q₁*", f"{q1s:.2f}")
m2.metric("q₂*", f"{q2s:.2f}")
m3.metric("Q*",  f"{Qs:.2f}")
m4.metric("P*",  f"{Ps:.2f}")
m5.metric("EC",  f"{CS:.2f}")
st.caption("Este app asume solución interior (si obtienes cantidades negativas con tus parámetros, ajusta a, b, c₁, c₂).")
