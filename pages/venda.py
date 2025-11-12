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
st.set_page_config(page_title="Vendas", page_icon="🎫")
st.title("👤 Gerenciador de vendas")
st.write(
    """
    Esta página é um gerenciador de vendas.
    Aqui é possível visualizar, adicionar e analisar as vendas em tempo real.
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

def carregar_clientes():
    """Carrega os clientes do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_cliente, nome_completo
                    FROM cliente
                    order by cliente desc;
                """)
                dados = cur.fetchall()
                lista_clientes = dados
                return lista_clientes 
    except Exception as e:
        st.error(f"Erro ao consultar clientes: {e}")
        return pd.DataFrame()

def carregar_produtos():
    """Carrega os produtos do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_produto, nome_produto, descricao, preco_venda
                    FROM produto 
                    order by produto desc;
                """)
                dados = cur.fetchall()
                lista_produtos = dados
                return lista_produtos 
    except Exception as e:
        st.error(f"Erro ao consultar produtos: {e}")
        return pd.DataFrame()

def adicionar_venda(quantidade, valor_unitario, subtotal):
    """Adiciona uma venda no banco Neon"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO item_venda 
                    (id_produto, quantidade, valor_unitario, subtotal)
                    VALUES (%s, %s, %s, %s);

                    INSERT INTO venda
                    (id_cliente, data_venda, valor_total)
                    VALUES (%s, %s, %s);
                """, (
                    quantidade, 
                    valor_unitario, 
                    subtotal, 
                    datetime.datetime.now(), 
                    True
                ))
                conn.commit()
                return True
    except psycopg2.Error as e:
        st.error(f"Erro ao adicionar venda: {e}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return False

# ------------------------------------------------------------
# ➕ Formulário para adicionar um novo cliente
# ------------------------------------------------------------
st.header("Adicionar uma nova venda")
lista_clientes = carregar_clientes()
lista_produtos = carregar_produtos()
with st.form("add_venda"):
    nome_completo = st.selectbox("Nome completo", [entry['nome_completo'] for entry in lista_clientes])
    produto = st.selectbox("produto", [entry['nome_produto'] for entry in lista_produtos])
    submitted = st.form_submit_button("Cadastrar venda")

# Processa o cadastro
if submitted:
    if nome_completo and produto:
        sucesso = adicionar_venda(nome_completo, produto, email, cep, endereco, complemento, numero)
        if sucesso:
            st.success(f"Cliente {nome_completo} cadastrado com sucesso!")
    else:
        st.error("Preencha pelo menos Nome, CPF e Email para cadastrar.")

# ------------------------------------------------------------
# 📋 Mostrar todos os clientes
# ------------------------------------------------------------
st.header("Vendas cadastrados")
df_vendas = carregar_vendas()

if df_vendas.empty:
    st.info("Nenhuma venda cadastrada ainda.")
else:
    st.dataframe(df_vendas, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# 📊 Gráficos e estatísticas
# ------------------------------------------------------------
#   st.header("Análise de dados e gráficos")
#   if not df_clientes.empty:
#       st.write("Distribuição de nomes de clientes:")
#       chart_nome = (
#           alt.Chart(df_clientes)
#           .mark_arc()
#           .encode(
#               theta="count():Q",
#               color="nome_completo:N"
#           )
#           .properties(height=300)
#       )
#       st.altair_chart(chart_nome, use_container_width=True)
#
