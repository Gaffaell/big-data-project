import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
#if "authenticated" not in st.session_state or not st.session_state.authenticated:
#    st.warning("Você precisa fazer o login para acessar esta página!")
#    st.stop()

# Show app title and description.
st.set_page_config(page_title="Gerenciador de produtos", page_icon="🎫")
st.title("👤 Gerenciador de produtos")
st.write(
    """
    Este aplicativo é um gerenciador de produtos. Nele, é possível cadastrar 
    produtos novos, ver todos os produtos e ver estatísticas.
    """
)

#------------------------------------------------------------------
# variaveis de formatação

# dataframe content
data = { 
    "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
    "Categoria": np.random.choice(["Ração seca", "Ração úmida", "Briquedo", "Medicação"], size=100),
    "Subcategoria": np.random.choice(["Imunidade", "Premium", "Super premium"], size=100),
    "Tipo de animal": np.random.choice(["Gato", "Cachorro", "Outros"], size=100), 
    "Porte": np.random.choice(["Grande", "Médio", "Pequeno"], size=100),
    "Idade": np.random.choice(["Filhote", "Adulto"], size=100),
    "Nome do produto": np.random.choice(["Purina", "Pedigree", "Gran plus", "Royal canin"], size=100),
    "Descrição": np.random.choice(["Ração de gato adulto gran plus", "Ração de cachorro filhote royal canin"], size=100), 
    "Preço unitário de venda": "R$20",
    "Preço unitário de compra": "R$7",
    "Porcentagem de lucro": "65%",
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
# adicionar um novo produto no banco de dados

# Show a section to add a new ticket.
st.header("Adicionar um produto") 

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_produto"):
    categoria = st.selectbox("Categoria", ["Ração seca", "Ração úmida", "Briquedo", "Medicação"])
    subcategoria = st.selectbox("Subcategoria", ["Imunidade", "Premium", "Super premium", "Não possui"])
    tipo_animal = st.selectbox("Tipo de animal", ["Gato", "Cachorro", "Cavalo", "Peixe"])
    porte = st.selectbox("Porte", ["Pequeno", "Médio", "Grande"])
    idade = st.selectbox("Idade", ["Filhote", "Jovem", "Adulto"])
    nome_produto = st.selectbox("Nome do produto", ["Purina", "Pedigree", "Gran plus", "Royal canin", "Outra marca"])
    descricao = st.text_area("Descrição", placeholder="Ex: Ração de gato adulto gran plus", height=50, max_chars=50)
    preco_venda = st.number_input("Preço unitário de venda")
    preco_compra = st.number_input("Preço unitário de compra")
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1]) # vai pegar o id do banco de dados
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    porcentagem_lucro = (((preco_venda - preco_compra) * 100) // preco_venda)
    df = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}", # vai pegar o id do banco de dados
                "Date Submitted": today,
                "Categoria": categoria,
                "Subcategoria": subcategoria,
                "Tipo de animal": tipo_animal,
                "Porte": porte,
                "Idade": idade,
                "Nome do produto": nome_produto,
                "Descrição": descricao,
                "Preço unitário de venda": preco_venda,
                "Preço unitário de compra": preco_compra,
                "Porcentagem de lucro": porcentagem_lucro,
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