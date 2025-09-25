# hotelling.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def hotelling_lineal_tab():
    st.subheader("Hotelling lineal (dos firmas en 0 y 1)")
    st.caption("Demanda unitaria; puedes usar el equilibrio (cobertura total) o fijar precios manualmente. "
               "El gráfico 1 muestra ganancias por ubicación; el 2, el superávit de consumidores.")

    c1, c2 = 1.0, 1.0  # valores iniciales sugeridos
    colA, colB, colC = st.columns(3)
    S = colA.number_input("Valor de reserva S", min_value=0.0, value=10.0, step=0.1, format="%.2f")
    t = colB.number_input("Costo de transporte t", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    c1 = colC.number_input("Costo marginal c₁", min_value=0.0, value=c1, step=0.1, format="%.2f")
    c2 = colC.number_input("Costo marginal c₂", min_value=0.0, value=c2, step=0.1, format="%.2f", key="c2_hot")

    modo = st.radio("Precios", ["Equilibrio de Nash (cobertura total)", "Elegir manualmente"], horizontal=True)
    if modo.startswith("Equilibrio"):
        # p* con cobertura total: p1*=(2c1+c2+3t)/3, p2*=(c1+2c2+3t)/3
        p1 = (2*c1 + c2 + 3*t)/3
        p2 = (c1 + 2*c2 + 3*t)/3
        st.info(f"Precios de equilibrio: p₁* = {p1:.2f}, p₂* = {p2:.2f}")
    else:
        colp1, colp2 = st.columns(2)
        p1 = colp1.number_input("Precio p₁", min_value=0.0, value=float(np.round((2*c1 + c2 + 3*t)/3, 2)),
                                step=0.1, format="%.2f")
        p2 = colp2.number_input("Precio p₂", min_value=0.0, value=float(np.round((c1 + 2*c2 + 3*t)/3, 2)),
                                step=0.1, format="%.2f")

    # Malla y utilidades
    x = np.linspace(0.0, 1.0, 2001)
    delivered1 = p1 + t*x
    delivered2 = p2 + t*(1 - x)
    u1 = S - delivered1
    u2 = S - delivered2
    u0 = np.zeros_like(x)
    best = np.maximum.reduce([u1, u2, u0])
    choose1 = (u1 == best) & (best > 0)
    choose2 = (u2 == best) & (best > 0)

    q1 = choose1.mean()
    q2 = choose2.mean()
    no_buy = 1.0 - (q1 + q2)

    # Métricas
    x_star = np.clip((p2 - p1 + t)/(2*t), 0.0, 1.0)  # punto indiferente (si hay)
    pi1 = (p1 - c1) * q1
    pi2 = (p2 - c2) * q2
    cs_density = best.clip(min=0.0)
    CS = float(np.trapz(cs_density, x))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("x̂ (indiferente)", f"{x_star:.2f}")
    m2.metric("Cuotas q₁ / q₂", f"{q1:.2f} / {q2:.2f}")
    m3.metric("Ganancias π₁ / π₂", f"{pi1:.2f} / {pi2:.2f}")
    m4.metric("Superávit consumidores (total)", f"{CS:.2f}")
    if no_buy > 1e-6:
        st.warning(f"Mercado **no cubierto**: {no_buy:.2f} no compra (sube S o baja precios).")

    # 1) Gráfico: ganancias de las empresas por ubicación (productor)
    ps = np.zeros_like(x)
    margin1 = max(p1 - c1, 0.0)
    margin2 = max(p2 - c2, 0.0)
    ps[choose1] = margin1
    ps[choose2] = margin2

    fig1, ax1 = plt.subplots()
    ax1.plot(x, ps, linewidth=2)
    ax1.fill_between(x, 0, ps, alpha=0.3)
    ax1.set_xlabel("Ubicación del consumidor  x ∈ [0,1]")
    ax1.set_ylabel("Ganancia por consumidor")
    ax1.set_title("Ganancias de las empresas a lo largo de la línea")
    st.pyplot(fig1, clear_figure=True)

    # 2) Gráfico: superávit del consumidor por ubicación (envolvente)
    fig2, ax2 = plt.subplots()
    ax2.plot(x, cs_density, linewidth=2)
    ax2.fill_between(x, 0, cs_density, alpha=0.3)
    ax2.axvline(x_star, linestyle="--")
    ax2.set_xlabel("Ubicación del consumidor  x ∈ [0,1]")
    ax2.set_ylabel("Superávit del consumidor")
    ax2.set_title("Superávit del consumidor (S - precio entregado)")
    st.pyplot(fig2, clear_figure=True)

    # Extra opcional: gráfico de precios entregados como guía visual
    with st.expander("Ver precios entregados y partición del mercado"):
        fig3, ax3 = plt.subplots()
        ax3.plot(x, delivered1, label="p₁ + t·x")
        ax3.plot(x, delivered2, label="p₂ + t·(1-x)")
        ax3.axvline(x_star, linestyle="--")
        ax3.set_xlabel("x")
        ax3.set_ylabel("Precio entregado")
        ax3.legend()
        st.pyplot(fig3, clear_figure=True)
