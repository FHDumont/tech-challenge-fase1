import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
import os

# Obtém o hostname da API do ambiente
API_HOST = os.getenv("API_HOST", "http://localhost:8000")  # Fallback para localhost

st.title("Books Scraper Dashboard")
st.subheader("Press R for content refresh")


# Função para carregar os dados com cache e atualização periódica
@st.cache_data(ttl=30)  # Recarrega a cada 60 segundos
def load_data(_timestamp):
    """
    Carrega os dados do CSV com cache de 60 segundos.
    O parâmetro _timestamp força a recarga periódica.
    """
    try:
        df = pd.read_csv(
            "data/books.csv",
            dtype={"id": int, "title": str, "href": str, "price": float, "rating": int, "availability": str, "category": str, "image_url": str},
        )
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o CSV: {str(e)}")
        return pd.DataFrame()


# Força a recarga periódica usando o timestamp atual
df = load_data(time.time())

# Total de livros
st.metric("Total de Livros", len(df))

# Preço médio
st.metric("Preço Médio", f"£{df['price'].mean():.2f}" if not df.empty else "£0.00")

# Distribuição de ratings
fig = px.histogram(df, x="rating", title="Distribuição de Ratings")
st.plotly_chart(fig)

# Livros por categoria
fig = px.histogram(df, x="category", title="Livros por Categoria")
st.plotly_chart(fig)

# Top 5 livros mais caros
st.subheader("Top 5 Livros Mais Caros")
st.dataframe(df.nlargest(5, "price")[["title", "price", "category"]] if not df.empty else pd.DataFrame())

# Consulta à API para status
try:
    response = requests.get(f"{API_HOST}/api/v1/health", timeout=5)
    health = response.json()
    st.metric("API Status", health["api_status"])
    st.metric("Dados Carregados", str(health["data_loaded"]))
except Exception as e:
    st.error("Erro ao conectar à API")
