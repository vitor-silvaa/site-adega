import sqlite3
from datetime import datetime


# ==================================
# CONEXÃO COM O BANCO
# ==================================

def conectar():
    conn = sqlite3.connect("produtos.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ==================================
# CRIAR E ATUALIZAR TABELAS
# ==================================

def criar_tabela():

    conn = conectar()
    cursor = conn.cursor()

    # Tabela de produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)

    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(produtos)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]

    # Adicionar estoque sem apagar os produtos existentes
    if "estoque" not in colunas:
        cursor.execute("""
            ALTER TABLE produtos
            ADD COLUMN estoque INTEGER NOT NULL DEFAULT 0
        """)

    if "estoque_minimo" not in colunas:
        cursor.execute("""
            ALTER TABLE produtos
            ADD COLUMN estoque_minimo INTEGER NOT NULL DEFAULT 5
        """)

    # Tabela de movimentações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data_hora TEXT NOT NULL,

            FOREIGN KEY (produto_id)
            REFERENCES produtos(id)
            ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ==================================
# CADASTRAR PRODUTO
# ==================================

def cadastrar_produto(nome, preco, categoria, estoque=0, estoque_minimo=5):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO produtos
        (name, price, category, estoque, estoque_minimo)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, preco, categoria, estoque, estoque_minimo))

    conn.commit()
    conn.close()


# ==================================
# LISTAR PRODUTOS
# ==================================

def listar_produtos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, price, category, estoque, estoque_minimo
        FROM produtos
    """)

    produtos = cursor.fetchall()

    conn.close()

    return produtos


# ==================================
# EDITAR PRODUTO
# ==================================

def editar_produto(id, nome, preco, categoria):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE produtos
        SET name = ?, price = ?, category = ?
        WHERE id = ?
    """, (nome, preco, categoria, id))

    conn.commit()
    conn.close()


# ==================================
# EXCLUIR PRODUTO
# ==================================

def excluir_produto(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM produtos
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()


# ==================================
# REGISTRAR MOVIMENTAÇÃO
# ==================================

def registrar_movimentacao(produto_id, tipo, quantidade):

    if tipo not in ("Entrada", "Saída"):
        raise ValueError("Tipo de movimentação inválido.")

    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    conn = conectar()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT estoque
            FROM produtos
            WHERE id = ?
        """, (produto_id,))

        produto = cursor.fetchone()

        if produto is None:
            raise ValueError("Produto não encontrado.")

        estoque_atual = produto[0]

        if tipo == "Saída":

            if quantidade > estoque_atual:
                raise ValueError("Estoque insuficiente!")

            novo_estoque = estoque_atual - quantidade

        else:

            novo_estoque = estoque_atual + quantidade

        # Atualizar estoque
        cursor.execute("""
            UPDATE produtos
            SET estoque = ?
            WHERE id = ?
        """, (novo_estoque, produto_id))

        # Registrar histórico
        cursor.execute("""
            INSERT INTO movimentacoes
            (produto_id, tipo, quantidade, data_hora)
            VALUES (?, ?, ?, ?)
        """, (
            produto_id,
            tipo,
            quantidade,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ))

        conn.commit()

        return novo_estoque

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ==================================
# HISTÓRICO DE MOVIMENTAÇÕES
# ==================================

def listar_movimentacoes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            movimentacoes.id,
            produtos.name,
            movimentacoes.tipo,
            movimentacoes.quantidade,
            movimentacoes.data_hora

        FROM movimentacoes

        INNER JOIN produtos
        ON produtos.id = movimentacoes.produto_id

        ORDER BY movimentacoes.id DESC
    """)

    movimentacoes = cursor.fetchall()

    conn.close()

    return movimentacoes