import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="Gerenciador de estoque", page_icon="🎫")
st.title("👤 Gerenciador de estoque")
st.write(
    """
    Este página é um gerenciador de estoque de produtos. Nele, é possível ver 
    estoque existentes e ver estatísticas.
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

    "Categoria": np.random.choice(["Ração seca", "Ração úmida", "Briquedo", "Medicação"], size=100),
    "Subcategoria": np.random.choice(["Imunidade", "Premium", "Super premium"], size=100),
    "Tipo de Animal": np.random.choice(["Gato", "Cachorro", "Outros"], size=100), 
    "Porte": np.random.choice(["Grande", "Médio", "Pequeno"], size=100),
    "Idade": np.random.choice(["Filhote", "Adulto"], size=100),
    "Date Submitted": [
        datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
        for _ in range(100)
    ],
}
df = pd.DataFrame(data)

st.session_state.df = df

st.header("Produtos em estoque")

df_new = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)
# -------------------------------------------------------------------------------------------------------------
# parte para mostrar grafico e estatisticas
st.header("Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
#col1, col2, col3 = st.columns(3)
#num_open_tickets = len(st.session_state.df[st.session_state.df.Bairro == "Marambai"])
#col1.metric(label="Todos os clientes que moram no bairro marambaia", value=num_open_tickets, delta=10)
#col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
#col3.metric(label="Average resolution time (hours)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("")
status_plot = (
    alt.Chart(df)
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
    alt.Chart(df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")