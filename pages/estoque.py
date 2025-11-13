import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import altair as alt
from contextlib import contextmanager

# ------------------------------------------------------------
# 🔐 Verificação de login
# ------------------------------------------------------------
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa fazer o login para acessar esta página!")
    st.stop()

# ------------------------------------------------------------
# ⚙️ Configuração da página
# ------------------------------------------------------------
st.set_page_config(page_title="Estoque", page_icon="🎫")
st.title("👤 Analise de estoque cadastrado")
st.write(
    """
    Esta página é dedicada a mostrar o estoque cadastrado
    """
)

# ------------------------------------------------------------
# 🌐 Conexão com o banco de dados Neon PostgreSQL
# ------------------------------------------------------------
@contextmanager
def get_db_connection():
    """Context manager para gerenciar conexões com o banco"""
    conn = None
    try:
        conn = psycopg2.connect(
            host="ep-frosty-pond-a4wvle05-pooler.us-east-1.aws.neon.tech",
            dbname="neondb",
            user="neondb_owner",
            password="npg_4kcBT1iJmsgw",
            port="5432",
            sslmode="require",
            cursor_factory=RealDictCursor,
            connect_timeout=10
        )
        yield conn
    except psycopg2.Error as e:
        st.error(f"Erro na conexão com o banco de dados: {e}")
        raise
    finally:
        if conn:
            conn.close()

# ------------------------------------------------------------
# 📦 Funções auxiliares
# ------------------------------------------------------------
def carregar_estoque():
    """Carrega o estoque do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_estoque, categoria, subcategoria, tipo_animal, porte, faixa_etaria, quantidade,
                           data_atualizacao
                    FROM estoque 
                    ORDER BY id_estoque DESC;
                """)
                dados = cur.fetchall()
                df_estoque = pd.DataFrame(dados)
                return df_estoque
    except Exception as e:
        st.error(f"Erro ao consultar estoque: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------
# 📋 Mostrar todos os clientes
# ------------------------------------------------------------
st.header("Estoque cadastrado")
df_estoque = carregar_estoque()

if df_estoque.empty:
    st.info("Nenhum estoque cadastrado ainda.")
else:
    st.dataframe(df_estoque, use_container_width=True, hide_index=True)


# ------------------------------------------------------------
# parte para mostrar grafico e estatisticas
# ------------------------------------------------------------

st.header("Analise de dados e gráficos")

# Show two Altair charts using st.altair_chart.
st.write("")
st.write("")
st.write("* Quantidade de produtos cada categoria")
categoria_plot = (
    alt.Chart(df_estoque)
    .mark_bar()
    .encode(
        x="categoria:O",
        y="count():Q",
        #xOffset="Status:N",
        color="categoria:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(categoria_plot, use_container_width=True, theme="streamlit")

st.write("* Quantidade de produtos de cada tipo de animal")
tipo_animal_plot = (
    alt.Chart(df_estoque)
    .mark_arc()
    .encode(
        theta="count():Q", 
        color="tipo_animal:O"
    )
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(tipo_animal_plot, use_container_width=True, theme="streamlit")
