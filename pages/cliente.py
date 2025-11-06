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
st.set_page_config(page_title="Gerenciador de clientes", page_icon="🎫")
st.title("👤 Gerenciador de clientes")
st.write(
    """
    Este aplicativo é um gerenciador de perfis de clientes.
    Aqui é possível visualizar, adicionar e analisar clientes em tempo real.
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

def adicionar_cliente(nome_completo, cpf, email, cep, endereco, complemento, numero):
    """Adiciona um cliente no banco Neon"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO cliente 
                    (nome_completo, cpf, email, cep, endereco, complemento, numero, criado_em, cliente_ativo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    nome_completo, 
                    cpf, 
                    email, 
                    cep, 
                    endereco, 
                    complemento, 
                    numero, 
                    datetime.datetime.now(), 
                    True
                ))
                conn.commit()
                return True
    except psycopg2.Error as e:
        st.error(f"Erro ao adicionar cliente: {e}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return False

# ------------------------------------------------------------
# ➕ Formulário para adicionar um novo cliente
# ------------------------------------------------------------
st.header("Adicionar um novo cliente")
st.write("Não use . ou - nos campos CPF e CEP")
with st.form("add_cliente"):
    nome_completo = st.text_input("Nome completo", placeholder="Ex: João Paulo Costa")
    cpf = st.text_input("CPF", placeholder="Ex: 12345678910")
    email = st.text_input("Email", placeholder="Ex: cliente@gmail.com")
    cep = st.text_input("CEP", placeholder="12345678")
    endereco = st.text_input("Endereço", placeholder="Ex: Travessa Júlio César")
    complemento = st.text_input("Complemento", placeholder="Ex: Ap 101")
    numero = st.text_input("Número", placeholder="Ex: 78B")
    submitted = st.form_submit_button("Cadastrar cliente")

# Processa o cadastro
if submitted:
    if nome_completo and cpf and email:
        sucesso = adicionar_cliente(nome_completo, cpf, email, cep, endereco, complemento, numero)
        if sucesso:
            st.success(f"Cliente {nome_completo} cadastrado com sucesso!")
    else:
        st.error("Preencha pelo menos Nome, CPF e Email para cadastrar.")

# ------------------------------------------------------------
# 📋 Mostrar todos os clientes
# ------------------------------------------------------------
st.header("Clientes cadastrados")
df_clientes = carregar_clientes()

if df_clientes.empty:
    st.info("Nenhum cliente cadastrado ainda.")
else:
    st.dataframe(df_clientes, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# 📊 Gráficos e estatísticas
# ------------------------------------------------------------
st.header("Análise de dados e gráficos")
if not df_clientes.empty:
    st.write("Distribuição de nomes de clientes:")
    chart_nome = (
        alt.Chart(df_clientes)
        .mark_arc()
        .encode(
            theta="count():Q",
            color="nome_completo:N"
        )
        .properties(height=300)
    )
    st.altair_chart(chart_nome, use_container_width=True)
