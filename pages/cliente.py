import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa fazer o login para acessar esta página!")
    st.stop()

# Show app title and description.
st.set_page_config(page_title="Gerenciador de clientes", page_icon="🎫")
st.title("👤 Gerenciador de clientes")
st.write(
    """
    Este aplicativo é um gerenciador de perfis de clientes. Nele, é possível cadastrar 
    novos clientes, ver todos os clientes e ver estatísticas.
    """
)

data = { # aqui vai dados do banco de dados para mostrar na tela
    #"ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
    #"Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
    #"Priority": np.random.choice(["High", "Medium", "Low"], size=100),
    #"Date Submitted": [
    #    datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
    #    for _ in range(100)
    #],
#       pegar esses dados do banco de dados para montrar na tela

    "ID": [f"{i}" for i in range(1100, 1000, -1)],
    "Nome": np.random.choice(["Rafael", "Gabriel", "Daniel", "Miguel"], size=100),
    "CPF": "123,456,789,12",
    "Bairro": np.random.choice(["Marambaia", "Sacramenta", "Batista campos", "Reduto"], size=100),
    "CEP": "12345678",
    "Endereco": "Rua dos bobos",
    "Numero": "0",
    "Email": "rafael@gmail.com",
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
st.header("Adicionar um novo cliente") 

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_cliente"):
    nome = st.text_area("Nome completo", placeholder="Ex: joão paulo costa", height=50, max_chars=100)
    CPF = st.text_area("CPF", placeholder="Ex: 123.456.789.10", height=50, max_chars=14)
    email = st.text_area("Email", placeholder="Ex: cliente@gmail.com", height=50, max_chars=50)
    bairro = st.text_area("Bairro", placeholder="Ex: marambaia", height=50, max_chars=50)
    endereco = st.text_area("Endereço", placeholder="Ex: travessa julio cesar", height=50, max_chars=50)
    CEP = st.text_area("CEP", placeholder="12345-678", height=50, max_chars=9)
    numero = st.text_area("Numero do endereço", placeholder="Ex: 78B", height=50, max_chars=10)
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1]) # vai pegar o id do banco de dados
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    df = pd.DataFrame(
        [
            {
                "ID": f"{recent_ticket_number+1}", # vai pegar o id do banco de dados
                "Date Submitted": today,
                "Nome": nome,
                "CPF": CPF,
                "Email": email,
                "Bairro": bairro,
                "Endereco": endereco,
                "CEP": CEP,
                "Numero": numero,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("Clinte cadastrado com sucesso! Aqui estão os dados:")
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
    disabled=[
        "ID", "Date Submitted", "Nome", "CPF", "Email", "Bairro", "Endereco"
        "CEP", "Numero" 
        ],
)

# -------------------------------------------------------------------------------------------------------------
# parte para mostrar grafico e estatisticas
 # Show some metrics and charts about the ticket.
st.header("Analíse de dados e gráficos")

# Show metrics side by side using `st.columns` and `st.metric`.
#col1, col2, col3 = st.columns(3)
#num_open_tickets = len(st.session_state.df[st.session_state.df.Bairro == "Marambai"])
#col1.metric(label="Todos os clientes que moram no bairro marambaia", value=num_open_tickets, delta=10)
#col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
#col3.metric(label="Average resolution time (hours)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("")
st.write("* Quantidade de clientes por bairro:")
clientes_bairro_plot = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x="Bairro:O",
        y="count():Q",
        xOffset="Status:N",
        color="Bairro:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(clientes_bairro_plot, use_container_width=True, theme="streamlit")

st.write("* Quantidade de clientes com o mesmo nome:")
clientes_nomme_plot = (
    alt.Chart(df)
    .mark_arc()
    .encode(
        theta="count():Q", 
        color="Nome:N"
        )
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(clientes_nomme_plot, use_container_width=True, theme="streamlit")