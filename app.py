# app.py
# Cournot (demanda inversa lineal) con dos gráficas:
# 1) Cruce de mejores respuestas (plano (q1, q2)) + primera bisectriz y regiones q1>q2 / q1<q2
# 2) Demanda inversa con excedente del consumidor, P* y Q*
# Asumimos solución interior.

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Cournot Duopolio — Visualizador", layout="wide")
st.title("Duopolio de Cournot — Visualizador interactivo (solución interior)")

st.markdown(
    r"""
- **Demanda inversa**: \(P(Q)=a-bQ\), con \(Q=q_1+q_2\).
- **Costos marginales**: \(c_1, c_2\) constantes.

**Equilibrio (interior)**:
\[
q_1^\*=\frac{a-2c_1+c_2}{3b},\quad
q_2^\*=\frac{a-2c_2+c_1}{3b},\quad
Q^\*=\frac{2a-(c_1+c_2)}{3b},\quad
P^\*=a-bQ^\*.
\]
"""
)

with st.sidebar:
    st.header("Parámetros")
    a = st.number_input("Intercepto de demanda a", value=100.0, step=1.0, min_value=0.0, format="%.2f")
    b = st.number_input("Pendiente de demanda b (>0)", value=1.0, step=0.1, min_value=1e-6, format="%.4f")
    c1 = st.number_input("Costo marginal firma 1 (c1)", value=20.0, step=1.0, min_value=0.0, format="%.2f")
    c2 = st.number_input("Costo marginal firma 2 (c2)", value=30.0, step=1.0, min_value=0.0, format="%.2f")
    st.caption("Sugerencia: a=100, b=1, c1=20, c2=30.")

# --- funciones ---
def cournot_interior(a, b, c1, c2):
    q1 = (a - 2*c1 + c2) / (3*b)
    q2 = (a - 2*c2 + c1) / (3*b)
    Q  = q1 + q2
    P  = a - b*Q
    return q1, q2, Q, P

def br1(q2, a, b, c1):
    return (a - c1 - b*q2) / (2*b)

def br2(q1, a, b, c2):
    return (a - c2 - b*q1) / (2*b)

def cs_linear(a, P, Q):
    if Q <= 0 or P >= a:
        return 0.0
    return 0.5*(a-P)*Q

# --- equilibrio y métricas ---
q1_star, q2_star, Q_star, P_star = cournot_interior(a, b, c1, c2)
CS = cs_linear(a, P_star, Q_star)

# --- rangos ---
q_sum_star = max(q1_star + q2_star, 1.0)
q_max = max(1.5*q_sum_star, a/max(b,1e-9)*0.9, 1.0)

col1, col2 = st.columns(2, gap="large")

# ========================= (1) BRs + bisectriz =========================
with col1:
    st.subheader("1) Cruce de mejores respuestas")
    fig1, ax1 = plt.subplots(figsize=(6.4, 5.2))

    q1_grid = np.linspace(0, q_max, 400)
    q2_grid = np.linspace(0, q_max, 400)

    ax1.plot(q1_grid, br2(q1_grid, a, b, c2), label="BR firma 2: q₂(q₁)")
    ax1.plot(br1(q2_grid, a, b, c1), q2_grid, label="BR firma 1: q₁(q₂)")

    # Primera bisectriz q1 = q2
    ax1.plot([0, q_max], [0, q_max], linestyle=":", linewidth=1.5, label="Primera bisectriz: q₁=q₂")

    # Punto de equilibrio
    ax1.scatter([q1_star], [q2_star], zorder=5)
    ax1.annotate(f"({q1_star:.2f}, {q2_star:.2f})", (q1_star, q2_star),
                 textcoords="offset points", xytext=(8, 6))

    # Etiquetas de regiones
    # Debajo de la bisectriz: q2<q1 ⇒ "q1>q2"
    ax1.text(0.70*q_max, 0.45*q_max, "q1 > q2", fontsize=11, alpha=0.8)
    # Encima de la bisectriz: q2>q1 ⇒ "q1<q2"
    ax1.text(0.30*q_max, 0.80*q_max, "q1 < q2", fontsize=11, alpha=0.8)

    ax1.set_xlabel("q₁")
    ax1.set_ylabel("q₂")
    ax1.set_xlim(0, q_max)
    ax1.set_ylim(0, q_max)
    ax1.grid(True, linewidth=0.5, alpha=0.5)
    ax1.legend(loc="best")
    st.pyplot(fig1)

# ========================= (2) Demanda inversa =========================
with col2:
    st.subheader("2) Demanda inversa con excedente del consumidor, P* y Q*")
    fig2, ax2 = plt.subplots(figsize=(6.4, 5.2))

    Q_line_max = max(1.2*Q_star, a/max(b,1e-9))
    Q_line = np.linspace(0, Q_line_max, 400)
    P_line = np.maximum(a - b*Q_line, 0.0)

    ax2.plot(Q_line, P_line, label="Demanda inversa: P(Q)=a−bQ")
    if Q_star > 0 and P_star < a:
        ax2.fill_between([0, Q_star], [a, a], [P_star, P_star], alpha=0.2, label="Excedente del consumidor")

    ax2.axvline(Q_star, linestyle="--")
    ax2.axhline(P_star, linestyle="--")
    ax2.scatter([Q_star], [P_star], zorder=5)

    ax2.annotate(fr"Q^\*={Q_star:.2f}", (Q_star, 0), textcoords="offset points", xytext=(5, 6))
    ax2.annotate(fr"P^\*={P_star:.2f}", (0, P_star), textcoords="offset points", xytext=(5, 6))

    ax2.set_xlabel("Q")
    ax2.set_ylabel("P")
    ax2.set_xlim(0, max(Q_line_max, Q_star*1.1, 1.0))
    ax2.set_ylim(0, max(a*1.05, P_star*1.2 + 1.0))
    ax2.grid(True, linewidth=0.5, alpha=0.5)
    ax2.legend(loc="best")
    st.pyplot(fig2)

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("q₁*", f"{q1_star:.2f}")
m2.metric("q₂*", f"{q2_star:.2f}")
m3.metric("Q*",  f"{Q_star:.2f}")
m4.metric("P*",  f"{P_star:.2f}")
st.caption(f"Excedente del consumidor ≈ {CS:.2f}")

