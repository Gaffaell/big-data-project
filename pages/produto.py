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
st.set_page_config(page_title="Produtos", page_icon="🎫")
st.title("👤 Gerenciador de Produtos")
st.write(
    """
    Este aplicativo é um gerenciador de Produtos conectado ao banco de dados Neon.
    Aqui é possível visualizar e adicionar produtos em tempo real.
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
def carregar_produtos():
    """Carrega os podutos do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_produto, nome_produto, descricao, preco_venda, preco_compra, percentual_lucro,
                    criado_em
                    FROM produto 
                    ORDER BY id_produto DESC;
                """)
                dados = cur.fetchall()
                df = pd.DataFrame(dados)
                return df
    except Exception as e:
        st.error(f"Erro ao consultar produtos: {e}")
        return pd.DataFrame()

def adicionar_produto(nome_produto, descricao, preco_venda, preco_compra):
    """Adiciona um produto no banco Neon"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO produto
                    (nome_produto, descricao, preco_venda, preco_compra, criado_em)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    nome_produto, 
                    descricao, 
                    preco_venda, 
                    preco_compra, 
                    datetime.datetime.now(), 
                ))
                conn.commit()
                return True
    except psycopg2.Error as e:
        st.error(f"Erro ao adicionar produto: {e}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return False

# ------------------------------------------------------------
# ➕ Formulário para adicionar um novo produto
# ------------------------------------------------------------
st.header("Adicionar um novo produto")
with st.form("id_produto"):
    nome_produto = st.text_input("Nome produto", placeholder="Ex: Ração premium de gato")
    descricao = st.text_input("Descricao", placeholder="Ex: Ração seca completa para gato adulto")
    preco_venda = st.number_input("Preço de venda")
    preco_compra = st.number_input("Preço de compra")
    submitted = st.form_submit_button("Cadastrar produto")

# Processa o cadastro
if submitted:
    if nome_produto and preco_venda:
        sucesso = adicionar_produto(nome_produto, descricao, preco_venda, preco_compra)
        if sucesso:
            st.success(f"Produto {nome_produto} cadastrado com sucesso!")
    else:
        st.error("Preencha pelo menos Nome e Preço de venda para cadastrar.")

# ------------------------------------------------------------
# 📋 Mostrar todos os produtos 
# ------------------------------------------------------------
st.header("Produtos cadastrados")
df_produtos = carregar_produtos()

if df_produtos.empty:
    st.info("Nenhum produto cadastrado ainda.")
else:
    st.dataframe(df_produtos, use_container_width=True, hide_index=True)
