import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import plotly.express as px
import plotly.graph_objects as go
from contextlib import contextmanager
import numpy as np

# ------------------------------------------------------------
# 🔐 Verificação de login
# ------------------------------------------------------------
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa fazer o login para acessar esta página!")
    st.stop()

# ------------------------------------------------------------
# ⚙️ Configuração da página
# ------------------------------------------------------------
st.set_page_config(
    page_title="Análise de Dados - Pet Shop",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        font-weight: 600;
        color: #f0f0f0 !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 14px;
        color: #e0e0e0 !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

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
        st.error(f"❌ Erro na conexão com o banco de dados: {e}")
        raise
    finally:
        if conn:
            conn.close()

# ------------------------------------------------------------
# 📦 Funções auxiliares
# ------------------------------------------------------------
@st.cache_data(ttl=300)
def carregar_estoque():
    """Carrega o estoque do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_estoque, categoria, subcategoria, tipo_animal, porte, 
                           faixa_etaria, quantidade, data_atualizacao
                    FROM estoque 
                    ORDER BY id_estoque DESC;
                """)
                dados = cur.fetchall()
                if dados:
                    df = pd.DataFrame(dados)
                    if 'data_atualizacao' in df.columns:
                        df['data_atualizacao'] = pd.to_datetime(df['data_atualizacao'])
                    return df
                return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao consultar estoque: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
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
                if dados:
                    df = pd.DataFrame(dados)
                    if 'criado_em' in df.columns:
                        df['criado_em'] = pd.to_datetime(df['criado_em'])
                    return df
                return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao consultar clientes: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def carregar_clientes_frequentes():
    """Carrega os clientes mais frequentes"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT nome_completo, qtd_compras, total_gasto
                    FROM vw_clientes_frequentes
                    ORDER BY qtd_compras DESC;
                """)
                dados = cur.fetchall()
                if dados:
                    df = pd.DataFrame(dados)
                    # Converter Decimal para float
                    if 'total_gasto' in df.columns:
                        df['total_gasto'] = df['total_gasto'].astype(float)
                    return df
                return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao consultar clientes frequentes: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def carregar_vendas():
    """Carrega as vendas do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT log_vendas.acao, log_vendas.detalhe, log_vendas.data_hora,
                           venda.data_venda, venda.valor_total, venda.meio_compra
                    FROM log_vendas
                    JOIN venda ON log_vendas.id_venda = venda.id_venda
                    ORDER BY log_vendas.id_log DESC;
                """)
                dados = cur.fetchall()
                if dados:
                    df = pd.DataFrame(dados)
                    if 'data_venda' in df.columns:
                        df['data_venda'] = pd.to_datetime(df['data_venda'])
                    if 'data_hora' in df.columns:
                        df['data_hora'] = pd.to_datetime(df['data_hora'])
                    # Converter Decimal para float
                    if 'valor_total' in df.columns:
                        df['valor_total'] = df['valor_total'].astype(float)
                    return df
                return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao consultar vendas: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def carregar_produtos_mais_vendidos():
    """Carrega os produtos mais vendidos"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT nome_produto, total_vendido
                    FROM vw_produtos_mais_vendidos
                    ORDER BY total_vendido DESC;
                """)
                dados = cur.fetchall()
                if dados:
                    return pd.DataFrame(dados)
                return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao consultar produtos mais vendidos: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def carregar_validade():
    """Carrega os dados de controle de validade do banco Neon em um DataFrame"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id_validade,
                        id_produto,
                        nome_produto,
                        categoria,
                        marca,
                        lote,
                        data_fabricacao,
                        data_validade,
                        quantidade_lote,
                        quantidade_disponivel,
                        fornecedor,
                        observacoes,
                        dias_para_vencer,
                        status_validade,
                        criticidade
                    FROM vw_produtos_validade
                    ORDER BY data_validade ASC;
                """)
                dados = cur.fetchall()
                if dados:
                    df = pd.DataFrame(dados)
                    # Converter colunas de data
                    if 'data_fabricacao' in df.columns:
                        df['data_fabricacao'] = pd.to_datetime(df['data_fabricacao'])
                    if 'data_validade' in df.columns:
                        df['data_validade'] = pd.to_datetime(df['data_validade'])
                    return df
                return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao consultar controle de validade: {e}")
        return pd.DataFrame()


# ------------------------------------------------------------
# 📊 Header e Título
# ------------------------------------------------------------
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    st.title("📊 Dashboard de Análise - Pet Shop")
    st.markdown("**Análise completa de vendas, clientes e estoque em tempo real**")
with col_header2:
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ------------------------------------------------------------
# 📅 Filtro de Período na Sidebar
# ------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Filtro de Período")

tipo_filtro = st.sidebar.radio(
    "Tipo de Filtro:",
    options=["Predefinido", "Personalizado"],
    index=0,
    help="Escolha entre períodos predefinidos ou selecione datas específicas"
)

