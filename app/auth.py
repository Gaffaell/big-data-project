
import hashlib


USERS = {
    "matheus@gmail.com": hashlib.sha256("123456".encode()).hexdigest(),
}

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def verify_credentials(email: str, password: str) -> bool:
    if not email or not password:
        return False
    stored = USERS.get(email.strip().lower())
    return stored is not None and stored == sha256(password)

def is_authenticated(session) -> bool:
    return bool(session.get("auth") and session.get("user"))

def login(session, email: str):
    session["auth"] = True
    session["user"] = email
    session["display_name"] = email.split("@")[0].title()

def logout(session):
    for k in ("auth", "user", "display_name"):
        session.pop(k, None)
