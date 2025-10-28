import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

#if "authenticated" not in st.session_state or not st.session_state.authenticated:
#    st.warning("Você precisa fazer o login para acessar esta página!")
#    st.stop()

# O FRONT END TEM QUE FAZER A MELHOR FORMA E MAIS DINAMICA DE 
# EXPOR APENAS OS DADOS RELEVANTES E COMPARA LOS DE UMA FORMA QUE O CLIENTE
# CONSIGA ENTENDER. JÁ DEIXAR PRONTO ENQUANTO FAZEMOS A NOSSA PARTE SIMULTANEAMENTE
#
# dados: de movimentação: saída, entrada, lucro; dividos por categorias; dividor por mês, ano, etc
# itens: que mais sairam, menos sairam, a comprar, causaram prejuízo; divido por categoria
# cliente: ultimo mes, ultimo ano, ultima semana, media geral, localizações, faixa etaria, genero
# --  media de gastos, frequncia de compra, metodo de compra preferido
# animais: ultimo mes, ultimo ano, ultima semana, media geral, categoria, porte, idade, raça 
# *** engajamento: ENGAJAMENTO REDES SOCIAIS, REDES SOCIAIS ATIVAS, CURTIDAS TOTAIS INSTAGRAM, CURTIDAS TOTAIS TIKTOK  
# *** POSTAGENS: POR MES, CLIQUES NO SITE POR MES, CLIENTES QUE ENTRARAM PELAS REDES SOCIAIS, CLIENTES QUE ENTRARAM DIRETAMENTE PELO WHATSAPP 
# -- CLIENTES QUE COMPRARAM DAS REDES SOCIAIS, VIDEOS POSTADOS, POSTAGENS REALIZADAS 
# *** ENGAJAMENTO CARROSSEL, ENGAJAMETO VIDEO , ENGAJAMENTO FOTOS , ENGAJAMENTO STORIES 
# *** INVESTIMENTO MENSAL EM MARKETING DIGITAL , CLIQUES/REAL, VENDAS/REAL
# *** Taxa de conversão (quantos cliques resultaram em compras). Custo por aquisição (CPA) por canal.
# -- Horários de maior engajamento (para otimizar posts). Taxa de retenção ou seguidores ativos (não só curtidas).
# -- Comparativo mês a mês de desempenho das postagens. MENÇOES NAS REDES SOCIAIS 

# Show app title and description.
st.set_page_config(page_title="Gerenciado de clientes", page_icon="🎫")
st.title("👤 Gerenciador de perfis de clientes")
st.write(
    """
    Este aplicativo é um gerenciador de perfis de clientes. Nele, é possível editar 
    clientes existentes e ver estatísticas.
    """
)

data = { #       pegar esses dados do banco de dados para montrar na tela

    "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
    "Nome": np.random.choice(["Rafael", "Gabriel", "Daniel", "Miguel"], size=100),
    "Data da venda": datetime.datetime.now().strftime("%d-%m-%Y"),   
    "Valor total": np.random.choice(["12", "33", "324", "122"]), 
    "Produtos": np.random.choice(["Ração de gato", "Ração de cahorro", "Brinquedo de gato"]),
    "Valor unitário do produto": np.random.choice(["12", "23", "54", "25"]),
    "Date Submitted": [
        datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
        for _ in range(100)
    ],
}
df = pd.DataFrame(data)

# Save the dataframe in session state (a dictionary-like object that persists across
# page runs). This ensures our data is persisted when the app updates.
st.session_state.df = df


# -------------------------------------------------------------------------------------------------
# adicionar um novo cliente no banco de dados

# Show a section to add a new ticket.
st.header("Resgistra uma nova venda") 

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_venda"):
    nome = st.text_area("Nome completo", placeholder="Ex: joão paulo costa", height=50, max_chars=100)
    data_venda = st.date_input("Data de venda")
    valor_total = st.number_input("Valor total", placeholder="Ex:53,34")
    valor_unit = st.number_input("Valor Unitário do produto", placeholder="Ex:53,34")
    produto = st.text_area("Produtos", placeholder="Ex: Ração de gato", height=50, max_chars=50)
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1]) # vai pegar o id do banco de dados
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    df = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}", # vai pegar o id do banco de dados
                "Nome": nome,
                "Data de venda": data_venda,
                "Valor total": valor_total,
                "Valor unitário": valor_unit,
                "Produto": produto,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("Ticket submitted! Here are the ticket details:")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df, st.session_state.df], axis=0)

# -----------------------------------------------------------------------------------------------------------
# mostra todos os clientes cadastrados
# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.

# Show section to view and edit existing tickets in a table.
st.header("Clientes cadastrados")

# Show section to view and edit existing tickets in a table.
#st.info(
#    "You can edit the tickets by double clicking on a cell. Note how the plots below "
#    "update automatically! You can also sort the table by clicking on the column headers.",
#    icon="✍️",
#
#"""

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
df_new = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)

# -------------------------------------------------------------------------------------------------------------
# parte para mostrar grafico e estatisticas
 # Show some metrics and charts about the ticket.
st.header("Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Bairro == "Marambai"])
col1.metric(label="Todos os clientes que moram no bairro marambaia", value=num_open_tickets, delta=10)
#col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
#col3.metric(label="Average resolution time (hours)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")