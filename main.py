import streamlit as st
import db

st.set_page_config(
    page_title="Adega Filho Da Mãe",
    page_icon="🍻",
    layout="wide"
)

db.criar_tabela()


# ==================================
# SISTEMA DE NOTIFICAÇÕES
# ==================================

def notificacao_sucesso(mensagem):
    st.session_state["mensagem_sucesso"] = mensagem


if "mensagem_sucesso" in st.session_state:

    st.success(f"✅ {st.session_state.mensagem_sucesso}")

    del st.session_state["mensagem_sucesso"]


# ==================================
# CONTROLE DE ACESSO
# ==================================

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False

if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = "cliente"


# ==================================
# MENU LATERAL
# ==================================

st.sidebar.title("🍻 Adega Filho Da Mãe")

st.sidebar.divider()

if st.session_state.usuario_logado:

    st.sidebar.success("Administrador conectado")

    if st.sidebar.button("🚪 Sair do painel"):

        st.session_state.usuario_logado = False
        st.session_state.tipo_usuario = "cliente"

        st.rerun()

    pagina = st.sidebar.radio(
    "Painel administrativo",
    [
        "Dashboard",
        "Produtos",
        "Cadastrar",
        "Editar",
        "Excluir",
        "Gerenciar Estoque"
    ]
)

else:

    pagina = st.sidebar.radio(
        "Navegação",
        [
            "Início",
            "Produtos",
            "Login administrativo"
        ]
    )


# ==================================
# CARREGAR PRODUTOS E FILTROS
# ==================================

produtos = db.listar_produtos()


def filtrar_produtos(produtos):
    busca = st.text_input("🔎 Pesquisar produto")
    categorias = sorted(set(p[3] for p in produtos))

    categoria = st.selectbox(
        "📂 Categoria",
        ["Todas"] + categorias
    )

    filtrados = produtos

    if busca:
        filtrados = [
            p for p in filtrados
            if busca.casefold() in p[1].casefold()
        ]

    if categoria != "Todas":
        filtrados = [
            p for p in filtrados
            if p[3] == categoria
        ]

    return filtrados


# ==================================
# ÁREA DO CLIENTE
# ==================================

