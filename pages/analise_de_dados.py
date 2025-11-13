from re import error
from typing_extensions import Writer
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
                    SELECT nome_completo, qtd_compras, total_gasto
                    FROM vw_clientes_frequentes
                    order BY qtd_compras;
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

def carregar_produtos_mais_vendidos():
    """Carrega os produtos mais vendidos"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                SELECT nome_produto, total_vendido, receita_total
                FROM vw_produtos_mais_vendidos
                ORDER BY total_vendido;
                """)
                dados = cur.fetchall()
                df = pd.DataFrame(dados)
                return df
    except Exception as e:
        st.error(f"Erro ao consultar os produtos mais vendidos: {e}")
        return pd.DataFrame()

def carregar_categorias_mais_vendidas ():
    """Carrega categorias mais vendidos"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                SELECT categoria, num_vendas, total_itens_vendidos, receita_total
                FROM vw_vendas_por_categoria
                ORDER BY num_vendas;
                """)
                dados = cur.fetchall()
                df = pd.DataFrame(dados)
                return df
    except Exception as e:
        st.error(f"Erro ao consultar as categorias mais vendidas: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------
# ⚙️Visualização de dados e gráficos (otimizado)
# ------------------------------------------------------------
st.title("# Análise de dados de estoque")
st.write("Esta seção apresenta um resumo visual do estoque atual.")

df_estoque = carregar_estoque()

# --- Criação dos gráficos ---
categoria_plot = (
    alt.Chart(df_estoque)
    .mark_bar()
    .encode(
        x="categoria:O",
        y="count():Q",
        color="categoria:N"
    )
    .properties(width=300, height=300)
)

tipo_animal_plot = (
    alt.Chart(df_estoque)
    .mark_arc()
    .encode(
        theta="count():Q",
        color="tipo_animal:N"
    )
    .properties(width=250, height=300)
)

# --- Exibição lado a lado ---
col1, col2 = st.columns(2)
with col1:
    st.write("Quantidade de produtos por categoria")
    st.altair_chart(categoria_plot, use_container_width=False, theme="streamlit")

with col2:
    st.write("Distribuição por tipo de animal")
    st.altair_chart(tipo_animal_plot, use_container_width=False, theme="streamlit")


# ------------------------------------------------------------
# Clientes
# ------------------------------------------------------------
st.title("# Análise de dados de clientes")
df_cliente = carregar_clientes()

clientes_frequentes_plot = (
    alt.Chart(df_cliente)
    .mark_bar()
    .encode(
        x="nome_completo:O",
        y="qtd_compras:Q",
        color="nome_completo:N"
    )
    .properties(width=400, height=300)
)

clientes_total_gasto_plot = (
    alt.Chart(df_cliente)
    .mark_bar()
    .encode(
        x="nome_completo:O",
        y="total_gasto:Q",
        color="nome_completo:N"
    )
    .properties(width=400, height=300)
)

col1, col2 = st.columns(2)
with col1:
    st.write("Proporção de clientes mais frequentes")
    st.altair_chart(clientes_frequentes_plot, use_container_width=False, theme="streamlit")

with col1:
    st.write("Proporção de gasto total de cada cliente")
    st.altair_chart(clientes_total_gasto_plot, use_container_width=False, theme="streamlit")

# ------------------------------------------------------------
# Vendas
# ------------------------------------------------------------
st.title("# Análise de dados de vendas")
df_venda = carregar_vendas()

meio_compra_plot = (
    alt.Chart(df_venda)
    .mark_arc()
    .encode(
        theta="count():Q",
        color="meio_compra:N"
    )
    .properties(width=300, height=300)
)

linha_vendas_plot = (
    alt.Chart(df_venda)
    .mark_line(point=True)
    .encode(
        x="data_venda:T",
        y="valor_total:Q"
    )
    .properties(width=400, height=300)
)

df_produtos_mais_vendidos = carregar_produtos_mais_vendidos()
produtos_mais_vendidos_plot = (
    alt.Chart(df_produtos_mais_vendidos)
    .mark_bar()
    .encode(
        x="nome_produto:O",
        y="total_vendido:Q",
        color="nome_produto:N"
    )
    .properties(width=400, height=300)
)

produtos_maior_receita_plot = (
    alt.Chart(df_produtos_mais_vendidos)
    .mark_bar()
    .encode(
        x="nome_produto:O",
        y="receita_total:Q",
        color="nome_produto:N"
    )
    .properties(width=400, height=300)
)

df_categorias_mais_vendidas = carregar_categorias_mais_vendidas()
categorias_mais_vendidas_plot = (
    alt.Chart(df_categorias_mais_vendidas)
    .mark_bar()
    .encode(
        x="categoria:O",
        y="total_itens_vendidos:Q",
        color="categoria:N"
    )
    .properties(width=400, height=300)
)

col1, col2 = st.columns(2)
with col1:
    st.write("Meio de compra mais utilizado")
    st.altair_chart(meio_compra_plot, use_container_width=False, theme="streamlit")

with col2:
    st.write("Valores das vendas ao longo do tempo")
    st.altair_chart(linha_vendas_plot, use_container_width=False, theme="streamlit")

col1, col2 = st.columns(2)
with col1:
    st.write("Produtos mais vendidos")
    st.altair_chart(produtos_mais_vendidos_plot, use_container_width=False, theme="streamlit")

with col2:
    st.write("Produtos com maior receita total")
    st.altair_chart(produtos_maior_receita_plot, use_container_width=False, theme="streamlit")

col1, col2 = st.columns(2)
with col1:
    st.write("Categorias mais vendidas")
    st.altair_chart(categorias_mais_vendidas_plot, use_container_width=False, theme="streamlit")
