import streamlit as st
from datetime import datetime
import zoneinfo

# Configuração da página
st.set_page_config(page_title="Operações CD", layout="wide")

# Função para pegar a hora certa de Brasília
def obter_hora_brasil():
    fuso_sp = zoneinfo.ZoneInfo("America/Sao_Paulo")
    return datetime.now(fuso_sp)

st.title("📦 Sistema de Operações do CD")

# Exibe a data e hora atualizada no fuso correto
agora = obter_hora_brasil()
st.write(f"**Data e Hora atual:** {agora.strftime('%d/%m/%Y %H:%M:%S')}")

st.divider()

# Espaço para você começar a colocar suas novas funções reais do CD
st.info("Sistema zerado e pronto para receber os dados reais do CD.")
