# Bienvenidos al Detector de Noticias Falsas

Análisis y clasificación de noticias usando Python, Pandas, Scikit-learn, Matplotlib y Streamlit.

## Descripción

Este proyecto carga un dataset de noticias y lo limpia para facilitar su análisis y clasificación.  
Después, entrena un modelo de aprendizaje automático usando *TF-IDF* y *SGDClassifier* para diferenciar noticias *REALES* y *FALSAS*.  
Además, permite hacer predicciones individuales desde una interfaz en *Streamlit* o clasificar varias noticias a la vez mediante un archivo CSV.  
Por último, genera un HTML donde se pueden comprobar métricas del modelo, errores de clasificación, tablas y gráficos.

## Funcionalidades

- Carga de datos desde un archivo CSV.
- Limpieza del texto para eliminar metadatos, fuentes y restos de scraping.
- Vectorización del contenido con TF-IDF.
- Entrenamiento de un clasificador SGD para distinguir noticias reales y falsas.
- Evaluación del modelo con accuracy, confusion matrix y classification report.
- Generación de un gráfico con la distribución de noticias reales y falsas.
- Exportación de un informe HTML con resultados y ejemplos clasificados.
- Guardado del vectorizador y del modelo entrenado en archivos `.pkl`.
- Predicción de una sola noticia desde la app de Streamlit.
- Predicción por lotes desde un CSV subido por el usuario.

## Tecnologías utilizadas

- Python
- Pandas
- Matplotlib
- Scikit-learn
- Joblib
- Jinja2
- Streamlit

## Archivos principales

- `train_model.py`: entrena el modelo, evalúa resultados y guarda los archivos del clasificador.
- `app.py`: interfaz web en Streamlit para hacer predicciones individuales o por CSV.
- `fake_or_real_news.csv`: dataset principal de entrenamiento.
- `vectorizer.pkl`: vectorizador TF-IDF entrenado.
- `classifier.pkl`: modelo entrenado.
- `news_report.html`: informe HTML generado automáticamente.

## Ejecución

```bash
python fake_news_detector.py
streamlit run predict_news.py
```

---

# Welcome to the Fake News Detector

News analysis and classification using Python, Pandas, Scikit-learn, Matplotlib, and Streamlit.

## Description

This project loads a news dataset and cleans it to make analysis and classification easier.  
It then trains a machine learning model using *TF-IDF* and *SGDClassifier* to distinguish *REAL* and *FAKE* news articles.  
In addition, it allows single predictions through a *Streamlit* interface or batch predictions using a CSV file.  
Finally, it generates an HTML report where model metrics, classification errors, tables, and charts can be reviewed.

## Features

- Loading data from a CSV file.
- Cleaning text to remove metadata, agency prefixes, and scraping leftovers.
- Vectorizing article content with TF-IDF.
- Training an SGD classifier to separate fake and real news.
- Evaluating the model with accuracy, confusion matrix, and classification report.
- Generating a chart showing the distribution of fake and real news.
- Exporting an HTML report with results and classified examples.
- Saving the trained vectorizer and classifier as `.pkl` files.
- Predicting a single article from the Streamlit app.
- Predicting multiple articles from an uploaded CSV file.

## Technologies Used

- Python
- Pandas
- Matplotlib
- Scikit-learn
- Joblib
- Jinja2
- Streamlit

## Main Files

- `train_model.py`: trains the model, evaluates results, and saves the classifier files.
- `app.py`: Streamlit web app for single and batch predictions.
- `fake_or_real_news.csv`: main training dataset.
- `vectorizer.pkl`: trained TF-IDF vectorizer.
- `classifier.pkl`: trained classification model.
- `news_report.html`: automatically generated HTML report.

## Run

```bash
python fake_news_detector.py
streamlit run predict_news.py
```