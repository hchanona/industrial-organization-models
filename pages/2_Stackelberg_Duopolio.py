
# Duopolio de Stackelberg (líder–seguidor) con demanda inversa lineal
# 1) BRs y punto de Stackelberg (en el plano (q1, q2))
# 2) Demanda inversa con excedente del consumidor, P* y Q*
# Asumimos solución interior (q1*>0, q2*>0).

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.title("Duopolio de Stackelberg (Líder–Seguidor)")

with st.sidebar:
    st.header("Parámetros")
    a  = st.number_input("Intercepto de demanda a", value=100.0, step=1.0, min_value=0.0, format="%.2f")
    b  = st.number_input("Pendiente de demanda b (>0)", value=1.0,  step=0.1, min_value=0.0001, format="%.4f")
    c1 = st.number_input("Costo marginal líder (c1)", value=20.0,   step=1.0, min_value=0.0, format="%.2f")
    c2 = st.number_input("Costo marginal seguidor (c2)", value=30.0,   step=1.0, min_value=0.0, format="%.2f")
    st.caption("Ejemplo: a=100, b=1, c1=20, c2=30 (interior).")

# Funciones de reacción (usamos la de seguidor explícitamente)
def br_follower(q1, a, b, c2):
    return (a - c2 - b*q1) / (2*b)

def br_cournot_firm1(q2, a, b, c1):
    # Solo para visualizar el cruce Cournot (referencia), no para el equilibrio Stackelberg
    return (a - c1 - b*q2) / (2*b)

# Solución de Stackelberg (líder=1, seguidor=2):
# q1* = (a + c2 - 2 c1) / (2 b)
# q2* = (a - 3 c2 + 2 c1) / (4 b)
# Q*  = (3 a - c2 - 2 c1) / (4 b)
# P*  = a - b Q* = (a + c2 + 2 c1) / 4
q1_star = (a + c2 - 2*c1) / (2*b)
q2_star = (a - 3*c2 + 2*c1) / (4*b)
Q_star  = q1_star + q2_star
P_star  = a - b*Q_star

def cs_linear(a, P, Q):
    return 0.0 if (Q <= 0 or P >= a) else 0.5 * (a - P) * Q

CS = cs_linear(a, P_star, Q_star)

# Rango para gráfica en (q1, q2)
q1q2_sum = max(q1_star + q2_star, 1.0)
q_max = max(1.5*q1q2_sum, a / max(b, 1e-9) * 0.9, 1.0)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("1) Reacción del seguidor y referencia Cournot")
    fig1, ax1 = plt.subplots(figsize=(6.2, 5.2))

    q1_grid = np.linspace(0, q_max, 400)
    q2_grid = np.linspace(0, q_max, 400)

    # BR del seguidor (firma 2)
    ax1.plot(q1_grid, br_follower(q1_grid, a, b, c2), label="BR seguidor: q₂(q₁)")

    # BR de firma 1 al estilo Cournot (solo referencia visual)
    ax1.plot(br_cournot_firm1(q2_grid, a, b, c1), q2_grid, linestyle="--", label="BR firma 1 (Cournot, ref.)")

    # Punto de Stackelberg (sobre BR del seguidor pero NO en el cruce de BRs)
    ax1.scatter([q1_star], [q2_star], zorder=5)
    ax1.annotate(fr"({q1_star:.2f}, {q2_star:.2f})", (q1_star, q2_star), textcoords="offset points", xytext=(8, 6))

    # Línea de compromiso del líder (marcar q1* vertical)
    ax1.axvline(q1_star, linestyle=":", linewidth=1.2, label="Compromiso del líder: q₁*")

    ax1.set_xlabel("q₁ (líder)")
    ax1.set_ylabel("q₂ (seguidor)")
    ax1.set_xlim(0, q_max)
    ax1.set_ylim(0, q_max)
    ax1.grid(True, linewidth=0.5, alpha=0.5)
    ax1.legend(loc="best")
    st.pyplot(fig1)

with col2:
    st.subheader("2) Demanda inversa con excedente del consumidor, P* y Q*")
    fig2, ax2 = plt.subplots(figsize=(6.2, 5.2))

    Qmax = max(1.2*Q_star, a / max(b, 1e-9))
    Q_line = np.linspace(0, Qmax, 400)
    P_line = np.maximum(a - b*Q_line, 0.0)
    ax2.plot(Q_line, P_line, label="Demanda inversa: P(Q)=a−bQ")

    if Q_star > 0 and P_star < a:
        Q_fill = np.linspace(0, Q_star, 200)
        P_fill = a - b*Q_fill
        ax2.fill_between(Q_fill, P_fill, P_star, alpha=0.2, label="Excedente del consumidor")

    ax2.axvline(Q_star, linestyle="--")
    ax2.axhline(P_star, linestyle="--")
    ax2.scatter([Q_star], [P_star], zorder=5)

    ax2.annotate(fr"Q*={Q_star:.2f}", (Q_star, 0), textcoords="offset points", xytext=(5, 6))
    ax2.annotate(fr"P*={P_star:.2f}", (0, P_star), textcoords="offset points", xytext=(5, 6))

    ax2.set_xlabel("Q")
    ax2.set_ylabel("P")
    ax2.set_xlim(0, max(Qmax, Q_star*1.1, 1.0))
    ax2.set_ylim(0, max(a*1.05, P_star*1.2 + 1.0))
    ax2.grid(True, linewidth=0.5, alpha=0.5)
    ax2.legend(loc="best")
    st.pyplot(fig2)

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("q₁* (líder)", f"{q1_star:.2f}")
m2.metric("q₂* (seguidor)", f"{q2_star:.2f}")
m3.metric("Q*",  f"{Q_star:.2f}")
m4.metric("P*",  f"{P_star:.2f}")
st.caption(f"Excedente del consumidor ≈ {CS:.2f}")
