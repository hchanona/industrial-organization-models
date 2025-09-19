# app.py
# Cournot (demanda inversa lineal) con dos gráficas:
# 1) Cruce de mejores respuestas (en el plano (q1, q2))
# 2) Demanda inversa con excedente del consumidor, P* y Q*
# Versión simple: asumimos solución **interior** (sin tratar esquinas).

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Cournot Duopolio — Visualizador", layout="wide")

st.title("Duopolio de Cournot — Visualizador interactivo (solución interior)")

st.markdown(
    r"""
Ajusta los parámetros de la **demanda inversa lineal** y los **costos marginales** de cada firma.
- **Demanda inversa**: \( P(Q) = a - bQ \), con \( Q = q_1 + q_2 \).
- **Costos marginales**: \( c_1 \) y \( c_2 \) (constantes).

**Equilibrio de Cournot interior**:
\[
q_1^\*=\frac{a-2c_1+c_2}{3b},\quad
q_2^\*=\frac{a-2c_2+c_1}{3b},\quad
Q^\*=q_1^\*+q_2^\*=\frac{2a-(c_1+c_2)}{3b},\quad
P^\* = a - bQ^\*.
\]

Nota: este app **asume** que \(q_1^\*, q_2^\* > 0\). Si no ocurre con tus parámetros, ajusta \(a, b, c_1, c_2\) para que la solución sea interior.
"""
)

# -----------------------------
# Sidebar de parámetros
# -----------------------------
with st.sidebar:
    st.header("Parámetros")
    a = st.number_input("Intercepto de demanda a", value=100.0, step=1.0, min_value=0.0, format="%.2f")
    b = st.number_input("Pendiente de demanda b (>0)", value=1.0, step=0.1, min_value=0.0001, format="%.4f")
    c1 = st.number_input("Costo marginal firma 1 (c1)", value=20.0, step=1.0, min_value=0.0, format="%.2f")
    c2 = st.number_input("Costo marginal firma 2 (c2)", value=30.0, step=1.0, min_value=0.0, format="%.2f")
    st.markdown("---")
    st.caption("Sugerencia: prueba con **a=100, b=1, c1=20, c2=30**.")

# -----------------------------
# Funciones básicas
# -----------------------------
def cournot_interior(a, b, c1, c2):
    q1 = (a - 2*c1 + c2) / (3*b)
    q2 = (a - 2*c2 + c1) / (3*b)
    Q  = q1 + q2
    P  = a - b*Q
    return q1, q2, Q, P

def best_response_q1(q2, a, b, c1):
    # q1(q2) = (a - c1 - b q2)/(2b)  (no truncamos: asumimos interior)
    return (a - c1 - b*q2) / (2*b)

def best_response_q2(q1, a, b, c2):
    # q2(q1) = (a - c2 - b q1)/(2b)
    return (a - c2 - b*q1) / (2*b)

def consumer_surplus_linear(a, P, Q):
    # Área del triángulo bajo la demanda y por encima de P* hasta Q*
    if Q <= 0 or P >= a:
        return 0.0
    return 0.5 * (a - P) * Q

# -----------------------------
# Cálculo del equilibrio (interior)
# -----------------------------
q1_star, q2_star, Q_star, P_star = cournot_interior(a, b, c1, c2)
CS = consumer_surplus_linear(a, P_star, Q_star)

# -----------------------------
# Rango para gráficas
# -----------------------------
# Tomamos un rango que cubra de sobra el equilibrio interior
q_sum_star = max(q1_star + q2_star, 1.0)
q_max = max(1.5*q_sum_star, a / max(b, 1e-9) * 0.9)
q_max = max(q_max, 1.0)  # seguridad

# -----------------------------
# Layout en dos columnas
# -----------------------------
col1, col2 = st.columns(2, gap="large")

# ---------------------------------
# (1) Cruce de mejores respuestas en el plano (q1, q2)
# ---------------------------------
with col1:
    st.subheader("1) Cruce de mejores respuestas")
    fig1, ax1 = plt.subplots(figsize=(6.2, 5.2))

    # BR2 como función de q1: y = q2_BR(q1)
    q1_grid = np.linspace(0, q_max, 400)
    q2_br = best_response_q2(q1_grid, a, b, c2)

    # BR1 "parametrizada": x = q1_BR(q2), y = q2 (para dibujar también en (q1, q2))
    q2_grid = np.linspace(0, q_max, 400)
    q1_br = best_response_q1(q2_grid, a, b, c1)

    ax1.plot(q1_grid, q2_br, label="BR firma 2: q₂(q₁)")
    ax1.plot(q1_br, q2_grid, label="BR firma 1: q₁(q₂)")

    # Punto de equilibrio
    ax1.scatter([q1_star], [q2_star], zorder=5)
    ax1.annotate(
        fr"({q1_star:.2f}, {q2_star:.2f})",
        (q1_star, q2_star),
        textcoords="offset points",
        xytext=(8, 6),
    )

    ax1.set_xlabel("q₁")
    ax1.set_ylabel("q₂")
    ax1.set_xlim(0, q_max)
    ax1.set_ylim(0, q_max)
    ax1.grid(True, linewidth=0.5, alpha=0.5)
    ax1.legend(loc="best")
    st.pyplot(fig1)

# ---------------------------------
# (2) Demanda inversa con excedente del consumidor, P* y Q*
# ---------------------------------
with col2:
    st.subheader("2) Demanda inversa con excedente del consumidor, P* y Q*")
    fig2, ax2 = plt.subplots(figsize=(6.2, 5.2))

    Q_line_max = max(1.2*Q_star, a / max(b, 1e-9))
    Q_line = np.linspace(0, Q_line_max, 400)
    P_line = np.maximum(a - b*Q_line, 0.0)

    # Curva de demanda inversa
    ax2.plot(Q_line, P_line, label="Demanda inversa: P(Q)=a−bQ")

    # Excedente del consumidor (triángulo)
    if Q_star > 0 and P_star < a:
        ax2.fill_between([0, Q_star], [a, a], [P_star, P_star], alpha=0.2, label="Excedente del consumidor")

    # Líneas de equilibrio
    ax2.axvline(Q_star, linestyle="--")
    ax2.axhline(P_star, linestyle="--")

    # Marcas y anotaciones
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

# -----------------------------
# Métricas
# -----------------------------
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("q₁*", f"{q1_star:.2f}")
m2.metric("q₂*", f"{q2_star:.2f}")
m3.metric("Q*",  f"{Q_star:.2f}")
m4.metric("P*",  f"{P_star:.2f}")
st.caption(f"Excedente del consumidor ≈ {CS:.2f}")

st.caption(
    "Nota: Si alguna cantidad interior resulta negativa, se aplica una solución con esquina (una firma produce 0 y la otra actúa como monopolista)."
)

