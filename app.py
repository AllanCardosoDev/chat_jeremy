import streamlit as st
from groq import Groq
import re  # Biblioteca para remover padrões indesejados na resposta

# Modelos disponíveis na Groq
MODELOS_GROQ = [
    "gema2-9b-isto",
    "llama-3.3-70b-versátil",
    "llama-3.1-8b-instant",
    "guarda-lhama-3-8b",
    "lhama3-70b-8192",
    "lhama3-8b-8192",
    "mixtral-8x7b-32768",
    "sussurro-grande-v3",
    "sussurro-grande-v3-turbo",
]

# Configuração da barra lateral
with st.sidebar:
    st.header("🔧 Configurações")
    groq_api_key = st.text_input("🔑 Chave da API Groq", key="chatbot_api_key", type="password")
    modelo_escolhido = st.selectbox("📌 Escolha o modelo da Groq:", MODELOS_GROQ, index=0)

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
        st.info("⚠️ Por favor, adicione sua chave de API Groq para continuar.")
        st.stop()

    # Inicializar o cliente Groq
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        st.error(f"❌ Erro ao inicializar o cliente Groq: {e}")
        st.stop()

    # Adicionar mensagem do usuário ao estado de sessão e exibi-la
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Obter resposta do assistente virtual Jeremy
    try:
        completion = client.chat.completions.create(
            model=modelo_escolhido,  # Utilizando o modelo escolhido na interface
            messages=st.session_state.mensagens,
            temperature=0.5,
            max_tokens=5000,
            top_p=0.65,
            stream=True,
            stop=None,
        )

        # Processamento correto da resposta
        resposta_completa = "".join([chunk.choices[0].delta.content or "" for chunk in completion])

        # Filtrando qualquer texto dentro de <think>...</think>
        resposta_limpa = re.sub(r"<think>.*?</think>", "", resposta_completa, flags=re.DOTALL).strip()

    except Exception as e:
        resposta_limpa = f"❌ Erro ao obter resposta: {e}"

    # Adicionar e exibir a resposta do assistente sem <think>
    st.session_state.mensagens.append({"role": "assistant", "content": resposta_limpa})
    st.chat_message("assistant").write(resposta_limpa)
