# app.py
# Cournot (demanda inversa lineal) con dos gráficas:
# 1) Cruce de mejores respuestas (plano (q1, q2) + bisectriz y regiones)
# 2) Demanda inversa con excedente del consumidor (triángulo), P* y Q*
# Asumimos solución interior.

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Cournot Duopolio — Visualizador", layout="wide")
st.title("Duopolio de Cournot")

# -----------------------------
# Sidebar de parámetros
# -----------------------------
with st.sidebar:
    st.header("Parámetros")
    a  = st.number_input("Intercepto de demanda a", value=100.0, step=1.0, min_value=0.0, format="%.2f")
    b  = st.number_input("Pendiente de demanda b (>0)", value=1.0,  step=0.1, min_value=0.0001, format="%.4f")
    c1 = st.number_input("Costo marginal firma 1 (c1)", value=20.0,   step=1.0, min_value=0.0, format="%.2f")
    c2 = st.number_input("Costo marginal firma 2 (c2)", value=30.0,   step=1.0, min_value=0.0, format="%.2f")
    st.caption("Ejemplo: a=100, b=1, c1=20, c2=30 (solución interior).")

# -----------------------------
# Funciones
# -----------------------------
def cournot_interior(a, b, c1, c2):
    q1 = (a - 2*c1 + c2) / (3*b)
    q2 = (a - 2*c2 + c1) / (3*b)
    Q  = q1 + q2
    P  = a - b*Q
    return q1, q2, Q, P

def br1(q2, a, b, c1):  # q1(q2)
    return (a - c1 - b*q2) / (2*b)

def br2(q1, a, b, c2):  # q2(q1)
    return (a - c2 - b*q1) / (2*b)

def cs_linear(a, P, Q):
    return 0.0 if (Q <= 0 or P >= a) else 0.5 * (a - P) * Q

# -----------------------------
# Cálculo del equilibrio
# -----------------------------
q1s, q2s, Qs, Ps = cournot_interior(a, b, c1, c2)
CS = cs_linear(a, Ps, Qs)

# Rango para gráficas
q_sum_star = max(q1s + q2s, 1.0)
q_max = max(1.5*q_sum_star, a / max(b, 1e-9) * 0.9, 1.0)

col1, col2 = st.columns(2, gap="large")

# ---------------------------------
# (1) Cruce de mejores respuestas + bisectriz y regiones
# ---------------------------------
with col1:
    st.subheader("1) Cruce de mejores respuestas")
    fig1, ax1 = plt.subplots(figsize=(6.2, 5.2))

    q1_grid = np.linspace(0, q_max, 400)
    q2_grid = np.linspace(0, q_max, 400)

    # BR2: y = q2(q1)
    ax1.plot(q1_grid, br2(q1_grid, a, b, c2), label="BR firma 2: q₂(q₁)")
    # BR1: x = q1(q2), y = q2  (para dibujarla en el plano (q1, q2))
    ax1.plot(br1(q2_grid, a, b, c1), q2_grid, label="BR firma 1: q₁(q₂)")

    # Bisectriz q2 = q1
    ax1.plot([0, q_max], [0, q_max], linestyle=":", linewidth=1.2, label="Bisectriz: q₂=q₁")

    # Punto de equilibrio
    ax1.scatter([q1s], [q2s], zorder=5)
    ax1.annotate(fr"({q1s:.2f}, {q2s:.2f})", (q1s, q2s), textcoords="offset points", xytext=(8, 6))

    # Etiquetas de regiones
    ax1.text(0.72*q_max, 0.86*q_max, "q₁ < q₂", fontsize=11, alpha=0.85)
    ax1.text(0.86*q_max, 0.72*q_max, "q₁ > q₂", fontsize=11, alpha=0.85)

    ax1.set_xlabel("q₁")
    ax1.set_ylabel("q₂")
    ax1.set_xlim(0, q_max)
    ax1.set_ylim(0, q_max)
    ax1.grid(True, linewidth=0.5, alpha=0.5)
    ax1.legend(loc="best")
    st.pyplot(fig1)

# ---------------------------------
# (2) Demanda inversa + excedente del consumidor (triángulo), P* y Q*
# ---------------------------------
with col2:
    st.subheader("2) Demanda inversa con excedente del consumidor, P* y Q*")
    fig2, ax2 = plt.subplots(figsize=(6.2, 5.2))

    Qmax = max(1.2*Qs, a / max(b, 1e-9))
    Q_line = np.linspace(0, Qmax, 400)
    P_line = np.maximum(a - b*Q_line, 0.0)
    ax2.plot(Q_line, P_line, label="Demanda inversa: P(Q)=a−bQ")

    # Triángulo del excedente del consumidor entre P(Q) y P* en [0, Q*]
    if Qs > 0 and Ps < a:
        Q_fill = np.linspace(0, Qs, 200)
        P_fill = a - b*Q_fill
        ax2.fill_between(Q_fill, P_fill, Ps, alpha=0.2, label="Excedente del consumidor")

    # Líneas y punto de equilibrio
    ax2.axvline(Qs, linestyle="--")
    ax2.axhline(Ps, linestyle="--")
    ax2.scatter([Qs], [Ps], zorder=5)

    ax2.annotate(fr"Q*={Qs:.2f}", (Qs, 0), textcoords="offset points", xytext=(5, 6))
    ax2.annotate(fr"P*={Ps:.2f}", (0, Ps), textcoords="offset points", xytext=(5, 6))

    ax2.set_xlabel("Q")
    ax2.set_ylabel("P")
    ax2.set_xlim(0, max(Qmax, Qs*1.1, 1.0))
    ax2.set_ylim(0, max(a*1.05, Ps*1.2 + 1.0))
    ax2.grid(True, linewidth=0.5, alpha=0.5)
    ax2.legend(loc="best")
    st.pyplot(fig2)

# -----------------------------
# Métricas
# -----------------------------
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("q₁*", f"{q1s:.2f}")
m2.metric("q₂*", f"{q2s:.2f}")
m3.metric("Q*",  f"{Qs:.2f}")
m4.metric("P*",  f"{Ps:.2f}")
st.caption(f"Excedente del consumidor ≈ {CS:.2f}")


