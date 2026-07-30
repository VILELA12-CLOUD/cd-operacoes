import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import zoneinfo

# Configuração da página
st.set_page_config(page_title="Operações CD", layout="wide", initial_sidebar_state="expanded")

# Estilização
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .card-metric {
        background-color: white; padding: 18px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS PERMANENTE ---
DB_NAME = "operacoes_cd.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Motoboys cadastrados
    c.execute('''CREATE TABLE IF NOT EXISTS motoboys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE, placa TEXT, telefone TEXT)''')
    # Bipagem de Pacotes
    c.execute('''CREATE TABLE IF NOT EXISTS pacotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT, codigo TEXT, motoboy TEXT, hora TEXT, tipo TEXT)''')
    # Historico do dia a dia
    c.execute('''CREATE TABLE IF NOT EXISTS historico (
                    data TEXT PRIMARY KEY, total INTEGER, entregues INTEGER, 
                    insucessos INTEGER, taxa_sucesso REAL, faturamento REAL, 
                    pago_motos REAL, lucro REAL)''')
    conn.commit()
    conn.close()

init_db()

# Função para pegar a hora certa de Brasília
def obter_hora_brasil():
    fuso_sp = zoneinfo.ZoneInfo("America/Sao_Paulo")
    return datetime.now(fuso_sp)

# --- SESSÃO E NAVEGAÇÃO ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1

if 'motoboys_hoje' not in st.session_state:
    st.session_state.motoboys_hoje = []

if 'configs_motoboys' not in st.session_state:
    st.session_state.configs_motoboys = {}

# --- FUNÇÕES DE BIPAGEM COM BANCO DE DADOS ---
def add_pacote_saida():
    cod = st.session_state.input_bip_saida.strip()
    moto = st.session_state.get('moto_atual_sel', '')
    if cod and moto:
        conn = sqlite3.connect(DB_NAME)
        hoje_str = obter_hora_brasil().strftime("%Y-%m-%d")
        hora_str = obter_hora_brasil().strftime("%H:%M:%S")
        conn.execute("INSERT INTO pacotes (data, codigo, motoboy, hora, tipo) VALUES (?, ?, ?, ?, 'SAIDA')",
                     (hoje_str, cod, moto, hora_str))
        conn.commit()
        conn.close()
        st.session_state.input_bip_saida = ""

def add_pacote_insucesso():
    cod = st.session_state.input_bip_insucesso.strip()
    if cod:
        conn = sqlite3.connect(DB_NAME)
        hoje_str = obter_hora_brasil().strftime("%Y-%m-%d")
        hora_str = obter_hora_brasil().strftime("%H:%M:%S")
        conn.execute("INSERT INTO pacotes (data, codigo, motoboy, hora, tipo) VALUES (?, ?, 'SISTEMA', ?, 'INSUCESSO')",
                     (hoje_str, cod, hora_str))
        conn.commit()
        conn.close()
        st.session_state.input_bip_insucesso = ""

# --- NAVEGAÇÃO LATERAL ---
st.sidebar.markdown("<h2 style='color:#00C2FF;'>📦 CD Operações</h2>", unsafe_allow_html=True)

menu_opcoes = {
    1: "1️⃣ Dashboard",
    2: "2️⃣ Seleção de Motoboys",
    3: "3️⃣ Roteirização & Saída",
    4: "4️⃣ Bipagem de Insucessos",
    5: "5️⃣ Reconciliação",
    6: "6️⃣ Resumo Financeiro",
    7: "📊 Relatório Historico"
}

for num, nome in menu_opcoes.items():
    if st.sidebar.button(nome, use_container_width=True, type="primary" if st.session_state.etapa == num else "secondary"):
        st.session_state.etapa = num
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Zerar / Reiniciar Dia Atual", use_container_width=True):
    conn = sqlite3.connect(DB_NAME)
    hoje_str = obter_hora_brasil().strftime("%Y-%m-%d")
    conn.execute("DELETE FROM pacotes WHERE data = ?", (hoje_str,))
    conn.commit()
    conn.close()
    st.session_state.motoboys_hoje = []
    st.session_state.configs_motoboys = {}
    st.session_state.etapa = 1
    st.sidebar.success("Dia atual zerado!")
    st.rerun()

# ==========================================
# TELA 1: DASHBOARD
# ==========================================
if st.session_state.etapa == 1:
    st.title("📦 Sistema de Operações do CD")
    agora = obter_hora_brasil()
    st.write(f"**Data e Hora atual:** {agora.strftime('%d/%m/%Y %H:%M:%S')}")
    st.divider()
    
    st.subheader("Bom dia, futuros Milionários 🚀")
    st.write("Sistema zerado e pronto para receber os dados reais do CD.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Começar Uma Nova Rota", type="primary", use_container_width=True):
        st.session_state.etapa = 2
        st.rerun()

# ==========================================
# TELA 2: SELEÇÃO E CADASTRO DE MOTOBOYS
# ==========================================
elif st.session_state.etapa == 2:
    st.title("2️⃣ Seleção da Equipe do Dia")
    
    conn = sqlite3.connect(DB_NAME)
    df_cadastrados = pd.read_sql_query("SELECT nome, placa, telefone FROM motoboys", conn)
    conn.close()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("👥 Motoboys Cadastrados")
        nomes_disponiveis = df_cadastrados['nome'].tolist() if not df_cadastrados.empty else []
        
        if not nomes_disponiveis:
            st.info("Nenhum motoboy cadastrado ainda. Use o formulário ao lado para cadastrar.")
        
        selecionados = st.multiselect(
            "Marque os motoboys que vão trabalhar hoje:",
            options=nomes_disponiveis,
            default=st.session_state.motoboys_hoje
        )
        st.session_state.motoboys_hoje = selecionados

    with col2:
        st.subheader("➕ Cadastrar Novo Motoboy")
        with st.form("form_novo_moto", clear_on_submit=True):
            novo_nome = st.text_input("Nome Completo")
            nova_placa = st.text_input("Placa do Veículo")
            novo_tel = st.text_input("Telefone")
            if st.form_submit_button("Cadastrar Motoboy"):
                if novo_nome:
                    conn = sqlite3.connect(DB_NAME)
                    try:
                        conn.execute("INSERT INTO motoboys (nome, placa, telefone) VALUES (?, ?, ?)", 
                                     (novo_nome, nova_placa, novo_tel))
                        conn.commit()
                        st.success(f"{novo_nome} cadastrado com sucesso!")
                    except:
                        st.error("Motoboy já cadastrado!")
                    conn.close()
                    st.rerun()
                else:
                    st.error("Digite o nome do motoboy!")

    st.markdown("---")
    if st.button("Avançar para Roteirização ➡️", type="primary"):
        if not st.session_state.motoboys_hoje:
            st.warning("Selecione pelo menos 1 motoboy para continuar!")
        else:
            for m in st.session_state.motoboys_hoje:
                if m not in st.session_state.configs_motoboys:
                    st.session_state.configs_motoboys[m] = {"valor_pacote": 1.80, "obs": ""}
            st.session_state.etapa = 3
            st.rerun()

# ==========================================
# TELA 3: ROTEIRIZAÇÃO & BIPAGEM DE SAÍDA
# ==========================================
elif st.session_state.etapa == 3:
    st.title("3️⃣ Roteirização e Bipagem de Saída")
    
    if not st.session_state.motoboys_hoje:
        st.warning("Nenhum motoboy selecionado para o dia. Volte para a Tela 2.")
    else:
        moto_atual = st.selectbox("🎯 Escolha o Motoboy para Bipar:", st.session_state.motoboys_hoje, key='moto_atual_sel')
        
        if moto_atual:
            if moto_atual not in st.session_state.configs_motoboys:
                st.session_state.configs_motoboys[moto_atual] = {"valor_pacote": 1.80, "obs": ""}

            c_conf1, c_conf2 = st.columns([1, 2])
            with c_conf1:
                val_p = st.number_input(
                    f"Valor por Pacote ({moto_atual}):",
                    min_value=0.0, value=st.session_state.configs_motoboys[moto_atual]["valor_pacote"], step=0.10
                )
                st.session_state.configs_motoboys[moto_atual]["valor_pacote"] = val_p
            with c_conf2:
                obs_p = st.text_input(
                    f"Observações do dia ({moto_atual}):",
                    value=st.session_state.configs_motoboys[moto_atual]["obs"]
                )
                st.session_state.configs_motoboys[moto_atual]["obs"] = obs_p

            st.markdown("---")
            
            st.text_input(
                "📦 Bipe ou Digite o Código do Pacote e aperte ENTER:",
                key="input_bip_saida",
                on_change=add_pacote_saida
            )

            conn = sqlite3.connect(DB_NAME)
            hoje_str = obter_hora_brasil().strftime("%Y-%m-%d")
            df_pacotes_moto = pd.read_sql_query(
                "SELECT codigo, hora FROM pacotes WHERE data=? AND motoboy=? AND tipo='SAIDA'", 
                conn, params=(hoje_str, moto_atual)
            )
            conn.close()

            st.subheader(f"📋 Pacotes Bipados para {moto_atual}: {len(df_pacotes_moto)} volumes")
            if not df_pacotes_moto.empty:
                st.dataframe(df_pacotes_moto, use_container_width=True, hide_index=True)

    st.markdown("---")
    c_esp, c_btn = st.columns([3, 1])
    with c_btn:
        if st.button("Finalizar Rotas ➡️", type="primary", use_container_width=True):
            st.session_state.etapa = 4
            st.rerun()

# ==========================================
# TELA 4: BIPAGEM DE INSUCESSOS
# ==========================================
elif st.session_state.etapa == 4:
    st.title("4️⃣ Bipagem de Insucessos e Devoluções")
    
    st.text_input(
        "⚠️ Bipe ou Digite o Pacote Insucesso / Sobra e aperte ENTER:",
        key="input_bip_insucesso",
        on_change=add_pacote_insucesso
    )

    conn = sqlite3.connect(DB_NAME)
    hoje_str = obter_hora_brasil().strftime("%Y-%m-%d")
    df_ins = pd.read_sql_query("SELECT codigo, hora FROM pacotes WHERE data=? AND tipo='INSUCESSO'", conn, params=(hoje_str,))
    conn.close()

    st.subheader(f"🔴 Total de Insucessos Bipados: {len(df_ins)}")
    if not df_ins.empty:
        st.dataframe(df_ins[['codigo', 'hora']], use_container_width=True, hide_index=True)

    st.markdown("---")
    c_esp, c_btn = st.columns([3, 1])
    with c_btn:
        if st.button("Finalizar e Reconciliar ➡️", type="primary", use_container_width=True):
            st.session_state.etapa = 5
            st.rerun()

# ==========================================
# TELA 5: RECONCILIAÇÃO
# ==========================================
elif st.session_state.etapa == 5:
    st.title("5️⃣ Reconciliação de Entregas e Insucessos")
    
    conn = sqlite3.connect(DB_NAME)
    hoje_str = obter_hora_brasil().strftime("%Y-%m-%d")
    df_saidas = pd.read_sql_query("SELECT codigo, motoboy FROM pacotes WHERE data=? AND tipo='SAIDA'", conn, params=(hoje_str,))
    df_ins = pd.read_sql_query("SELECT codigo FROM pacotes WHERE data=? AND tipo='INSUCESSO'", conn, params=(hoje_str,))
    conn.close()

    insucessos_set = set(df_ins['codigo'].tolist()) if not df_ins.empty else set()
    
    lista_conferencia = []
    if not df_saidas.empty:
        for _, p in df_saidas.iterrows():
            foi_insucesso = p["codigo"] in insucessos_set
            lista_conferencia.append({
                "Código Pacote": p["codigo"],
                "Motoboy": p["motoboy"],
                "Status Final": "🔴 INSUCESSO / SOBRA" if foi_insucesso else "🟢 ENTREGUE COM SUCESSO",
                "Foi Insucesso?": foi_insucesso
            })
            
    df_conf = pd.DataFrame(lista_conferencia)
    
    st.subheader("🔍 Evidenciação dos Códigos")
    if not df_conf.empty:
        st.dataframe(df_conf[['Código Pacote', 'Motoboy', 'Status Final']], use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("💰 Pagamento dos Motoboys (Somente Sucessos)")
    
    resumo_motos = []
    for m in st.session_state.motoboys_hoje:
        df_m = df_conf[df_conf["Motoboy"] == m] if not df_conf.empty else pd.DataFrame()
        tot_saida = len(df_m)
        tot_insucesso = len(df_m[df_m["Foi Insucesso?"] == True]) if not df_m.empty else 0
        tot_entregue = tot_saida - tot_insucesso
        
        cfg = st.session_state.configs_motoboys.get(m, {"valor_pacote": 1.80, "obs": ""})
        taxa = cfg["valor_pacote"]
        obs = cfg["obs"]
        valor_final_pago = tot_entregue * taxa
        
        resumo_motos.append({
            "Motoboy": m,
            "Saíram": tot_saida,
            "Insucessos": tot_insucesso,
            "Entregues com Sucesso": tot_entregue,
            "Taxa Combinada": f"R$ {taxa:.2f}",
            "TOTAL A PAGAR": f"R$ {valor_final_pago:.2f}",
            "Observações": obs
        })
        
    st.dataframe(pd.DataFrame(resumo_motos), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    c_esp, c_btn = st.columns([3, 1])
    with c_btn:
        if st.button("Ir para Fechamento Financeiro ➡️", type="primary", use_container_width=True):
            st.session_state.etapa = 6
            st.rerun()

# ==========================================
# TELA 6: RESUMO FINANCEIRO DO DIA
# ==========================================
elif st.session_state.etapa == 6:
    st.title("6️⃣ Fechamento Financeiro do Dia")
    
    conn = sqlite3.connect(DB_NAME)
    hoje_str = obter_hora_brasil().strftime("%Y-%m-%d")
    df_s = pd.read_sql_query("SELECT codigo, motoboy FROM pacotes WHERE data=? AND tipo='SAIDA'", conn, params=(hoje_str,))
    df_i = pd.read_sql_query("SELECT codigo FROM pacotes WHERE data=? AND tipo='INSUCESSO'", conn, params=(hoje_str,))
    conn.close()

    tot_sairam = len(df_s)
    tot_insucessos = len(df_i)
    tot_entregues = max(0, tot_sairam - tot_insucessos)
    
    taxa_sucesso = (tot_entregues / tot_sairam * 100) if tot_sairam > 0 else 0.0
    
    st.subheader("📊 Números Gerais da Operação")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de Pacotes Bipados", f"{tot_sairam} un")
    m2.metric("Entregues com Sucesso", f"{tot_entregues} un")
    m3.metric("Insucessos / Sobras", f"{tot_insucessos} un")
    m4.metric("% Taxa de Sucesso", f"{taxa_sucesso:.1f}%")

    st.markdown("---")
    st.subheader("💵 Cálculo do Repasse Mercado Livre")
    
    fat_normal = (tot_entregues * 2.60) + (tot_insucessos * 1.30)
    fat_bonus = (tot_entregues * 2.90) + (tot_insucessos * 1.30)
    
    if taxa_sucesso >= 98.0 and tot_sairam > 0:
        st.success(f"🎉 PARABÉNS! Atingimos {taxa_sucesso:.1f}% de sucesso no dia (Meta 98% batida)!")
        c_val1, c_val2 = st.columns(2)
        with c_val1:
            st.markdown(f"<div class='card-metric'><h4>Valor Padrão (R$ 2,60)</h4><h2>R$ {fat_normal:.2f}</h2></div>", unsafe_allow_html=True)
        with c_val2:
            st.markdown(f"<div class='card-metric' style='border-color:#28C76F;'><h4>🌟 Com Bônus 98% (R$ 2,90)</h4><h2 style='color:#28C76F;'>R$ {fat_bonus:.2f}</h2></div>", unsafe_allow_html=True)
    else:
        st.info(f"Taxa de Sucesso: **{taxa_sucesso:.1f}%** (Para liberar a exibição do bônus de R$ 2,90 é necessário bater 98.0%).")
        st.markdown(f"<div class='card-metric'><h4>Faturamento do Dia (Mercado Livre)</h4><h2>R$ {fat_normal:.2f}</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salvar Dia no Histórico e Concluir", type="primary"):
        hoje_dt = obter_hora_brasil().date()
        
        # Calcular total pago aos motoboys
        pago_motos = 0.0
        ins_set = set(df_i['codigo'].tolist()) if not df_i.empty else set()
        
        for m in st.session_state.motoboys_hoje:
            df_m = df_s[df_s["motoboy"] == m] if not df_s.empty else pd.DataFrame()
            tot_s_m = len(df_m)
            tot_i_m = len([c for c in df_m['codigo'] if c in ins_set]) if not df_m.empty else 0
            tot_e_m = tot_s_m - tot_i_m
            
            taxa_m = st.session_state.configs_motoboys.get(m, {}).get("valor_pacote", 1.80)
            pago_motos += (tot_e_m * taxa_m)

        fat_final = fat_bonus if taxa_sucesso >= 98.0 else fat_normal
        lucro_final = fat_final - pago_motos

        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT OR REPLACE INTO historico VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     (hoje_dt.strftime("%d/%m/%Y"), tot_sairam, tot_entregues, tot_insucessos, round(taxa_sucesso, 1), round(fat_final, 2), round(pago_motos, 2), round(lucro_final, 2)))
        conn.commit()
        conn.close()
        st.success("Dia finalizado e salvo permanentemente no banco de dados com sucesso!")

# ==========================================
# TELA 7: RELATÓRIO HISTÓRICO PERMANENTE
# ==========================================
elif st.session_state.etapa == 7:
    st.title("📊 Relatório de Desempenho e Histórico")
    
    conn = sqlite3.connect(DB_NAME)
    df_hist = pd.read_sql_query("SELECT * FROM historico", conn)
    conn.close()

    st.subheader("Resultados Salvos no Banco de Dados")
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum histórico salvo ainda no banco de dados.")
