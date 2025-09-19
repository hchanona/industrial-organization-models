# app.py
# Duopolio de Cournot (demanda inversa lineal) con dos gráficas:
# 1) Cruce de mejores respuestas
# 2) Demanda inversa con excedente del consumidor, precio y cantidad de equilibrio

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Cournot Duopolio — Visualizador", layout="wide")

st.title("Duopolio de Cournot — Visualizador interactivo")

st.markdown(
    r"""
Ajusta los parámetros de la **demanda inversa lineal** y los **costos marginales** de cada firma.
- **Demanda inversa**: \( P(Q) = a - bQ \), con \( Q = q_1 + q_2 \).
- **Costos marginales**: \( c_1 \) y \( c_2 \) (constantes).

El equilibrio de Cournot **interior** (sin restricciones) es:
\[
q_1^\*=\frac{a-2c_1+c_2}{3b},\quad
q_2^\*=\frac{a-2c_2+c_1}{3b},\quad
Q^\*=q_1^\*+q_2^\*,\quad
P^\* = a - bQ^\*.
\]

Si alguna \(q_i^\*\) resulta negativa, se aplica solución **con esquina**:
- Si \(q_1^\*<0\): \(q_1=0\) y la firma 2 produce como monopolista: \(q_2=\max\{(a-c_2)/(2b), 0\}\).
- Si \(q_2^\*<0\): \(q_2=0\) y la firma 1 produce como monopolista: \(q_1=\max\{(a-c_1)/(2b), 0\}\).
- Si ambas negativas: \(Q=0\), \(P=a\) (sin ventas).
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
    st.caption("Sugerencia: prueba con **a=100, b=1, c1=20, c2=30** para comenzar.")

# -----------------------------
# Funciones auxiliares
# -----------------------------
def cournot_unconstrained(a, b, c1, c2):
    """Equilibrio interior (sin truncar): puede dar cantidades negativas."""
    q1 = (a - 2*c1 + c2) / (3*b)
    q2 = (a - 2*c2 + c1) / (3*b)
    Q = q1 + q2
    P = a - b*Q
    return q1, q2, Q, P

def monopoly_quantity(a, b, c):
    """Cantidad de monopolio lineal con CM constante c (y demanda P=a-bQ)."""
    return max((a - c) / (2*b), 0.0)

def cournot_with_corners(a, b, c1, c2):
    """Equilibrio considerando esquinas si alguna cantidad interior es negativa."""
    q1_u, q2_u, Q_u, P_u = cournot_unconstrained(a, b, c1, c2)

    if q1_u >= 0 and q2_u >= 0:
        q1, q2 = q1_u, q2_u
    elif q1_u < 0 and q2_u >= 0:
        q1 = 0.0
        q2 = monopoly_quantity(a, b, c2)
    elif q2_u < 0 and q1_u >= 0:
        q2 = 0.0
        q1 = monopoly_quantity(a, b, c1)
    else:
        q1, q2 = 0.0, 0.0

    Q = q1 + q2
    P = max(a - b*Q, 0.0)
    return q1, q2, Q, P

def best_response_q1(q2, a, b, c1):
    """Mejor respuesta de la firma 1 ante q2 (truncada a [0, ∞))."""
    return max((a - c1 - b*q2) / (2*b), 0.0)

def best_response_q2(q1, a, b, c2):
    """Mejor respuesta de la firma 2 ante q1 (truncada a [0, ∞))."""
    return max((a - c2 - b*q1) / (2*b), 0.0)

def consumer_surplus_linear(a, P, Q):
    """Excedente del consumidor para demanda lineal P=a-bQ (triángulo)."""
    if Q <= 0:
        return 0.0
    return 0.5 * (a - P) * Q

def profits_linear(a, b, q1, q2, c1, c2):
    """Beneficios de cada firma con costos marginales constantes."""
    Q = q1 + q2
    P = max(a - b*Q, 0.0)
    pi1 = max(P - c1, 0.0) * q1
    pi2 = max(P - c2, 0.0) * q2
    return pi1, pi2, P, Q

# -----------------------------
# Cálculo del equilibrio
# -----------------------------
q1_star, q2_star, Q_star, P_star = cournot_with_corners(a, b, c1, c2)
CS = consumer_surplus_linear(a, P_star, Q_star)
pi1, pi2, _, _ = profits_linear(a, b, q1_star, q2_star, c1, c2)

# Cantidades de referencia para ejes
q1_mon = monopoly_quantity(a, b, c1)
q2_mon = monopoly_quantity(a, b, c2)
Q_mon_min_c = monopoly_quantity(a, b, min(c1, c2))

# Escalas para las gráficas
q_scale = max(q1_mon + q2_mon, Q_mon_min_c * 1.5, Q_star * 1.5, 1.0)
Q_max_plot = max(Q_star * 1.5, Q_mon_min_c * 1.5, (a / b) * 1.0 if b > 0 else 10.0, 1.0)

# -----------------------------
# Layout en dos columnas
# -----------------------------
col1, col2 = st.columns(2, gap="large")

# ---------------------------------
# Gráfica 1: Cruce de mejores respuestas
# ---------------------------------
with col1:
    st.subheader("1) Cruce de mejores respuestas")
    fig1, ax1 = plt.subplots(figsize=(6, 5))

    # Curva de mejor respuesta de la firma 1: q1 = (a - c1 - b q2) / (2b)
    q2_grid = np.linspace(0, q_scale, 400)
    q1_br = np.maximum((a - c1 - b*q2_grid) / (2*b), 0.0)

    # Curva de mejor respuesta de la firma 2: q2 = (a - c2 - b q1) / (2b)
    q1_grid = np.linspace(0, q_scale, 400)
    q2_br = np.maximum((a - c2 - b*q1_grid) / (2*b), 0.0)

    ax1.plot(q2_grid, q1_br, label="BR de la firma 1: q₁(q₂)")
    ax1.plot(q1_grid, q2_br, label="BR de la firma 2: q₂(q₁)")

    # Punto de equilibrio
    ax1.scatter(q2_star, q1_star, s=60, zorder=5)
    ax1.annotate(
        fr"Equilibrio (q₁^\*={q1_star:.2f}, q₂^\*={q2_star:.2f})",
        (q2_star, q1_star),
        textcoords="offset points",
        xytext=(8, 8),
    )

    ax1.set_xlabel("q₂")
    ax1.set_ylabel("q₁")
    ax1.set_xlim(0, q_scale)
    ax1.set_ylim(0, q_scale)
    ax1.grid(True, linewidth=0.5, alpha=0.5)
    ax1.legend(loc="best")
    st.pyplot(fig1)

# ---------------------------------
# Gráfica 2: Demanda inversa con EC, P* y Q*
# ---------------------------------
with col2:
    st.subheader("2) Demanda inversa con excedente del consumidor, P* y Q*")
    fig2, ax2 = plt.subplots(figsize=(6, 5))

    Q_line = np.linspace(0, max(Q_max_plot, 1.0), 400)
    P_line = np.maximum(a - b*Q_line, 0.0)

    # Demanda inversa
    ax2.plot(Q_line, P_line, label="Demanda inversa: P(Q)=a−bQ")

    # Sombreado del excedente del consumidor (triángulo bajo la intercepto a y sobre P*)
    if Q_star > 0 and P_star < a:
        ax2.fill_between([0, Q_star], [a, a], [P_star, P_star], alpha=0.2, label="Excedente del consumidor")

    # Líneas de equilibrio
    ax2.axvline(Q_star, linestyle="--")
    ax2.axhline(P_star, linestyle="--")

    # Marcas y anotaciones
    ax2.scatter([Q_star], [P_star], zorder=5)
    ax2.annotate(fr"Q^\*={Q_star:.2f}", (Q_star, 0), textcoords="offset points", xytext=(5, 5))
    ax2.annotate(fr"P^\*={P_star:.2f}", (0, P_star), textcoords="offset points", xytext=(5, 5))

    ax2.set_xlabel("Q")
    ax2.set_ylabel("P")
    ax2.set_xlim(0, max(Q_max_plot, Q_star*1.2, 1.0))
    ax2.set_ylim(0, max(a*1.05, P_star*1.5 + 1))
    ax2.grid(True, linewidth=0.5, alpha=0.5)
    ax2.legend(loc="best")
    st.pyplot(fig2)

# -----------------------------
# Métricas y detalles numéricos
# -----------------------------
st.markdown("---")
st.subheader("Resumen numérico del equilibrio")
c1_col, c2_col, out_col = st.columns([1, 1, 2])

with c1_col:
    st.metric("c₁", f"{c1:.2f}")
    st.metric("q₁*", f"{q1_star:.2f}")
    st.metric("π₁", f"{pi1:.2f}")

with c2_col:
    st.metric("c₂", f"{c2:.2f}")
    st.metric("q₂*", f"{q2_star:.2f}")
    st.metric("π₂", f"{pi2:.2f}")

with out_col:
    st.metric("Q*", f"{Q_star:.2f}")
    st.metric("P*", f"{P_star:.2f}")
    st.metric("Excedente del consumidor", f"{CS:.2f}")

st.caption(
    "Nota: Si alguna cantidad interior resulta negativa, se aplica una solución con esquina (una firma produce 0 y la otra actúa como monopolista)."
)