if tipo_filtro == "Predefinido":
    periodo_escolhido = st.sidebar.selectbox(
        "Selecione o período:",
        options=['Geral', 'Último Mês', 'Última Semana', 'Hoje', 'Últimos 3 Meses', 'Últimos 6 Meses', 'Último Ano'],
        index=0
    )
    
    # Calcular datas baseado no período
    hoje = pd.Timestamp.now()
    
    if periodo_escolhido == 'Hoje':
        data_inicio_filtro = hoje.replace(hour=0, minute=0, second=0)
        data_fim_filtro = hoje
    elif periodo_escolhido == 'Última Semana':
        data_inicio_filtro = hoje - pd.Timedelta(days=7)
        data_fim_filtro = hoje
    elif periodo_escolhido == 'Último Mês':
        data_inicio_filtro = hoje - pd.Timedelta(days=30)
        data_fim_filtro = hoje
    elif periodo_escolhido == 'Últimos 3 Meses':
        data_inicio_filtro = hoje - pd.Timedelta(days=90)
        data_fim_filtro = hoje
    elif periodo_escolhido == 'Últimos 6 Meses':
        data_inicio_filtro = hoje - pd.Timedelta(days=180)
        data_fim_filtro = hoje
    elif periodo_escolhido == 'Último Ano':
        data_inicio_filtro = hoje - pd.Timedelta(days=365)
        data_fim_filtro = hoje
    else:  # Geral
        data_inicio_filtro = None
        data_fim_filtro = None
    
    # Mostrar período selecionado
    if data_inicio_filtro and data_fim_filtro:
        st.sidebar.info(f"📆 {data_inicio_filtro.strftime('%d/%m/%Y')} até {data_fim_filtro.strftime('%d/%m/%Y')}")
    else:
        st.sidebar.info("📆 Todos os períodos")

else:  # Personalizado
    col_data1, col_data2 = st.sidebar.columns(2)
    
    with col_data1:
        data_inicio_filtro = st.date_input(
            "Data Início:",
            value=pd.Timestamp.now() - pd.Timedelta(days=30),
            help="Selecione a data inicial"
        )
    
    with col_data2:
        data_fim_filtro = st.date_input(
            "Data Fim:",
            value=pd.Timestamp.now(),
            help="Selecione a data final"
        )
    
    # Converter para Timestamp
    data_inicio_filtro = pd.Timestamp(data_inicio_filtro)
    data_fim_filtro = pd.Timestamp(data_fim_filtro).replace(hour=23, minute=59, second=59)
    
    # Validar datas
    if data_inicio_filtro > data_fim_filtro:
        st.sidebar.error("⚠️ Data inicial não pode ser maior que a data final!")
        data_inicio_filtro = None
        data_fim_filtro = None
    else:
        dias_diferenca = (data_fim_filtro - data_inicio_filtro).days
        st.sidebar.success(f"✅ Período de {dias_diferenca} dias selecionado")

st.markdown("---")

# ------------------------------------------------------------
# 📥 Carregar e Filtrar dados
# ------------------------------------------------------------
with st.spinner("📥 Carregando dados do banco..."):
    df_estoque = carregar_estoque()
    df_clientes = carregar_clientes()
    df_vendas_original = carregar_vendas()
    df_clientes_freq = carregar_clientes_frequentes()
    df_produtos_vendidos = carregar_produtos_mais_vendidos()

# Aplicar filtro de data nas vendas
df_vendas = df_vendas_original.copy()
if data_inicio_filtro and data_fim_filtro and not df_vendas.empty and 'data_venda' in df_vendas.columns:
    df_vendas = df_vendas[
        (df_vendas['data_venda'] >= data_inicio_filtro) & 
        (df_vendas['data_venda'] <= data_fim_filtro)
    ]
    
    # Atualizar também clientes frequentes e produtos mais vendidos para o período
    if not df_vendas.empty:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Clientes frequentes no período
                    cur.execute(f"""
                        SELECT 
                            c.nome_completo,
                            COUNT(v.id_venda) AS qtd_compras,
                            COALESCE(SUM(v.valor_final), 0) AS total_gasto
                        FROM cliente c
                        LEFT JOIN venda v ON c.id_cliente = v.id_cliente
                        WHERE c.cliente_ativo = TRUE
                        AND v.data_venda >= '{data_inicio_filtro.strftime('%Y-%m-%d')}'
                        AND v.data_venda <= '{data_fim_filtro.strftime('%Y-%m-%d')}'
                        GROUP BY c.id_cliente, c.nome_completo
                        HAVING COUNT(v.id_venda) > 0
                        ORDER BY qtd_compras DESC, total_gasto DESC;
                    """)
                    dados = cur.fetchall()
                    if dados:
                        df_clientes_freq = pd.DataFrame(dados)
                        if 'total_gasto' in df_clientes_freq.columns:
                            df_clientes_freq['total_gasto'] = df_clientes_freq['total_gasto'].astype(float)
                    
                    # Produtos mais vendidos no período
                    cur.execute(f"""
                        SELECT 
                            p.nome_produto,
                            COALESCE(SUM(iv.quantidade), 0) AS total_vendido
                        FROM produto p
                        LEFT JOIN item_venda iv ON p.id_produto = iv.id_produto
                        LEFT JOIN venda v ON iv.id_venda = v.id_venda
                        WHERE p.ativo = TRUE
                        AND v.data_venda >= '{data_inicio_filtro.strftime('%Y-%m-%d')}'
                        AND v.data_venda <= '{data_fim_filtro.strftime('%Y-%m-%d')}'
                        GROUP BY p.id_produto, p.nome_produto
                        HAVING SUM(iv.quantidade) > 0
                        ORDER BY total_vendido DESC;
                    """)
                    dados = cur.fetchall()
                    if dados:
                        df_produtos_vendidos = pd.DataFrame(dados)
        except Exception as e:
            st.error(f"Erro ao filtrar dados: {e}")

