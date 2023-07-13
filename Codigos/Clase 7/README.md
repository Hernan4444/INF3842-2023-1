# Ejemplo Streamlit

El código de este directorio está pensado para enseñar las funcionalidades básicas de Streamlit de
acuerdo a lo mostrado en clases. En particular, usaremos un dataset de viajes en bicicletas compartidas
de la aplicación Divvy en la ciudad de Chicago en abril de 2020. Los datos fueron obtenidos de [aquí](https://divvy-tripdata.s3.amazonaws.com/index.html)

## Estructura de archivos

1. `202004-divvy-tripdata_clean.csv`: dataset para desarrollar el dashboard.
2. `app_final.py`: código final del dashboard.
3. `app_class.py`: plantilla para construir el dashboard desde cero en clases.
4. `requirements.txt`: librerías de Python necesarias para construir el dashboard.

## Cómo ejecutar
1. Instalar librerías: `pip install -r requirements.txt`.
2. Ejecutar: `streamlit run app_class.py`