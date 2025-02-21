import streamlit as st
from groq import Groq
import re  # Biblioteca para remover padrões indesejados na resposta
from PIL import Image
import numpy as np

# Modelos disponíveis na Groq
MODELOS_GROQ = [
    "qwen-2.5-32b",
    "deepseek-r1-distill-qwen-32b",
    "deepseek-r1-distill-llama-70b-specdec",
    "deepseek-r1-distill-llama-70b",
    "llama-3.3-70b-specdec",
    "llama-3.2-1b-preview",
    "llama-3.2-3b-preview",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
]

# Configuração da barra lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    groq_api_key = st.text_input("🔑 Chave da API Groq", key="chatbot_api_key", type="password")
    modelo_escolhido = st.selectbox("🧠 Escolha o modelo da Groq:", MODELOS_GROQ, index=0)

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
        st.info("❗ Por favor, adicione sua chave de API Groq para continuar.")
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
            max_tokens=1024,
            top_p=0.65,
            stream=False,  # Corrigido para não precisar processar chunk de resposta
            stop=None,
        )

        # Pegando a resposta do modelo corretamente
        resposta_completa = completion.choices[0].message.content

        # Removendo qualquer texto indesejado (caso queira filtrar algo específico)
        resposta_limpa = re.sub(r"<[^>]*>", "", resposta_completa, flags=re.DOTALL).strip()

    except Exception as e:
        resposta_limpa = f"❌ Erro ao obter resposta: {e}"

    # Adicionar e exibir a resposta do assistente
    st.session_state.mensagens.append({"role": "assistant", "content": resposta_limpa})
    st.chat_message("assistant").write(resposta_limpa)

# Upload de imagem
uploaded_image = st.file_uploader("📤 Upload de imagem", type=["jpg", "png", "jpeg"])

if uploaded_image:
    # Carregar a imagem
    image = Image.open(uploaded_image)

    # Exibir a imagem carregada
    st.image(image, caption="🖼️ Imagem carregada", use_column_width=True)

    # Converter a imagem para array NumPy
    image_array = np.array(image)

    # Enviar a imagem para o modelo
    try:
        completion = client.chat.completions.create(
            model=modelo_escolhido,  # Utilizando o modelo escolhido na interface
            messages=[{"role": "user", "content": "Descreva essa imagem"}],
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stop=None,
            files=[{"name": uploaded_image.name, "content": uploaded_image.read()}]  # Ajustado para o formato correto
        )

        # Pegando a resposta do modelo corretamente
        resposta_imagem = completion.choices[0].message.content

    except Exception as e:
        resposta_imagem = f"❌ Erro ao processar a imagem: {e}"

    # Exibir a resposta da IA sobre a imagem
    st.subheader("🔍 Resumo da Imagem")
    st.write(resposta_imagem)
