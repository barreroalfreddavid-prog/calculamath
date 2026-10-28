import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import quad

st.set_page_config(page_title="CalculaMath", page_icon="∫", layout="wide")

st.title("∫ CalculaMath")
st.caption("Calculadora de cálculo diferencial e integral: derivadas, extremos, integrales, gráficas y optimización.")

x = sp.symbols("x", real=True)
ALLOWED = {
    "x": x,
    "pi": sp.pi,
    "E": sp.E,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sqrt": sp.sqrt, "log": sp.log, "ln": sp.log,
    "exp": sp.exp, "abs": sp.Abs,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
}

def parse_function(raw):
    raw = raw.strip().replace("^", "**")
    if not raw:
        raise ValueError("Escribe una función.")
    expr = sp.sympify(raw, locals=ALLOWED, evaluate=True)
    if expr.free_symbols - {x}:
        raise ValueError("Solo se admite la variable x.")
    if expr.has(sp.Function) and any(
        not isinstance(node, sp.Function) for node in []
    ):
        pass
    return expr

def fmt(value):
    try:
        return sp.sstr(sp.simplify(value))
    except Exception:
        return str(value)

def safe_float(value):
    try:
        v = complex(sp.N(value))
        if abs(v.imag) < 1e-8 and np.isfinite(v.real):
            return float(v.real)
    except Exception:
        pass
    return None

with st.sidebar:
    st.header("Configuración")
    raw = st.text_input("Función f(x)", value="x**3 - 3*x**2 + 2",
                        help="Ejemplos: x**2, sin(x), exp(x), log(x), sqrt(x)")
    operation = st.selectbox("Análisis", [
        "Análisis completo", "Derivadas", "Máximos y mínimos",
        "Integrales y acumulación", "Optimización en un intervalo"
    ])
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("Límite inferior / inicio", value=0.0, step=1.0)
    with col2:
        b = st.number_input("Límite superior / fin", value=3.0, step=1.0)
    st.caption("Los límites también definen el intervalo visible de la gráfica.")
    calculate = st.button("Calcular", type="primary", use_container_width=True)

st.info("Introduce expresiones como `x**3 - 3*x**2 + 2`. También admite `sin(x)`, `cos(x)`, `sqrt(x)`, `log(x)` y `exp(x)`. Las funciones trigonométricas usan radianes.")

