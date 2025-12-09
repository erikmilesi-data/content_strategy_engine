import sqlite3
from pathlib import Path
import json
from datetime import datetime
from typing import Optional

from src.core.security import get_password_hash

DB_PATH = Path(__file__).resolve().parent / "history.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Inicializa o banco SQLite simples (usuários + histórico de análises).
    Garante criação de tabelas e usuário admin padrão.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # ---- Criação da tabela principal (com project_id) ----
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                topic TEXT,
                platform TEXT,
                mode TEXT,
                users_json TEXT,
                result_json TEXT,
                username TEXT,
                project_id INTEGER
            );
            """
        )

        # ---- Verificar colunas existentes (para bases antigas) ----
        cursor.execute("PRAGMA table_info(analysis_history)")
        columns = [col[1] for col in cursor.fetchall()]

        if "username" not in columns:
            cursor.execute("ALTER TABLE analysis_history ADD COLUMN username TEXT;")

        if "project_id" not in columns:
            cursor.execute(
                "ALTER TABLE analysis_history ADD COLUMN project_id INTEGER;"
            )

        # ---- Tabela de usuários ----
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            """
        )

        # ---- Usuário padrão ----
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        row = cursor.fetchone()

        if row["total"] == 0:
            hashed_admin = get_password_hash("admin123")
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("admin", hashed_admin),
            )

        conn.commit()


# ------------------------------------------------------------
#   SALVAR ANÁLISE
# ------------------------------------------------------------
def save_analysis(
    username: str,
    topic,
    platform,
    mode,
    users,
    result,
    project_id: Optional[int] = None,
):
    """
    Salva a análise associada ao usuário (e opcionalmente a um projeto).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_history (
                timestamp,
                topic,
                platform,
                mode,
                users_json,
                result_json,
                username,
                project_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                topic,
                platform,
                mode,
                json.dumps(users, ensure_ascii=False),
                json.dumps(result, ensure_ascii=False),
                username,
                project_id,
            ),
        )
        conn.commit()


# ------------------------------------------------------------
#   LISTAR HISTÓRICO DO USUÁRIO
# ------------------------------------------------------------
def list_history(
    username: str,
    limit: int = 50,
    project_id: Optional[int] = None,
):
    """
    Lista histórico do usuário, opcionalmente filtrando por projeto.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        base_query = """
            SELECT id, timestamp, topic, platform, mode, project_id
            FROM analysis_history
            WHERE username = ?
        """
        params = [username]

        if project_id is not None:
            base_query += " AND project_id = ?"
            params.append(project_id)

        base_query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor.execute(base_query, params)
        rows = cursor.fetchall()

    return rows


# ------------------------------------------------------------
#   CARREGAR ENTRADA ESPECÍFICA DO USUÁRIO
# ------------------------------------------------------------
def load_entry(username: str, entry_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM analysis_history
            WHERE id = ? AND username = ?
            """,
            (entry_id, username),
        )
        row = cursor.fetchone()
    return row


# ------------------------------------------------------------
#   BUSCAR USUÁRIO
# ------------------------------------------------------------
def get_user_by_username(username: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM users WHERE username = ?
            """,
            (username,),
        )
        row = cursor.fetchone()
    return row


# ------------------------------------------------------------
#   CRIAR USUÁRIO
# ------------------------------------------------------------
def create_user(username: str, hashed_password: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password)
            VALUES (?, ?)
            """,
            (username, hashed_password),
        )
        conn.commit()
        user_id = cursor.lastrowid

    # Mantemos um dict semelhante ao Row
    return {"id": user_id, "username": username, "password": hashed_password}
