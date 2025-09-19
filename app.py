# --- Dinámica de mejores respuestas (Altair) encapsulada ---
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

def render_cournot_dynamics_altair(a: float, b: float, c1: float, c2: float, key_prefix: str = "dyn"):
    """Renderiza trayectoria de mejores respuestas (Gauss–Seidel) en Altair.
    Llama: render_cournot_dynamics_altair(a,b,c1,c2)
    """
    # --- helpers ---
    def br1(q2, a, b, c1):  # q1(q2)
        return (a - c1 - b*q2) / (2*b)

    def br2(q1, a, b, c2):  # q2(q1)
        return (a - c2 - b*q1) / (2*b)

    def eq_cournot(a, b, c1, c2):
        q1 = (a - 2*c1 + c2) / (3*b)
        q2 = (a - 2*c2 + c1) / (3*b)
        return q1, q2

    st.markdown("### Dinámica (Altair): mejores respuestas iteradas")

    colA, colB, colC = st.columns(3)
    with colA:
        q1_0 = st.number_input("q₁ inicial", value=0.0, step=1.0, format="%.2f", key=f"{key_prefix}_q1_0")
    with colB:
        q2_0 = st.number_input("q₂ inicial", value=0.0, step=1.0, format="%.2f", key=f"{key_prefix}_q2_0")
    with colC:
        T = st.slider("Pasos de iteración", 1, 50, 20, key=f"{key_prefix}_steps")

    # --- trayectoria (Gauss–Seidel) ---
    path = [(0, q1_0, q2_0)]
    q1_t, q2_t = q1_0, q2_0
    for t in range(1, T + 1):
        q1_next = br1(q2_t, a, b, c1)
        q2_next = br2(q1_next, a, b, c2)
        path.append((t, q1_next, q2_next))
        q1_t, q2_t = q1_next, q2_next

    df_path = pd.DataFrame(path, columns=["step", "q1", "q2"])
    q1_star, q2_star = eq_cournot(a, b, c1, c2)

    # --- curvas de reacción y bisectriz ---
    qmax_guess = max(1.5 * (q1_star + q2_star), a / max(b, 1e-9) * 0.9, 1.0)
    qgrid = np.linspace(0, qmax_guess, 400)

    df_br1 = pd.DataFrame({"q1": br1(qgrid, a, b, c1), "q2": qgrid, "which": "BR 1: q₁(q₂)"})
    df_br2 = pd.DataFrame({"q1": qgrid, "q2": br2(qgrid, a, b, c2), "which": "BR 2: q₂(q₁)"})
    df_br = pd.concat([df_br1, df_br2], ignore_index=True)
    df_bis = pd.DataFrame({"q1": [0, qmax_guess], "q2": [0, qmax_guess]})

    # --- slider para prefijo de trayectoria ---
    max_step = int(df_path["step"].max())
    step_sel = st.slider("Mostrar hasta el paso", 1, max_step, max_step, key=f"{key_prefix}_show_until")
    df_path_vis = df_path[df_path["step"] <= step_sel]

    # --- gráficos Altair ---
    base = alt.Chart().properties(width=520, height=420)

    chart_br = base.mark_line().encode(
        x=alt.X("q1:Q", title="q₁", scale=alt.Scale(domain=[0, qmax_guess])),
        y=alt.Y("q2:Q", title="q₂", scale=alt.Scale(domain=[0, qmax_guess])),
        detail="which:N",
        tooltip=["q1:Q", "q2:Q", "which:N"]
    )

    chart_path = base.mark_line(point=True).encode(
        x="q1:Q", y="q2:Q", order="step:Q", tooltip=["step:Q", "q1:Q", "q2:Q"]
    )

    chart_equil = base.mark_point(size=70).encode(
        x="q1:Q", y="q2:Q", tooltip=alt.value([f"q1*={q1_star:.2f}", f"q2*={q2_star:.2f}"])
    )

    chart_bis = base.mark_line(strokeDash=[4, 4]).encode(x="q1:Q", y="q2:Q")

    final_chart = (
        chart_br.transform_lookup(
            lookup="which", from_=alt.LookupData(df_br, "which", ["q1", "q2", "which"])
        ).properties(title="Dinámica de mejores respuestas (Altair)")
        +
        chart_bis.transform_lookup(
            lookup="q1", from_=alt.LookupData(df_bis, "q1", ["q1", "q2"])
        )
        +
        chart_path.transform_lookup(
            lookup="step", from_=alt.LookupData(df_path_vis, "step", ["q1", "q2", "step"])
        )
        +
        chart_equil.transform_calculate(q1=f"{q1_star}", q2=f"{q2_star}").encode(x="q1:Q", y="q2:Q")
    )

    st.altair_chart(final_chart, use_container_width=False)
    st.caption("Actualización Gauss–Seidel: primero se actualiza q₁ con q₂ᵗ y luego q₂ con q₁ᵗ⁺¹. (Para Jacobi, usa q₁ᵗ en la BR2.)")
