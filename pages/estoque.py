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
st.set_page_config(page_title="Gerenciador de estoque", page_icon="🎫")
st.title("👤 Gerenciador de estoque")
st.write(
    """
    Este página é um gerenciador de estoque de produtos. Nele, é possível ver 
    estoque existentes e ver estatísticas.
    """
)

data = { # aqui vai dados do banco de dados para mostrar na tela

    "Categoria": np.random.choice(["Ração seca", "Ração úmida", "Brinquedo", "Medicação"], size=100),
    "Subcategoria": np.random.choice(["Imunidade", "Premium", "Super premium"], size=100),
    "Tipo de animal": np.random.choice(["Gato", "Cachorro", "Outros"], size=100), 
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
    disabled=["ID", "Date Submitted", "Categoria", "Subcategoria", "Tipo de animal",
              "Porte", "Idade"
    ],
)
# -------------------------------------------------------------------------------------------------------------
# parte para mostrar grafico e estatisticas
st.header("Analíse de dados e gráficos")

# Show metrics side by side using `st.columns` and `st.metric`.
st.write("Total de produtos de cada categoria:")

col1, col2, col3, col4 = st.columns(4)
num_racao_seca = len(st.session_state.df[st.session_state.df.Categoria == "Ração seca"])
num_racoa_umida = len(st.session_state.df[st.session_state.df.Categoria == "Ração úmida"])
num_brinquedo = len(st.session_state.df[st.session_state.df.Categoria == "Brinquedo"])
num_medicacao = len(st.session_state.df[st.session_state.df.Categoria == "Medicação"])

col1.metric(label="Total de Rações secas", value=num_racao_seca)
col2.metric(label="Total de Rações úmidas", value=num_racoa_umida)
col3.metric(label="Total de Brinquedos", value=num_brinquedo)
col4.metric(label="Total de Medicações", value=num_medicacao)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("")
st.write("* Quantidade de produtos cada categoria")
categoria_plot = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x="Categoria:O",
        y="count():Q",
        #xOffset="Status:N",
        color="Categoria:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(categoria_plot, use_container_width=True, theme="streamlit")

st.write("* Quantidade de produtos de cada tipo de animal")
tipo_animal_plot = (
    alt.Chart(df)
    .mark_arc()
    .encode(
        theta="count():Q", 
        color="Tipo de animal:O"
    )
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(tipo_animal_plot, use_container_width=True, theme="streamlit")