# ------------------------------------------------------------
# 📊 KPIs Principais
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_vendas = df_vendas['valor_total'].sum() if not df_vendas.empty and 'valor_total' in df_vendas.columns else 0
    st.metric(
        label="💰 Faturamento Total",
        value=f"R$ {total_vendas:,.2f}",
        delta="Todas as vendas"
    )

with col2:
    total_clientes = len(df_clientes) if not df_clientes.empty else 0
    clientes_ativos = df_clientes[df_clientes['cliente_ativo'] == True].shape[0] if not df_clientes.empty and 'cliente_ativo' in df_clientes.columns else 0
    st.metric(
        label="👥 Total de Clientes",
        value=f"{total_clientes}",
        delta=f"{clientes_ativos} ativos"
    )

with col3:
    total_produtos = len(df_estoque) if not df_estoque.empty else 0
    estoque_total = df_estoque['quantidade'].sum() if not df_estoque.empty and 'quantidade' in df_estoque.columns else 0
    st.metric(
        label="📦 Itens em Estoque",
        value=f"{estoque_total}",
        delta=f"{total_produtos} produtos"
    )

with col4:
    total_vendas_count = len(df_vendas) if not df_vendas.empty else 0
    ticket_medio = total_vendas / total_vendas_count if total_vendas_count > 0 else 0
    st.metric(
        label="🎫 Ticket Médio",
        value=f"R$ {ticket_medio:.2f}",
        delta=f"{total_vendas_count} vendas"
    )

st.markdown("---")

# ------------------------------------------------------------
# 📈 Gráficos Principais
# ------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "🛒 Vendas", "👥 Clientes", "📦 Estoque"])

