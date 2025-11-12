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
#if "authenticated" not in st.session_state or not st.session_state.authenticated:
#    st.warning("Você precisa fazer o login para acessar esta página!")
#    st.stop()

# ------------------------------------------------------------
# ⚙️ Configuração da página
# ------------------------------------------------------------
st.set_page_config(page_title="Analise de dados", page_icon="🎫")
st.title("👤 Analise de dados")
st.write(
    """
    Esta página é dediacada à analise de dados.
    Aqui é possível visualizar e analisar dados pertinentes ao negócio em tempo real.
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
                df = pd.DataFrame(dados)
                return df
    except Exception as e:
        st.error(f"Erro ao consultar estoque: {e}")
        return pd.DataFrame()

def carregar_clientes():
    """Carrega os clientes do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_cliente, cliente_ativo, criado_em, cpf, cep, endereco,
                           complemento, numero, nome_completo, email
                    FROM cliente
                    ORDER BY id_cliente DESC;
                """)
                dados = cur.fetchall()
                df = pd.DataFrame(dados)
                return df
    except Exception as e:
        st.error(f"Erro ao consultar clientes: {e}")
        return pd.DataFrame()

def carregar_vendas():
    """Carrega as vendas do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT log_vendas.acao, log_vendas.detalhe, venda.data_venda, venda.valor_total, venda.meio_compra
                    FROM log_vendas
                    JOIN venda on log_vendas.id_venda = venda.id_venda
                    ORDER BY id_log DESC;
                """)
                dados = cur.fetchall()
                df = pd.DataFrame(dados)
                return df
    except Exception as e:
        st.error(f"Erro ao consultar vendas: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------
# ⚙️Visualização de dados e gráficos
# ------------------------------------------------------------
# Show two Altair charts using st.altair_chart.
st.title("# Analise de dados de estoque")

st.write("")
st.write("")
st.write("* Quantidade de produtos de cada categoria")
df_estoque = carregar_estoque()
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

# Dados de clientes
st.title("# Analse de dados de clientes")
st.write("")
st.write("")
st.write("* Quantidade de clientes ativos")
df_cliente = carregar_clientes()
tipo_animal_plot = (
    alt.Chart(df_cliente)
    .mark_arc()
    .encode(
        theta="count():Q", 
        color="cliente_ativo:O"
    )
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(tipo_animal_plot, use_container_width=True, theme="streamlit")

# Dados de venda
st.title("# Analise de dados de vendas")

st.write("")
st.write("")
st.write("* Meio de compra mais utilizado")
df_venda = carregar_vendas()
categoria_plot = (
    alt.Chart(df_venda)
    .mark_bar()
    .encode(
        x="meio_compra:O",
        y="count():Q",
        #xOffset="Status:N",
        color="meio_compra:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(categoria_plot, use_container_width=True, theme="streamlit")

st.write("* Valores de cada venda em um certo período")
tipo_animal_plot = (
    alt.Chart(df_venda)
    .mark_line()
    .encode(
        x="data_venda", 
        y="valor_total"
    )
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(tipo_animal_plot, use_container_width=True, theme="streamlit")
