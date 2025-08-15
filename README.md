# Algoritmic Trading: Actividades y Ejercicios de Backtesting

Este proyecto está orientado a la práctica y aprendizaje de técnicas de backtesting y la implementación de estrategias financieras usando Python. Incluye notebooks, scripts y diagramas de actividades en formato PlantUML (.puml) para documentar y visualizar la lógica de las estrategias.

## Características
- Ejercicios prácticos de backtesting con datos reales y simulados.
- Implementación de estrategias de trading personalizadas.
- Visualización de resultados y análisis de desempeño.
- Diagramas de actividades en PlantUML para documentar la lógica de las estrategias.

## Estructura del proyecto
- `code/` : Notebooks y scripts de backtesting y estrategias.
- `data/` : Archivos de datos históricos para pruebas.
- `docs/` : Diagramas de actividades (.puml) y documentación adicional.

## Dependencias principales
El proyecto utiliza las siguientes librerías (ver `pyproject.toml`):

- backtrader (>=1.9.78.123,<2.0.0.0)
- matplotlib (>=3.10.5,<4.0.0)
- pandas (>=2.3.1,<3.0.0)
- vectorbt (>=0.28.0,<0.29.0)
- yfinance (>=0.2.65,<0.3.0)
- fmp-python (>=0.1.5,<0.2.0)

## Instalación

1. Clona este repositorio.
2. Instala las dependencias usando Poetry:

```bash
poetry install
```

O usando pip (si no usas Poetry):

```bash
pip install -r requirements.txt
```

## Uso

- Ejecuta los notebooks en la carpeta `code/` para explorar y modificar las estrategias.
- Los diagramas de actividades en `docs/` pueden visualizarse con cualquier visor compatible con PlantUML.
- Modifica o crea tus propias estrategias y experimenta con diferentes parámetros y datos.

## Ejercicios sugeridos
- Implementa una estrategia de cruce de medias móviles y analiza su desempeño.
- Modifica una estrategia para incluir gestión de riesgo y stop-loss.
- Documenta tu estrategia con un diagrama de actividades en PlantUML.
- Compara resultados entre diferentes activos y timeframes.

## Créditos
Autor: Jiliar Silgado

---
¡Explora, aprende y experimenta con el backtesting de estrategias financieras en Python!