if not st.session_state.usuario_logado:

    # INÍCIO
    if pagina == "Início":

        st.title("🍻 Adega Filho Da Mãe")

        st.subheader("Bem-vindo à nossa loja!")

        st.write(
            "Encontre seus produtos favoritos "
            "de maneira rápida e prática."
        )

        st.info("Acesse a aba Produtos para visualizar nosso catálogo.")


    # PRODUTOS
    elif pagina == "Produtos":

        st.title("🛍️ Nosso catálogo")

        if produtos:

            filtrados = filtrar_produtos(produtos)

            st.divider()

            st.write(
                f"**{len(filtrados)} produto(s) encontrado(s)**"
            )

            if filtrados:

                for produto in filtrados:

                    id, nome, preco, categoria, estoque, estoque_minimo = produto

                    with st.container(border=True):

                        col1, col2, col3 = st.columns([4, 2, 2])

                        with col1:
                            st.markdown(f"**{nome}**")

                        with col2:
                            st.write(f"R$ {preco:.2f}")

                        with col3:
                            st.caption(f"📂 {categoria}")

            else:

                st.warning("Nenhum produto encontrado.")

        else:

            st.info("Nenhum produto disponível no momento.")

    # LOGIN ADMINISTRATIVO
    elif pagina == "Login administrativo":

        st.title("🔐 Login administrativo")
        st.write("Entre com suas credenciais para acessar o painel da loja.")

        with st.form("form_login_admin"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

        if entrar:
            try:
                credenciais = st.secrets["admin"]
                usuario_correto = credenciais["usuario"]
                senha_correta = credenciais["senha"]

                if usuario == usuario_correto and senha == senha_correta:
                    st.session_state.usuario_logado = True
                    st.session_state.tipo_usuario = "admin"
                    notificacao_sucesso("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

            except (KeyError, FileNotFoundError):
                st.error(
                    "Credenciais administrativas não configuradas. "
                    "Verifique o arquivo .streamlit/secrets.toml."
                )


# ==================================
# ÁREA ADMINISTRATIVA
# ==================================

else:

    # DASHBOARD
    if pagina == "Dashboard":

        st.title("⚙️ Painel administrativo")

        st.subheader("Visão geral da loja")

        categorias = set(p[3] for p in produtos)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de produtos", len(produtos))

        with col2:
            st.metric("Categorias", len(categorias))

        with col3:
            st.metric(
                "Valor total do catálogo",
                f"R$ {sum(p[2] for p in produtos):.2f}"
            )

        st.divider()

        st.subheader("Últimos produtos cadastrados")

        for produto in produtos[-5:]:

            id, nome, preco, categoria, estoque, estoque_minimo = produto

            st.write(f"**{nome}** | R$ {preco:.2f} | {categoria}")


    # VISUALIZAR PRODUTOS
    elif pagina == "Produtos":

        st.title("📦 Gerenciar catálogo")

        if produtos:

            filtrados = filtrar_produtos(produtos)

            for produto in filtrados:

                id, nome, preco, categoria, estoque, estoque_minimo = produto

                with st.container(border=True):

                    st.write(f"**{nome}**")

                    st.write(f"R$ {preco:.2f}")

                    st.caption(categoria)

        else:

            st.info("Nenhum produto cadastrado.")


    # CADASTRAR
    elif pagina == "Cadastrar":

        st.title("➕ Cadastrar produto")

        categorias = sorted(set(p[3] for p in produtos))

        with st.form("cadastro"):

            nome = st.text_input("Nome do produto")

            preco = st.number_input(
                "Preço",
                min_value=0.01,
                step=0.50
            )

            categoria_escolhida = st.selectbox(
                "Categoria",
                ["Selecionar categoria"] + categorias + ["Nova categoria"]
            )

            cadastrar = st.form_submit_button("Cadastrar produto")

            # Categoria nova
            if categoria_escolhida == "Nova categoria":

                categoria = st.text_input("Digite a nova categoria")

            elif categoria_escolhida == "Selecionar categoria":

                categoria = ""

            else:

                categoria = categoria_escolhida

            if cadastrar:

                if not nome.strip() or not categoria.strip():

                    st.error("Preencha todos os campos!")

                else:

                    duplicado = any(
                        p[1].strip().casefold() == nome.strip().casefold()
                        for p in produtos
                    )

                    if duplicado:

                        st.error("Este produto já está cadastrado!")

                    else:

                        db.cadastrar_produto(
                            nome.strip(),
                            preco,
                            categoria.strip()
                        )

                        notificacao_sucesso(
                            "Produto cadastrado com sucesso!"
                        )

                        st.rerun()


    # EDITAR
    elif pagina == "Editar":

        st.title("✏️ Editar produtos")

        if produtos:

            filtrados = filtrar_produtos(produtos)

            if filtrados:

                selecionado = st.selectbox(
                    "Selecione o produto",
                    filtrados,
                    format_func=lambda p: f"{p[1]} | R$ {p[2]:.2f}"
                )

                id, nome, preco, categoria, estoque, estoque_minimo = selecionado

                with st.form("editar"):

                    novo_nome = st.text_input(
                        "Nome",
                        value=nome
                    )

                    novo_preco = st.number_input(
                        "Preço",
                        min_value=0.01,
                        value=float(preco)
                    )

                    nova_categoria = st.text_input(
                        "Categoria",
                        value=categoria
                    )

                    salvar = st.form_submit_button("Salvar alterações")

                    if salvar:

                        if not novo_nome.strip() or not nova_categoria.strip():

                            st.error("Preencha todos os campos!")

                        else:

                            duplicado = any(
                                p[1].strip().casefold() == novo_nome.strip().casefold()
                                and p[0] != id
                                for p in produtos
                            )

                            if duplicado:

                                st.error("Já existe outro produto com esse nome!")

                            else:

                                db.editar_produto(
                                    id,
                                    novo_nome.strip(),
                                    novo_preco,
                                    nova_categoria.strip()
                                )

                                notificacao_sucesso(
                                    "Produto atualizado com sucesso!"
                                )

                                st.rerun()

        else:

            st.info("Nenhum produto cadastrado.")


    # EXCLUIR
    elif pagina == "Excluir":

        st.title("🗑️ Excluir produtos")

        if produtos:

            filtrados = filtrar_produtos(produtos)

            if filtrados:

                selecionado = st.selectbox(
                    "Selecione o produto",
                    filtrados,
                    format_func=lambda p: f"{p[1]} | R$ {p[2]:.2f}"
                )

                id, nome, preco, categoria, estoque, estoque_minimo = selecionado

                st.warning(
                    f"Você está prestes a excluir: **{nome}**"
                )

                confirmar = st.checkbox(
                    "Confirmo a exclusão deste produto."
                )

                if st.button(
                    "🗑️ Excluir produto",
                    disabled=not confirmar
                ):

                    db.excluir_produto(id)

                    notificacao_sucesso(
                        "Produto excluído com sucesso!"
                    )

                    st.rerun()

        else:

            st.info("Nenhum produto cadastrado.")


    # ==================================
    # GERENCIAR ESTOQUE
    # ==================================
    elif pagina == "Gerenciar Estoque":

        st.title("📦 Gerenciamento de Estoque")
        produtos = db.listar_produtos()

        if produtos:
            total_itens = sum(p[4] for p in produtos)

            # Valor total: preço unitário multiplicado pela quantidade em estoque
            valor_total_estoque = sum(
                float(p[2]) * int(p[4])
                for p in produtos
            )

            estoque_baixo = sum(1 for p in produtos if 0 < p[4] <= p[5])
            esgotados = sum(1 for p in produtos if p[4] == 0)

            # Formatação do valor em reais (padrão brasileiro)
            valor_formatado = (
                f"R$ {valor_total_estoque:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 Itens em estoque", total_itens)
            col2.metric("💰 Valor total do estoque", valor_formatado)
            col3.metric("⚠️ Estoque baixo", estoque_baixo)
            col4.metric("❌ Esgotados", esgotados)

            st.divider()
            st.subheader("🔄 Registrar movimentação")

            with st.form("form_movimentacao"):
                selecionado = st.selectbox(
                    "Produto",
                    produtos,
                    format_func=lambda p: f"{p[1]} | Estoque: {p[4]}"
                )

                id_produto, nome, preco, categoria, estoque, estoque_minimo = selecionado
                st.info(f"Estoque atual de {nome}: {estoque} unidades")

                tipo = st.selectbox("Movimentação", ["Entrada", "Saída"])
                quantidade = st.number_input("Quantidade", min_value=1, step=1)

                registrar = st.form_submit_button(
                    "Registrar movimentação",
                    use_container_width=True
                )

                if registrar:
                    try:
                        novo_estoque = db.registrar_movimentacao(
                            id_produto, tipo, int(quantidade)
                        )
                        notificacao_sucesso(
                            f"{tipo} registrada! Novo estoque de {nome}: "
                            f"{novo_estoque} unidades."
                        )
                        st.rerun()
                    except ValueError as erro:
                        st.error(str(erro))

            st.divider()
            st.subheader("📋 Estoque atual")

            for p in produtos:
                id_produto, nome, preco, categoria, estoque, estoque_minimo = p

                if estoque == 0:
                    status = "🔴 Esgotado"
                elif estoque <= estoque_minimo:
                    status = "🟡 Estoque baixo"
                else:
                    status = "🟢 Disponível"

                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    col1.write(f"**{nome}**")
                    col2.write(f"📦 {estoque} unidades")
                    col3.write(f"Mínimo: {estoque_minimo}")
                    col4.write(status)

            st.divider()
            st.subheader("📜 Histórico de movimentações")
            movimentacoes = db.listar_movimentacoes()

            if movimentacoes:
                st.dataframe(
                    [
                        {
                            "Produto": m[1],
                            "Tipo": m[2],
                            "Quantidade": m[3],
                            "Data e horário": m[4]
                        }
                        for m in movimentacoes
                    ],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhuma movimentação registrada.")
        else:
            st.warning("Cadastre produtos antes de movimentar o estoque.")

