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
    Aqui é possível visualizar e adicionar vendas em tempo real.
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
                    SELECT log_vendas.acao, log_vendas.detalhe, venda.data_venda, 
                    venda.valor_total, venda.desconto, venda.meio_compra
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
                    SELECT produto.id_produto, produto.nome_produto, produto.descricao, produto.preco_venda
                    FROM produto;
                """)
                dados = cur.fetchall()
                lista_produtos = dados
                return lista_produtos 
    except Exception as e:
        st.error(f"Erro ao consultar produtos: {e}")
        return pd.DataFrame()

def carregar_id_venda():
    """Carrega os produtos do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_venda
                    FROM venda;
                """)
                dados = cur.fetchall()
                lista_produtos = dados
                return lista_produtos 
    except Exception as e:
        st.error(f"Erro ao consultar produtos: {e}")
        return pd.DataFrame()

def adicionar_venda(nome_completo, produto, preco_unitario, quantidade, id_cliente, observacoes, meio_compra, total, acao):
    """Adiciona uma venda no banco Neon"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO venda
                    (id_venda, id_cliente, valor_final, valor_total, meio_compra, observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s);

                    INSERT INTO item_venda 
                    (id_venda, id_produto, quantidade, preco_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    id_venda,
                    id_cliente,
                    total,
                    total,
                    meio_compra,
                    observacoes,
                    id_venda,
                    id_produto,
                    quantidade,
                    preco_unitario,
                    total,
                ))
                conn.commit()
                return True
    except psycopg2.Error as e:
        st.error(f"Erro ao adicionar venda: {e}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return False

# --80----------------------------------------------------------
# ➕ Formulário para adicionar um novo cliente
# ------------------------------------------------------------
st.header("Adicionar uma nova venda")
lista_clientes = carregar_clientes()
lista_produtos = carregar_produtos()
df_id_venda = carregar_id_venda()
with st.form("add_venda"):
    nome_completo = st.selectbox("Nome completo", [entry['nome_completo'] for entry in lista_clientes])
    produto = st.selectbox("Produto", [entry['nome_produto'] for entry in lista_produtos])
    preco_unitario = float(
        next(
            (p['preco_venda'] for p in lista_produtos if p['nome_produto'] == produto),
            0
        )   
    )
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    id_cliente = next((p['id_cliente'] for p in lista_clientes if p['nome_completo'] == nome_completo),0)   
    id_produto = next((p['id_produto'] for p in lista_produtos if p['nome_produto'] == produto),0)   
    observacoes = st.text_input("Observações") 
    meio_compra = st.selectbox("Meio de compra", ["PIX", "Crédito", "Débito", "Dinheiro"])
    total = preco_unitario * quantidade
    submitted = st.form_submit_button("Cadastrar venda")

# Processa o cadastro
if submitted:
    if nome_completo and produto and quantidade and meio_compra:
        st.write(f"O seu total é de R$ {total}")
        id_venda = len(df_id_venda) + 1
        acao = "VENDA_CRIADA"
        sucesso = adicionar_venda(nome_completo, produto, preco_unitario, quantidade, id_cliente, observacoes, meio_compra, total, acao)
        if sucesso:
            st.success(f"Venda para {nome_completo} cadastrada com sucesso!")
    else:
        st.error("Preencha pelo menos o nome do cliente, produto, quantidade e meio de compra para cadastrar.")

# ------------------------------------------------------------
# 📋 Mostrar todos os clientes
# ------------------------------------------------------------
st.header("Vendas cadastrados")
df_vendas = carregar_vendas()

if df_vendas.empty:
    st.info("Nenhuma venda cadastrada ainda.")
else:
    st.dataframe(df_vendas, use_container_width=True, hide_index=True)
