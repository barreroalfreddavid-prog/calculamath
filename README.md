# CalculaMath

Aplicación educativa web para derivadas, integrales, puntos críticos, optimización en intervalos y gráficas.

## Ejecutar en tu computador

1. Instala Python 3.10 o posterior.
2. Abre una terminal dentro de esta carpeta.
3. Instala las dependencias:

   `pip install -r requirements.txt`

4. Ejecuta la página:

   `streamlit run app.py`

Se abrirá en el navegador.

## Publicarla en internet

Puedes subir `app.py` y `requirements.txt` a un repositorio de GitHub y desplegarlo desde Streamlit Community Cloud.

## Sintaxis de las funciones

- Potencias: `x**3`
- Multiplicación: `3*x`
- Raíz: `sqrt(x)`
- Exponencial: `exp(x)`
- Logaritmo natural: `log(x)`
- Trigonometría: `sin(x)`, `cos(x)`, `tan(x)` (radianes)

## Alcance

La aplicación intenta cálculos simbólicos con SymPy y utiliza integración numérica como alternativa para algunas integrales. No puede prometer solución exacta para toda función posible. Revisa el dominio, singularidades y supuestos de los problemas reales de optimización. No introduzcas código ni expresiones no confiables en una instalación pública sin reforzar la validación.
