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
st.set_page_config(page_title="Gerenciador de registros de vendas", page_icon="🎫")
st.title("👤 Gerenciador de registros de vendas")
st.write(
    """
    Este aplicativo é um gerenciador de registros de vendas. Nele, é possível cadastrar 
    uma nova venda, visualizar vendas existentes e ver estatísticas.
    """
)

data = { #       pegar esses dados do banco de dados para montrar na tela

    "ID": [f"{i}" for i in range(1100, 1000, -1)],
    "Nome": np.random.choice(["Rafael", "Gabriel", "Daniel", "Miguel"], size=100),
    "Valor total": np.random.choice([12, 33, 324, 122], size=100), 
    "Produto": np.random.choice(["Ração de gato", "Ração de cahorro", "Brinquedo de gato", "Brinquedo de cachorro"], size=100),
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
    nome_cliente = st.text_area("Nome completo", placeholder="Ex: joão paulo costa", height=50, max_chars=100)
    nome_produto = st.multiselect("Produto", ["Ração de gato", "Ração de cahorro", "Brinquedo de gato", "Brinquedo de cachorro"])
    valor_total = st.number_input("Valor total")
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
                "Nome": nome_cliente,
                "Valor total": valor_total,
                "Produto": nome_produto,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("Venda cadastrada com sucesso! Aqui estão os dados:")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df, st.session_state.df], axis=0)

# -----------------------------------------------------------------------------------------------------------
# mostra todos os clientes cadastrados
# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.

# Show section to view and edit existing tickets in a table.
st.header("Vendas cadastradas")

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
    disabled=["ID", "Date Submitted", "Nome", "Produto", "Data de venda", "valor total"],
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
st.write("* Quantidade de vendas em cada mês:")
venda_mes_plot = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="month(Date Submitted):N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(venda_mes_plot, use_container_width=True, theme="streamlit")

st.write("* O produto que mais vende:")
venda_produto_plot = (
    alt.Chart(df)
    .mark_arc()
    .encode(
        theta="count():Q", 
        color="Produto:N"
    )
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(venda_produto_plot, use_container_width=True, theme="streamlit")