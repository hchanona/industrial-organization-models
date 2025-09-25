# pages/4_Hotelling_Lineal.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Hotelling lineal (dos firmas en 0 y 1)")
st.caption("Demanda unitaria. Graficamos: ganancias por ubicación, superávit del consumidor y el mapa de precios entregados.")

# -------------------------
# Parámetros
# -------------------------
colA, colB, colC = st.columns(3)
S  = colA.number_input("Valor de reserva S", min_va