if calculate:
    try:
        f = parse_function(raw)
        f1 = sp.diff(f, x)
        f2 = sp.diff(f1, x)
        st.subheader("Función analizada")
        st.latex(r"f(x) = " + sp.latex(f))

        show_all = operation == "Análisis completo"
        if show_all or operation == "Derivadas":
            st.subheader("Derivadas")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Primera derivada**")
                st.latex(r"f'(x) = " + sp.latex(f1))
            with c2:
                st.markdown("**Segunda derivada**")
                st.latex(r"f''(x) = " + sp.latex(f2))

        if show_all or operation == "Máximos y mínimos" or operation == "Optimización en un intervalo":
            st.subheader("Puntos críticos y extremos")
            try:
                critical = sp.solveset(sp.Eq(f1, 0), x, domain=sp.Interval(min(a,b), max(a,b)) if operation == "Optimización en un intervalo" else sp.S.Reals)
                candidates = []
                if isinstance(critical, sp.FiniteSet):
                    candidates = list(critical)
                elif isinstance(critical, sp.Union):
                    candidates = [v for part in critical.args if isinstance(part, sp.FiniteSet) for v in part]
                if operation == "Optimización en un intervalo":
                    candidates += [sp.Float(a), sp.Float(b)]
                rows = []
                for cp in candidates:
                    xv = safe_float(cp)
                    yv = safe_float(f.subs(x, cp))
                    if xv is None or yv is None:
                        continue
                    second = safe_float(f2.subs(x, cp))
                    if abs(xv-a) < 1e-7 or abs(xv-b) < 1e-7:
                        kind = "Extremo del intervalo"
                    elif second is not None and second > 1e-7:
                        kind = "Mínimo local (prueba de f'' )"
                    elif second is not None and second < -1e-7:
                        kind = "Máximo local (prueba de f'' )"
                    else:
                        kind = "Revisar: prueba de segunda derivada inconclusa"
                    rows.append({"x": round(xv, 6), "f(x)": round(yv, 6), "Clasificación": kind})
                if rows:
                    st.dataframe(rows, use_container_width=True, hide_index=True)
                    st.caption("La clasificación automática usa la segunda derivada como prueba cuando es concluyente. Para funciones con puntos singulares, extremos de frontera o casos degenerados, revisa el dominio y el comportamiento local.")
                else:
                    st.write("No se encontraron puntos críticos reales finitos en el intervalo o no se pudieron clasificar automáticamente.")
            except Exception as e:
                st.warning(f"No se pudieron determinar todos los puntos críticos simbólicamente: {e}")

        if show_all or operation == "Integrales y acumulación":
            st.subheader("Integrales")
            try:
                indefinite = sp.integrate(f, x)
                st.markdown("**Integral indefinida**")
                st.latex(r"\int f(x)\,dx = " + sp.latex(indefinite) + r" + C")
            except Exception:
                st.warning("No se encontró una antiderivada simbólica cerrada para esta función.")
            try:
                definite = sp.integrate(f, (x, a, b))
                st.markdown(f"**Integral definida de {a:g} a {b:g}**")
                st.latex(r"\int_{" + str(a) + "}^{" + str(b) + "} f(x)\,dx = " + sp.latex(definite))
                num = safe_float(definite)
                if num is not None:
                    st.metric("Valor numérico", f"{num:.8g}")
            except Exception:
                try:
                    fn = sp.lambdify(x, f, modules=["numpy"])
                    result, err = quad(lambda t: float(fn(t)), a, b, limit=200)
                    st.metric("Integral aproximada", f"{result:.8g}")
                    st.caption(f"Estimación del error numérico: {err:.2g}. Verifica que la función sea integrable en el intervalo.")
                except Exception as e:
                    st.warning(f"No fue posible calcular la integral en ese intervalo: {e}")

        st.subheader("Gráfica interactiva")
        lo, hi = min(a,b), max(a,b)
        if abs(hi-lo) < 1e-9:
            lo, hi = lo-5, hi+5
        xs = np.linspace(lo, hi, 700)
        fn = sp.lambdify(x, f, modules=["numpy"])
        with np.errstate(all="ignore"):
            ys = np.asarray(fn(xs))
            if ys.ndim == 0:
                ys = np.full_like(xs, float(ys))
            ys = np.asarray(ys, dtype=float)
        ys[~np.isfinite(ys)] = np.nan
        # Hide extreme values to keep useful scale while retaining discontinuities as gaps.
        ys[np.abs(ys) > 1e6] = np.nan
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)"))
        fig.update_layout(xaxis_title="x", yaxis_title="f(x)", template="plotly_white",
                          height=480, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Interpretación")
        st.write(f"La función ingresada es **f(x) = {sp.sstr(f)}**.")
        st.write("La primera derivada describe la tasa de cambio instantánea; la segunda derivada ayuda a estudiar la concavidad. La integral definida representa acumulación neta y el área con signo en el intervalo elegido.")
        if operation == "Optimización en un intervalo":
            st.write(f"Para optimizar en [{a:g}, {b:g}], se deben comparar los puntos críticos interiores con los extremos del intervalo.")
    except Exception as e:
        st.error(f"No se pudo interpretar la función: {e}")
        st.markdown("Comprueba la sintaxis. Ejemplos válidos: `x**2 + 3*x`, `sin(x)`, `sqrt(x)`, `log(x)`, `exp(-x**2)`.")
else:
    st.subheader("Prueba rápida")
    st.markdown("""
    - **Derivadas:** para `x**3 - 3*x**2 + 2`, la primera derivada es `3*x**2 - 6*x`.
    - **Integrales:** elige los límites y consulta la acumulación en ese intervalo.
    - **Máximos y mínimos:** encuentra puntos críticos reales y clasifica los casos concluyentes.
    - **Optimización:** compara puntos críticos y extremos del intervalo indicado.
    """)
    st.caption("Nota: las funciones matemáticas generales no siempre tienen soluciones simbólicas exactas. Los resultados numéricos y la clasificación automática deben interpretarse según el dominio y las condiciones del problema.")
