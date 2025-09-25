
# IO Lab — Multipágina (Streamlit)

Multipágina con:

- **Duopolio de Cournot** (cantidades simultáneas) — réplica funcional para integrar tu visualizador al multipágina.
- **Duopolio de Stackelberg (líder–seguidor)** (cantidades secuenciales).

> Este proyecto **no modifica tu script original**; solo crea un programa aparte con páginas. Puedes reemplazar la segunda por Bertrand/Hotelling cuando lo decidas.

## Estructura

```
.
├── Home.py
├── pages
│   ├── 1_Duopolio_de_Cournot.py
│   └── 2_Stackelberg_Duopolio.py
└── requirements.txt
```

## Cómo ejecutar

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Luego usa el selector de páginas (arriba a la izquierda) para cambiar entre modelos.
