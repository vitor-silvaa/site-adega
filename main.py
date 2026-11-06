import streamlit as st
from dbProdutos import produtos

# Inicializando o carrinho
if 'cart' not in st.session_state:
    st.session_state.cart = []

st.title("🛒 PitStop guará")
categories = list(set(p["category"] for p in produtos))
selected_category = st.selectbox("Escolha a categoria:", ["Todos"] + categories)

if selected_category == "Todos":
    filtered_products = produtos  # Mostra todos
else:
    filtered_products = [p for p in produtos if p["category"] == selected_category]

# Exibir os produtos filtrados
for product in filtered_products:
    # Criando colunas
    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(f"**{product['name']}** - R$ {product['price']:.2f}")

    
