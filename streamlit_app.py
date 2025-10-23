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


st.title("🎫 Support tickets")
st.write(
    """
    This app shows how you can build an internal tool in Streamlit. Here, we are 
    implementing a support ticket workflow. The user can create a ticket, edit 
    existing tickets, and view some statistics.
    """
)

# Dataframe em sessão
if "df" not in st.session_state:
    np.random.seed(42)
    issue_descriptions = [
        "Network connectivity issues in the office",
        "Software application crashing on startup",
        "Printer not responding to print commands",
        "Email server downtime",
        "Data backup failure",
        "Login authentication problems",
        "Website performance degradation",
        "Security vulnerability identified",
        "Hardware malfunction in the server room",
        "Employee unable to access shared files",
        "Database connection failure",
        "Mobile application not syncing data",
        "VoIP phone system issues",
        "VPN connection problems for remote employees",
        "System updates causing compatibility issues",
        "File server running out of storage space",
        "Intrusion detection system alerts",
        "Inventory management system errors",
        "Customer data not loading in CRM",
        "Collaboration tool not sending notifications",
    ]
    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
    }
    st.session_state.df = pd.DataFrame(data)

# Add ticket
st.header("Add a ticket")
with st.form("add_ticket_form"):
    issue = st.text_area("Describe the issue")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Submit")

if submitted:
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
            }
        ]
    )
    st.write("Ticket submitted! Here are the ticket details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Edit/view
st.header("Existing tickets")
st.write(f"Number of tickets: `{len(st.session_state.df)}`")
st.info(
    "You can edit the tickets by double clicking on a cell. Note how the plots below "
    "update automatically! You can also sort the table by clicking on the column headers.",
    icon="✍️",
)
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
    },
    disabled=["ID", "Date Submitted"],
)

# Stats
st.header("Statistics")
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="Number of open tickets", value=num_open_tickets, delta=10)
col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
col3.metric(label="Average resolution time (hours)", value=16, delta=2)

st.write("")
st.write("##### Ticket status per month")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5)
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Current ticket priorities")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5)
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
