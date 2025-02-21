import streamlit as st
from groq import Groq
import re
import requests  # Para buscar dados da web (SerpAPI)
from streamlit_feedback import streamlit_feedback  # Para coleta de feedback
import trubrics  # Para armazenar feedbacks

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
    st.header("🔧 Configurações")
    groq_api_key = st.text_input("🔑 Chave da API Groq", key="chatbot_api_key", type="password")
    modelo_escolhido = st.selectbox("📌 Escolha o modelo da Groq:", MODELOS_GROQ, index=0)
    serpapi_key = st.text_input("🌎 Chave da API SerpAPI (opcional para buscas na web)", type="password")
    ativar_busca_web = st.checkbox("🔍 Buscar na web se necessário")
    
    # Links úteis
    "[📜 Ver código-fonte](https://github.com/seu-repositorio)"
    "[💡 Obter API da Groq](https://platform.groq.com/account/api-keys)"
    "[🌎 Criar conta na SerpAPI](https://serpapi.com/)"

# Título do aplicativo
st.title("💬 Chatbot com Jeremy")
st.caption("🚀 Chatbot interativo com IA da Groq e busca na web")

# Inicialização do estado de sessão para mensagens e resposta do arquivo
if "mensagens" not in st.session_state:
    st.session_state["mensagens"] = [{"role": "assistant", "content": "Como posso ajudar você?"}]
if "resposta" not in st.session_state:
    st.session_state["resposta"] = None

# Exibição de mensagens já presentes no estado de sessão
for msg in st.session_state.mensagens:
    st.chat_message(msg["role"]).write(msg["content"])

# Função para buscar informações na web usando SerpAPI
def buscar_na_web(consulta):
    if not serpapi_key:
        return "⚠️ A busca na web está ativada, mas a chave da API SerpAPI não foi fornecida."
    
    url = "https://serpapi.com/search"
    params = {
        "q": consulta,
        "hl": "pt",
        "gl": "br",
        "api_key": serpapi_key
    }

    try:
        resposta = requests.get(url, params=params)
        dados = resposta.json()
        
        # Pegar os 3 primeiros resultados da pesquisa
        resultados = dados.get("organic_results", [])
        resposta_busca = "\n".join([f"{r['title']}: {r['link']}" for r in resultados[:3]])

        return resposta_busca if resposta_busca else "❌ Nenhum resultado encontrado."
    except Exception as e:
        return f"❌ Erro ao buscar na web: {e}"

# Upload de arquivo
uploaded_file = st.file_uploader("📂 Faça upload de um arquivo (.txt, .md)", type=["txt", "md"])

if uploaded_file:
    article = uploaded_file.read().decode()
    st.session_state["artigo"] = article
    st.write("✅ Arquivo carregado com sucesso!")

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

    # Se a busca na web estiver ativada, buscar antes de consultar o chatbot
    resposta_web = ""
    if ativar_busca_web:
        resposta_web = buscar_na_web(prompt)

    # Se o usuário subiu um arquivo, permitir perguntas sobre ele
    if uploaded_file:
        prompt = f"Aqui está um artigo:\n\n<article>\n{st.session_state['artigo']}\n</article>\n\n{prompt}"

    # Obter resposta do assistente virtual Jeremy
    try:
        completion = client.chat.completions.create(
            model=modelo_escolhido,
            messages=st.session_state.mensagens,
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stream=True,
            stop=None,
        )

        resposta_completa = "".join([chunk.choices[0].delta.content or "" for chunk in completion])
        resposta_limpa = re.sub(r"<think>.*?</think>", "", resposta_completa, flags=re.DOTALL).strip()

        if ativar_busca_web and resposta_web:
            resposta_limpa += f"\n\n🌎 Informações adicionais encontradas na web:\n{resposta_web}"

    except Exception as e:
        resposta_limpa = f"❌ Erro ao obter resposta: {e}"

    st.session_state.mensagens.append({"role": "assistant", "content": resposta_limpa})
    st.chat_message("assistant").write(resposta_limpa)

    st.session_state["resposta"] = resposta_limpa

# Feedback do usuário
if st.session_state["resposta"]:
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Opcional] Explique sua avaliação",
        key=f"feedback_{len(st.session_state['mensagens'])}",
    )

    if feedback and "TRUBRICS_EMAIL" in st.secrets:
        config = trubrics.init(
            email=st.secrets.TRUBRICS_EMAIL,
            password=st.secrets.TRUBRICS_PASSWORD,
        )
        collection = trubrics.collect(
            component_name="default",
            model="gpt",
            response=feedback,
            metadata={"chat": st.session_state["mensagens"]},
        )
        trubrics.save(config, collection)
        st.toast("✅ Feedback registrado!", icon="📝")
