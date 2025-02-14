import streamlit as st
from groq import Groq

# Configuração da barra lateral para inserção da chave da API
with st.sidebar:
    groq_api_key = st.text_input("Chave da API Groq", key="chatbot_api_key", type="password")

# Título do aplicativo
st.title("💬 Chatbot com Jeremy")
st.caption("🚀 Um chatbot interativo utilizando a API da Groq")

# Inicialização do estado de sessão para mensagens
if "mensagens" not in st.session_state:
    st.session_state["mensagens"] = [{"role": "assistant", "content": "Como posso ajudar você?"}]

# Exibição de mensagens já presentes no estado de sessão
for msg in st.session_state.mensagens:
    st.chat_message(msg["role"]).write(msg["content"])

# Entrada do usuário para o chat
if prompt := st.chat_input("Digite sua mensagem aqui"):
    if not groq_api_key:
        st.info("Por favor, adicione sua chave de API Groq para continuar.")
        st.stop()

    # Inicializar o cliente Groq
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        st.error(f"Erro ao inicializar o cliente Groq: {e}")
        st.stop()

    # Adicionar mensagem do usuário ao estado de sessão e exibi-la
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Obter resposta do assistente virtual Jeremy
    try:
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=st.session_state.mensagens,
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stream=True,
            stop=None,
        )
        resposta = "".join([chunk.choices[0].delta.content or "" for chunk in completion])
    except Exception as e:
        resposta = f"Erro ao obter resposta: {e}"

    # Adicionar e exibir a resposta do assistente
    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").write(resposta)
