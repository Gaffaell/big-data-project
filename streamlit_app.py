# streamlit_app.py
import datetime
import random
import hashlib

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

USERS = {
    # senha = "123456"
    "admin@exemplo.com": hashlib.sha256("123456".encode()).hexdigest(),
}

def _sha256(tx: str) -> str:
    return hashlib.sha256(tx.encode()).hexdigest()

def _is_authed() -> bool:
    return bool(st.session_state.get("auth") and st.session_state.get("user"))

def _login(email: str):
    st.session_state["auth"] = True
    st.session_state["user"] = email
    st.session_state["display_name"] = email.split("@")[0].title()

def _logout():
    for k in ("auth", "user", "display_name"):
        st.session_state.pop(k, None)

def _render_login():
    st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
    st.markdown(
        """
        <div style="max-width:420px;margin:8vh auto 0 auto;padding:2rem;border-radius:16px;
             background:var(--secondary-background-color,#1a2035);box-shadow:0 10px 30px rgba(0,0,0,.35)">
          <h2 style="text-align:center;margin-top:0">Bem-vindo!</h2>
          <p style="text-align:center;margin-bottom:1rem">Faça login para continuar</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        if email and password and USERS.get(email.strip().lower()) == _sha256(password):
            _login(email.strip().lower())
            st.success("Login realizado!")
            st.rerun()
        else:
            st.error("Credenciais inválidas. Verifique email e senha.")


if not _is_authed():
    _render_login()
    st.stop()


st.set_page_config(page_title="Support tickets", page_icon="🎫", layout="centered")


c1, c2 = st.columns([1, 6])
with c1:
    if st.button("Sair"):
        _logout()
        st.success("Sessão encerrada.")
        st.rerun()


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
st.set_page_config(page_title="Support tickets", page_icon="🎫")
st.title("👤 Gerenciador de perfis de clientes")
st.write(
    """
    Este aplicativo é um gerenciador de perfis de clientes. Nele, é possível editar 
    clientes existentes e ver estatísticas.
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

    "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
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
with st.form("add_ticket_form"):
    nome = st.text_area("Nome")
    CPF = st.text_area("CPF")
    bairro = st.text_area("Bairro")
    endereco = st.text_area("Endereço")
    CEP = st.text_area("CEP")
    numero = st.text_area("Numero do endereço")
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
                "Date Submitted": today,
                "Nome": nome,
                "CPF": CPF,
                "Bairro": bairro,
                "Endereco": endereco,
                "CEP": CEP,
                "Numero": numero,
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