# TAB 1: Visão Geral
with tab1:
    st.subheader("📊 Análise Geral do Negócio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de vendas por meio de compra
        if not df_vendas.empty and 'meio_compra' in df_vendas.columns and 'valor_total' in df_vendas.columns:
            st.markdown("#### 💳 Vendas por Meio de Pagamento")
            
            vendas_meio = df_vendas.groupby('meio_compra')['valor_total'].sum().reset_index()
            vendas_meio = vendas_meio.sort_values('valor_total', ascending=False)
            
            fig1 = px.bar(
                vendas_meio,
                x='meio_compra',
                y='valor_total',
                labels={'meio_compra': 'Meio de Pagamento', 'valor_total': 'Valor Total (R$)'},
                color='valor_total',
                color_continuous_scale='Purples',
                text_auto='.2f'
            )
            fig1.update_layout(
                showlegend=False,
                height=400,
                template='plotly_white'
            )
            fig1.update_traces(texttemplate='R$ %{text}', textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("📊 Nenhuma venda encontrada no período selecionado")
    
    with col2:
        # Produtos mais vendidos
        if not df_produtos_vendidos.empty:
            st.markdown("#### 🏆 Top 10 Produtos Mais Vendidos")
            top_produtos = df_produtos_vendidos.head(10)
            
            fig2 = px.bar(
                top_produtos,
                x='total_vendido',
                y='nome_produto',
                orientation='h',
                labels={'total_vendido': 'Quantidade Vendida', 'nome_produto': 'Produto'},
                color='total_vendido',
                color_continuous_scale='Viridis',
                text_auto=True
            )
            fig2.update_layout(
                showlegend=False,
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                template='plotly_white'
            )
            fig2.update_traces(textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("📊 Nenhum produto vendido no período selecionado")
    
    # Gráfico de evolução temporal (se houver dados de data)
    if not df_vendas.empty and 'data_venda' in df_vendas.columns:
        col_titulo, col_filtro_periodo, col_filtro_metrica = st.columns([2, 1, 1])
        
        with col_titulo:
            st.markdown("#### 📈 Evolução de Vendas ao Longo do Tempo")
        
        with col_filtro_periodo:
            granularidade = st.selectbox(
                "Período:",
                options=['Dia', 'Mês', 'Ano'],
                index=1,  # Padrão: Mês
                key='granularidade_vendas'
            )
        
        with col_filtro_metrica:
            metrica = st.selectbox(
                "Métrica:",
                options=['Faturamento', 'Quantidade de Vendas', 'Ambos'],
                index=2,  # Padrão: Ambos
                key='metrica_vendas'
            )
        
        # Agrupar dados conforme granularidade selecionada
        df_vendas_temp = df_vendas.copy()
        
        if granularidade == 'Dia':
            df_vendas_temp['periodo'] = df_vendas_temp['data_venda'].dt.date
            formato_label = '%d/%m/%Y'
        elif granularidade == 'Mês':
            df_vendas_temp['periodo'] = df_vendas_temp['data_venda'].dt.to_period('M').astype(str)
            formato_label = 'Mês/Ano'
        else:  # Ano
            df_vendas_temp['periodo'] = df_vendas_temp['data_venda'].dt.year.astype(str)
            formato_label = 'Ano'
        
        # Agrupar por período
        vendas_tempo = df_vendas_temp.groupby('periodo').agg({
            'valor_total': 'sum',
            'data_venda': 'count'  # Contar quantidade de vendas
        }).reset_index()
        vendas_tempo.columns = ['periodo', 'faturamento', 'quantidade']
        
        # Criar gráfico baseado na métrica selecionada
        if metrica == 'Faturamento':
            fig3 = px.line(
                vendas_tempo,
                x='periodo',
                y='faturamento',
                labels={'periodo': formato_label, 'faturamento': 'Faturamento (R$)'},
                markers=True
            )
            fig3.update_traces(
                line_color='#667eea', 
                line_width=3, 
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
            )
            fig3.update_layout(yaxis_title='Faturamento (R$)')
            
        elif metrica == 'Quantidade de Vendas':
            fig3 = px.line(
                vendas_tempo,
                x='periodo',
                y='quantidade',
                labels={'periodo': formato_label, 'quantidade': 'Quantidade de Vendas'},
                markers=True
            )
            fig3.update_traces(
                line_color='#10b981', 
                line_width=3, 
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Vendas: %{y}<extra></extra>'
            )
            fig3.update_layout(yaxis_title='Quantidade de Vendas')
            
        else:  # Ambos
            fig3 = go.Figure()
            
            # Linha de faturamento
            fig3.add_trace(go.Scatter(
                x=vendas_tempo['periodo'],
                y=vendas_tempo['faturamento'],
                name='Faturamento (R$)',
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8),
                yaxis='y1',
                hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
            ))
            
            # Linha de quantidade
            fig3.add_trace(go.Scatter(
                x=vendas_tempo['periodo'],
                y=vendas_tempo['quantidade'],
                name='Quantidade de Vendas',
                mode='lines+markers',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8),
                yaxis='y2',
                hovertemplate='<b>%{x}</b><br>Vendas: %{y}<extra></extra>'
            ))
            
            # Layout com dois eixos Y
            fig3.update_layout(
                xaxis=dict(title=formato_label),
                yaxis=dict(
                    title=dict(
                        text='Faturamento (R$)',
                        font=dict(color='#667eea')
                    ),
                    tickfont=dict(color='#667eea')
                ),
                yaxis2=dict(
                    title=dict(
                        text='Quantidade de Vendas',
                        font=dict(color='#10b981')
                    ),
                    tickfont=dict(color='#10b981'),
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
        
        fig3.update_layout(
            height=400,
            hovermode='x unified',
            template='plotly_white',
            xaxis_title=formato_label
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Mostrar estatísticas do período
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("📊 Períodos Analisados", len(vendas_tempo))
        with col_stat2:
            melhor_periodo_fat = vendas_tempo.loc[vendas_tempo['faturamento'].idxmax()]
            st.metric("🏆 Melhor Faturamento", f"{melhor_periodo_fat['periodo']}")
        with col_stat3:
            st.metric("💰 Valor", f"R$ {melhor_periodo_fat['faturamento']:,.2f}")
        with col_stat4:
            melhor_periodo_qtd = vendas_tempo.loc[vendas_tempo['quantidade'].idxmax()]
            st.metric("📈 Mais Vendas", f"{melhor_periodo_qtd['quantidade']:.0f} vendas")

# TAB 2: Vendas
with tab2:
    st.subheader("🛒 Análise Detalhada de Vendas")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not df_vendas.empty:
            st.markdown("#### 📋 Últimas Vendas Registradas")
            vendas_display = df_vendas[['data_venda', 'valor_total', 'meio_compra', 'acao']].head(20).copy()
            
            if 'data_venda' in vendas_display.columns:
                vendas_display['data_venda'] = vendas_display['data_venda'].dt.strftime('%d/%m/%Y')
            if 'valor_total' in vendas_display.columns:
                vendas_display['valor_total'] = vendas_display['valor_total'].apply(lambda x: f"R$ {x:.2f}")
            
            vendas_display.columns = ['Data', 'Valor', 'Meio de Pagamento', 'Ação']
            st.dataframe(vendas_display, use_container_width=True, hide_index=True)
        else:
            st.info("📊 Nenhuma venda registrada no sistema")
    
    with col2:
        if not df_vendas.empty and 'valor_total' in df_vendas.columns:
            st.markdown("#### 📊 Estatísticas de Vendas")
            
            st.metric("💰 Maior Venda", f"R$ {df_vendas['valor_total'].max():.2f}")
            st.metric("💵 Menor Venda", f"R$ {df_vendas['valor_total'].min():.2f}")
            st.metric("📊 Mediana", f"R$ {df_vendas['valor_total'].median():.2f}")
            st.metric("📈 Desvio Padrão", f"R$ {df_vendas['valor_total'].std():.2f}")
    
    st.markdown("---")
    
    # Análises avançadas de produtos
    st.markdown("### 📊 Análises Avançadas de Produtos")
    
    # Buscar dados de item_venda e produto
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Query para análise completa de produtos
                filtro_data = ""
                if data_inicio_filtro and data_fim_filtro:
                    filtro_data = f"AND v.data_venda >= '{data_inicio_filtro.strftime('%Y-%m-%d')}' AND v.data_venda <= '{data_fim_filtro.strftime('%Y-%m-%d')}'"
                
                cur.execute(f"""
                    SELECT 
                        p.id_produto,
                        p.nome_produto,
                        p.categoria,
                        p.preco_custo,
                        p.preco_venda,
                        COALESCE(SUM(iv.quantidade), 0) as total_vendido,
                        COALESCE(SUM(iv.subtotal), 0) as receita_total,
                        COALESCE(SUM(iv.quantidade * p.preco_custo), 0) as custo_total
                    FROM produto p
                    LEFT JOIN item_venda iv ON p.id_produto = iv.id_produto
                    LEFT JOIN venda v ON iv.id_venda = v.id_venda
                    WHERE p.ativo = TRUE {filtro_data}
                    GROUP BY p.id_produto, p.nome_produto, p.categoria, p.preco_custo, p.preco_venda
                    HAVING SUM(iv.quantidade) > 0;
                """)
                dados_produtos = cur.fetchall()
                
                if dados_produtos:
                    df_analise_produtos = pd.DataFrame(dados_produtos)
                    # Converter decimais para float
                    for col in ['preco_custo', 'preco_venda', 'total_vendido', 'receita_total', 'custo_total']:
                        if col in df_analise_produtos.columns:
                            df_analise_produtos[col] = df_analise_produtos[col].astype(float)
                    
                    # Calcular lucro
                    df_analise_produtos['lucro_total'] = df_analise_produtos['receita_total'] - df_analise_produtos['custo_total']
                    df_analise_produtos['margem_lucro'] = ((df_analise_produtos['preco_venda'] - df_analise_produtos['preco_custo']) / df_analise_produtos['preco_venda'] * 100).round(2)
                else:
                    df_analise_produtos = pd.DataFrame()
                
    except Exception as e:
        st.error(f"❌ Erro ao carregar análise de produtos: {e}")
        df_analise_produtos = pd.DataFrame()
    
    if not df_analise_produtos.empty:
        # Linha 1: Mais e Menos vendidos por categoria
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 Top 5 Itens Mais Vendidos por Categoria")
            vendas_por_cat = df_analise_produtos.groupby('categoria')['total_vendido'].sum().sort_values(ascending=False)
            
            fig_cat_top = px.bar(
                x=vendas_por_cat.values,
                y=vendas_por_cat.index,
                orientation='h',
                labels={'x': 'Quantidade Vendida', 'y': 'Categoria'},
                color=vendas_por_cat.values,
                color_continuous_scale='Greens',
                text_auto=True
            )
            fig_cat_top.update_layout(
                showlegend=False,
                height=350,
                template='plotly_white',
                yaxis={'categoryorder': 'total ascending'}
            )
            fig_cat_top.update_traces(textposition='outside')
            st.plotly_chart(fig_cat_top, use_container_width=True)
        
        with col2:
            st.markdown("#### 🐌 Top 5 Itens Menos Vendidos por Categoria")
            vendas_por_cat_baixo = df_analise_produtos.groupby('categoria')['total_vendido'].sum().sort_values(ascending=True).head(5)
            
            fig_cat_baixo = px.bar(
                x=vendas_por_cat_baixo.values,
                y=vendas_por_cat_baixo.index,
                orientation='h',
                labels={'x': 'Quantidade Vendida', 'y': 'Categoria'},
                color=vendas_por_cat_baixo.values,
                color_continuous_scale='Reds',
                text_auto=True
            )
            fig_cat_baixo.update_layout(
                showlegend=False,
                height=350,
                template='plotly_white',
                yaxis={'categoryorder': 'total descending'}
            )
            fig_cat_baixo.update_traces(textposition='outside')
            st.plotly_chart(fig_cat_baixo, use_container_width=True)
        
        st.markdown("---")
        
        # Linha 2: Produtos com baixa margem e produtos para comprar
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚠️ Produtos com Baixa Margem de Lucro (<20%)")
            produtos_baixa_margem = df_analise_produtos[df_analise_produtos['margem_lucro'] < 20].sort_values('margem_lucro')
            
            if not produtos_baixa_margem.empty:
                produtos_baixa_margem_display = produtos_baixa_margem[['nome_produto', 'categoria', 'margem_lucro', 'total_vendido']].head(10).copy()
                produtos_baixa_margem_display['margem_lucro'] = produtos_baixa_margem_display['margem_lucro'].apply(lambda x: f"{x:.1f}%")
                produtos_baixa_margem_display.columns = ['Produto', 'Categoria', 'Margem (%)', 'Vendidos']
                
                st.dataframe(
                    produtos_baixa_margem_display,
                    use_container_width=True,
                    hide_index=True,
                    height=350
                )
                st.caption("⚠️ Considere revisar preços ou fornecedores destes produtos")
            else:
                st.success("✅ Todos os produtos têm margem de lucro adequada!")
        
        with col2:
            st.markdown("#### 🛒 Produtos Prioritários para Compra")
            st.caption("Alta saída (>10 vendas) e estoque atual")
            
            # Buscar estoque atual dos produtos mais vendidos
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT 
                                p.nome_produto,
                                p.categoria,
                                e.quantidade as estoque_atual,
                                COUNT(iv.id_item_venda) as num_vendas,
                                SUM(iv.quantidade) as total_vendido
                            FROM produto p
                            LEFT JOIN estoque e ON 
                                p.categoria = e.categoria AND 
                                p.subcategoria = e.subcategoria
                            LEFT JOIN item_venda iv ON p.id_produto = iv.id_produto
                            WHERE p.ativo = TRUE
                            GROUP BY p.id_produto, p.nome_produto, p.categoria, e.quantidade
                            HAVING SUM(iv.quantidade) > 10
                            ORDER BY total_vendido DESC;
                        """)
                        dados_compra = cur.fetchall()
                        
                        if dados_compra:
                            df_comprar = pd.DataFrame(dados_compra)
                            # Converter para numérico
                            for col in ['estoque_atual', 'num_vendas', 'total_vendido']:
                                if col in df_comprar.columns:
                                    df_comprar[col] = pd.to_numeric(df_comprar[col], errors='coerce').fillna(0)
                            
                            # Calcular prioridade (alta venda + baixo estoque)
                            df_comprar['prioridade'] = df_comprar['total_vendido'] / (df_comprar['estoque_atual'] + 1)
                            df_comprar = df_comprar.sort_values('prioridade', ascending=False).head(10)
                            
                            df_comprar_display = df_comprar[['nome_produto', 'categoria', 'total_vendido', 'estoque_atual']].copy()
                            df_comprar_display['status'] = df_comprar_display['estoque_atual'].apply(
                                lambda x: '🔴 Urgente' if x < 10 else ('🟡 Atenção' if x < 30 else '🟢 Normal')
                            )
                            df_comprar_display.columns = ['Produto', 'Categoria', 'Vendidos', 'Estoque', 'Status']
                            
                            st.dataframe(
                                df_comprar_display,
                                use_container_width=True,
                                hide_index=True,
                                height=350
                            )
                        else:
                            st.info("📊 Dados insuficientes para análise")
            except Exception as e:
                st.error(f"Erro ao analisar estoque: {e}")
        
        st.markdown("---")
        
        # Análise de rentabilidade
        st.markdown("#### 💰 Análise de Rentabilidade dos Produtos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            produtos_lucrativos = df_analise_produtos[df_analise_produtos['lucro_total'] > 0]
            total_lucro = produtos_lucrativos['lucro_total'].sum()
            st.metric("💚 Lucro Total", f"R$ {total_lucro:,.2f}", delta="Produtos lucrativos")
        
        with col2:
            produtos_prejuizo = df_analise_produtos[df_analise_produtos['lucro_total'] < 0]
            if not produtos_prejuizo.empty:
                total_prejuizo = abs(produtos_prejuizo['lucro_total'].sum())
                st.metric("💔 Prejuízo Total", f"R$ {total_prejuizo:,.2f}", delta=f"{len(produtos_prejuizo)} produtos", delta_color="inverse")
            else:
                st.metric("💔 Prejuízo Total", "R$ 0,00", delta="Nenhum produto")
        
        with col3:
            margem_media = df_analise_produtos['margem_lucro'].mean()
            st.metric("📊 Margem Média", f"{margem_media:.1f}%", delta="Geral")
        
        # Tabela de produtos em prejuízo
        if not produtos_prejuizo.empty:
            st.markdown("##### 🚨 Produtos em Prejuízo - Não Comprar!")
            produtos_prejuizo_display = produtos_prejuizo[['nome_produto', 'categoria', 'preco_custo', 'preco_venda', 'total_vendido', 'lucro_total']].copy()
            produtos_prejuizo_display['preco_custo'] = produtos_prejuizo_display['preco_custo'].apply(lambda x: f"R$ {x:.2f}")
            produtos_prejuizo_display['preco_venda'] = produtos_prejuizo_display['preco_venda'].apply(lambda x: f"R$ {x:.2f}")
            produtos_prejuizo_display['lucro_total'] = produtos_prejuizo_display['lucro_total'].apply(lambda x: f"R$ {x:.2f}")
            produtos_prejuizo_display.columns = ['Produto', 'Categoria', 'Custo', 'Venda', 'Qtd Vendida', 'Prejuízo']
            
            st.dataframe(
                produtos_prejuizo_display,
                use_container_width=True,
                hide_index=True
            )
            st.error("⚠️ **Ação Recomendada:** Revisar precificação ou descontinuar estes produtos!")
        
        st.markdown("---")
        
        # Análise de Validade dos Produtos
        st.markdown("### ⏰ Controle de Validade de Produtos")
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Buscar produtos por status de validade
                    cur.execute("""
                        SELECT * FROM vw_produtos_validade
                        ORDER BY criticidade ASC, data_validade ASC;
                    """)
                    dados_validade = cur.fetchall()
                    
                    if dados_validade:
                        df_validade = pd.DataFrame(dados_validade)
                        
                        # Converter datas
                        for col in ['data_fabricacao', 'data_validade']:
                            if col in df_validade.columns:
                                df_validade[col] = pd.to_datetime(df_validade[col])
                        
                        # KPIs de Validade
                        col1, col2, col3, col4 = st.columns(4)
                        
                        vencidos = df_validade[df_validade['status_validade'] == 'VENCIDO']
                        vence_7dias = df_validade[df_validade['status_validade'] == 'VENCE EM 7 DIAS']
                        vence_30dias = df_validade[df_validade['status_validade'].isin(['VENCE EM 15 DIAS', 'VENCE EM 30 DIAS'])]
                        
                        with col1:
                            qtd_vencidos = vencidos['quantidade_disponivel'].sum() if not vencidos.empty else 0
                            st.metric("🔴 Produtos Vencidos", f"{int(qtd_vencidos)}", 
                                     delta=f"{len(vencidos)} lotes", delta_color="inverse")
                        
                        with col2:
                            qtd_7dias = vence_7dias['quantidade_disponivel'].sum() if not vence_7dias.empty else 0
                            st.metric("🟠 Vence em 7 dias", f"{int(qtd_7dias)}", 
                                     delta=f"{len(vence_7dias)} lotes", delta_color="inverse")
                        
                        with col3:
                            qtd_30dias = vence_30dias['quantidade_disponivel'].sum() if not vence_30dias.empty else 0
                            st.metric("🟡 Vence em 30 dias", f"{int(qtd_30dias)}", 
                                     delta=f"{len(vence_30dias)} lotes", delta_color="off")
                        
                        with col4:
                            # Buscar valor de prejuízo
                            cur.execute("""
                                SELECT SUM(cv.quantidade_disponivel * p.preco_custo) as prejuizo_total
                                FROM controle_validade cv
                                JOIN produto p ON cv.id_produto = p.id_produto
                                WHERE cv.data_validade < CURRENT_DATE 
                                  AND cv.quantidade_disponivel > 0;
                            """)
                            prejuizo = cur.fetchone()
                            prejuizo_valor = float(prejuizo['prejuizo_total']) if prejuizo and prejuizo['prejuizo_total'] else 0
                            st.metric("💸 Prejuízo Estimado", f"R$ {prejuizo_valor:,.2f}", 
                                     delta="Produtos vencidos", delta_color="inverse")
                        
                        # Tabelas por categoria de urgência
                        tab_venc, tab_7d, tab_30d, tab_todos = st.tabs([
                            "🔴 Vencidos", 
                            "🟠 Vence em 7 dias", 
                            "🟡 Vence em 30 dias", 
                            "📋 Todos"
                        ])
                        
                        with tab_venc:
                            if not vencidos.empty:
                                vencidos_display = vencidos[['nome_produto', 'categoria', 'lote', 'data_validade', 
                                                             'quantidade_disponivel', 'fornecedor', 'dias_para_vencer']].copy()
                                vencidos_display['data_validade'] = vencidos_display['data_validade'].dt.strftime('%d/%m/%Y')
                                vencidos_display['dias_para_vencer'] = vencidos_display['dias_para_vencer'].apply(lambda x: f"{abs(int(x))} dias")
                                vencidos_display.columns = ['Produto', 'Categoria', 'Lote', 'Validade', 
                                                           'Quantidade', 'Fornecedor', 'Vencido Há']
                                
                                st.dataframe(vencidos_display, use_container_width=True, hide_index=True)
                                st.error("🚨 **AÇÃO URGENTE:** Retirar do estoque e descartar adequadamente!")
                            else:
                                st.success("✅ Nenhum produto vencido no momento!")
                        
                        with tab_7d:
                            if not vence_7dias.empty:
                                vence7_display = vence_7dias[['nome_produto', 'categoria', 'lote', 'data_validade', 
                                                              'quantidade_disponivel', 'dias_para_vencer']].copy()
                                vence7_display['data_validade'] = vence7_display['data_validade'].dt.strftime('%d/%m/%Y')
                                vence7_display['dias_para_vencer'] = vence7_display['dias_para_vencer'].apply(lambda x: f"{int(x)} dias")
                                vence7_display.columns = ['Produto', 'Categoria', 'Lote', 'Validade', 
                                                         'Quantidade', 'Vence em']
                                
                                st.dataframe(vence7_display, use_container_width=True, hide_index=True)
                                st.warning("⚠️ **AÇÃO RECOMENDADA:** Fazer promoção urgente ou doação!")
                            else:
                                st.info("📊 Nenhum produto vencendo em 7 dias")
                        
                        with tab_30d:
                            if not vence_30dias.empty:
                                vence30_display = vence_30dias[['nome_produto', 'categoria', 'lote', 'data_validade', 
                                                                'quantidade_disponivel', 'dias_para_vencer', 'status_validade']].copy()
                                vence30_display['data_validade'] = vence30_display['data_validade'].dt.strftime('%d/%m/%Y')
                                vence30_display['dias_para_vencer'] = vence30_display['dias_para_vencer'].apply(lambda x: f"{int(x)} dias")
                                vence30_display.columns = ['Produto', 'Categoria', 'Lote', 'Validade', 
                                                          'Quantidade', 'Vence em', 'Status']
                                
                                st.dataframe(vence30_display, use_container_width=True, hide_index=True)
                                st.info("💡 **SUGESTÃO:** Monitorar e priorizar a venda destes produtos")
                            else:
                                st.info("📊 Nenhum produto vencendo em 30 dias")
                        
                        with tab_todos:
                            todos_display = df_validade[['nome_produto', 'categoria', 'lote', 'data_fabricacao',
                                                         'data_validade', 'quantidade_disponivel', 'status_validade']].copy()
                            todos_display['data_fabricacao'] = todos_display['data_fabricacao'].dt.strftime('%d/%m/%Y')
                            todos_display['data_validade'] = todos_display['data_validade'].dt.strftime('%d/%m/%Y')
                            todos_display.columns = ['Produto', 'Categoria', 'Lote', 'Fabricação', 
                                                    'Validade', 'Quantidade', 'Status']
                            
                            st.dataframe(todos_display, use_container_width=True, hide_index=True, height=400)
                    else:
                        st.info("📊 Nenhum registro de validade cadastrado")
                        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados de validade: {e}")
    else:
        st.info("📊 Dados insuficientes para análises avançadas no período selecionado")

# TAB 3: Clientes
with tab3:
    st.subheader("👥 Análise de Clientes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not df_clientes_freq.empty:
            st.markdown("#### 🏆 Top 10 Clientes Mais Frequentes")
            top_clientes = df_clientes_freq.head(10).copy()
            
            if 'total_gasto' in top_clientes.columns:
                top_clientes['total_gasto'] = top_clientes['total_gasto'].apply(lambda x: f"R$ {x:.2f}" if pd.notna(x) else "R$ 0,00")
            
            st.dataframe(
                top_clientes,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "nome_completo": "Cliente",
                    "qtd_compras": st.column_config.NumberColumn("Nº Compras", format="%d"),
                    "total_gasto": "Total Gasto"
                }
            )
        else:
            st.info("📊 Dados de clientes frequentes não disponíveis")
    
    with col2:
        if not df_clientes.empty:
            st.markdown("#### 📍 Distribuição de Clientes por CEP")
            if 'cep' in df_clientes.columns:
                # Extrair primeiros 5 dígitos do CEP para região
                df_clientes_temp = df_clientes.copy()
                df_clientes_temp['regiao_cep'] = df_clientes_temp['cep'].astype(str).str[:5]
                clientes_cep = df_clientes_temp['regiao_cep'].value_counts().head(10).reset_index()
                clientes_cep.columns = ['CEP', 'Quantidade']
                
                fig4 = px.bar(
                    clientes_cep,
                    x='CEP',
                    y='Quantidade',
                    labels={'CEP': 'Região (CEP)', 'Quantidade': 'Nº de Clientes'},
                    color='Quantidade',
                    color_continuous_scale='Blues'
                )
                fig4.update_layout(showlegend=False, template='plotly_white')
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("📊 Dados de CEP não disponíveis")
    
    # Cadastros ao longo do tempo
    if not df_clientes.empty and 'criado_em' in df_clientes.columns:
        st.markdown("#### 📈 Novos Cadastros ao Longo do Tempo")
        cadastros_tempo = df_clientes.groupby(df_clientes['criado_em'].dt.date).size().reset_index()
        cadastros_tempo.columns = ['data', 'quantidade']
        
        fig5 = px.area(
            cadastros_tempo,
            x='data',
            y='quantidade',
            labels={'data': 'Data', 'quantidade': 'Novos Cadastros'},
            color_discrete_sequence=['#667eea']
        )
        fig5.update_layout(template='plotly_white')
        st.plotly_chart(fig5, use_container_width=True)

# TAB 4: Estoque
with tab4:
    st.subheader("📦 Análise de Estoque")
    
    if not df_estoque.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Estoque por categoria
            if 'categoria' in df_estoque.columns and 'quantidade' in df_estoque.columns:
                st.markdown("#### 📊 Estoque por Categoria")
                estoque_cat = df_estoque.groupby('categoria')['quantidade'].sum().reset_index()
                estoque_cat = estoque_cat.sort_values('quantidade', ascending=False)
                
                fig6 = px.pie(
                    estoque_cat,
                    values='quantidade',
                    names='categoria',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig6.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            # Estoque por tipo de animal
            if 'tipo_animal' in df_estoque.columns and 'quantidade' in df_estoque.columns:
                st.markdown("#### 🐾 Estoque por Tipo de Animal")
                estoque_animal = df_estoque.groupby('tipo_animal')['quantidade'].sum().reset_index()
                estoque_animal = estoque_animal.sort_values('quantidade', ascending=False)
                
                fig7 = px.bar(
                    estoque_animal,
                    x='tipo_animal',
                    y='quantidade',
                    labels={'tipo_animal': 'Tipo de Animal', 'quantidade': 'Quantidade'},
                    color='quantidade',
                    color_continuous_scale='Viridis'
                )
                fig7.update_layout(showlegend=False, template='plotly_white')
                st.plotly_chart(fig7, use_container_width=True)
        
        # Tabela de estoque com alertas
        st.markdown("#### 📋 Detalhamento do Estoque")
        
        # Criar cópia para exibição
        estoque_display = df_estoque.copy()
        
        # Adicionar indicador de estoque baixo
        if 'quantidade' in estoque_display.columns:
            estoque_display['status'] = estoque_display['quantidade'].apply(
                lambda x: '🔴 Crítico' if x < 10 else ('🟡 Baixo' if x < 30 else '🟢 OK')
            )
        
        # Selecionar colunas para exibir
        cols_display = ['categoria', 'subcategoria', 'tipo_animal', 'quantidade', 'status']
        cols_display = [col for col in cols_display if col in estoque_display.columns]
        
        st.dataframe(
            estoque_display[cols_display],
            use_container_width=True,
            hide_index=True
        )
        
        st.caption("🔴 Crítico: Estoque < 10 | 🟡 Baixo: Estoque < 30 | 🟢 OK: Estoque adequado")
    else:
        st.info("📊 Nenhum dado de estoque disponível")

# ------------------------------------------------------------
# 📌 Footer
# ------------------------------------------------------------
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🐾 <b>Dashboard Pet Shop</b> | Análise em Tempo Real | Dados atualizados automaticamente</p>
        <p style='font-size: 12px;'>Conectado ao banco PostgreSQL - Neon Database</p>
    </div>

""", unsafe_allow_html=True)
