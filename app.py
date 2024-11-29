import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Inicializar o cliente da API Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Função para obter resposta da API Groq
def get_groq_response(messages):
    try:
        completion = client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stream=True,
            stop=None,
        )

        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        return response

    except Exception as err:
        return f"Erro: {err}"

# Função para a página de chat
def pagina_chat():
    st.header('🤖 Bem-vindo ao Jeremy', divider=True)

    if 'mensagens' not in st.session_state:
        st.session_state['mensagens'] = []
        # Adicionando uma mensagem inicial do assistente Jeremy
        st.session_state['mensagens'].append(('assistant', "Olá! Eu sou Jeremy, seu assistente virtual. Como posso ajudá-lo hoje?"))

    mensagens = st.session_state['mensagens']
    for mensagem in mensagens:
        chat = st.chat_message(mensagem[0])
        chat.markdown(mensagem[1])

    input_usuario = st.chat_input('Fale com o oráculo')
    if input_usuario:
        # Adicionar a mensagem do usuário à lista de mensagens
        mensagens.append(('user', input_usuario))
        
        # Preparar mensagens para a API
        formatted_messages = [{"role": "user", "content": msg[1]} for msg in mensagens if msg[0] == 'user']
        
        # Obter a resposta do Oráculo
        resposta_oraculo = get_groq_response(formatted_messages)
        
        # Adicionar a resposta do Oráculo à lista de mensagens
        mensagens.append(('assistant', resposta_oraculo))
        
        # Atualizar o estado da sessão
        st.session_state['mensagens'] = mensagens
        
        # Recarregar a interface
        st.rerun()

# Função principal
def main():
    pagina_chat()

if __name__ == '__main__':
    main()