import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

# Configuração da página
st.set_page_config(page_title="CD Operações - Mercado Livre", layout="wide", initial_sidebar_state="expanded")

# Estilização
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .card-metric {
        background-color: white; padding: 18px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
    }
    .badge-success { background-color: #DEF7EC; color: #03543F; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-danger { background-color: #FDE8E8; color: #9B1C1C; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-warning { background-color: #FEF08A; color: #854D0E; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS NA MEMÓRIA ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1

if 'motoboys_cadastrados' not in st.session_state:
    st.session_state.motoboys_cadastrados = [
        {"Nome": "Carlos Silva", "Placa": "ABC-1234", "Telefone": "(11) 98765-4321"},
        {"Nome": "Rafael Santos", "Placa": "DEF-5678", "Telefone": "(11) 91234-5678"},
        {"Nome": "Lucas Oliveira", "Placa": "GHI-9012", "Telefone": "(11) 93456-7890"}
    ]

if 'motoboys_hoje' not in st.session_state:
    st.session_state.motoboys_hoje = []

if 'configs_motoboys' not in st.session_state:
    st.session_state.configs_motoboys = {}

if 'pacotes_saida' not in st.session_state:
    st.session_state.pacotes_saida = []

if 'pacotes_insucesso' not in st.session_state:
    st.session_state.pacotes_insucesso = []

# --- FUNÇÕES DE BIPAGEM AUTOMÁTICA ---
def add_pacote_saida():
    cod = st.session_state.input_bip_saida.strip()
    moto = st.session_state.get('moto_atual_sel', '')
    if cod and moto:
        st.session_state.pacotes_saida.append({
            "codigo": cod,
            "motoboy": moto,
            "hora": datetime.now().strftime("%H:%M:%S")
        })
        st.session_state.input_bip_saida = ""

def add_pacote_insucesso():
    cod = st.session_state.input_bip_insucesso.strip()
    if cod:
        st.session_state.pacotes_insucesso.append(cod)
        st.session_state.input_bip_insucesso = ""

# Dados fictícios para o histórico
if 'historico_40_dias' not in st.session_state:
    hoje = date.today()
    dados_hist = []
    np.random.seed(42)
    for i in range(40, 0, -1):
        dt = hoje - timedelta(days=i)
        tot = int(np.random.randint(180, 350))
        taxa = np.random.choice([0.985, 0.99, 0.97, 0.982, 0.96])
        entregues = int(tot * taxa)
        insucessos = tot - entregues
        pago_motos = entregues * 1.80
        fat_ml = (entregues * (2.90 if (entregues/tot) >= 0.98 else 2.60)) + (insucessos * 1.30)
        dados_hist.append({
            "Data": dt.strftime("%d/%m/%Y"),
            "Data_Obj": dt,
            "Total Pacotes": tot,
            "Entregues": entregues,
            "Insucessos": insucessos,
            "% Sucesso": round((entregues/tot)*100, 1),
            "Faturamento ML (R$)": round(fat_ml, 2),
            "Pago Motoboys (R$)": round(pago_motos, 2),
            "Lucro CD (R$)": round(fat_ml - pago_motos, 2)
        })
    st.session_state.historico_40_dias = pd.DataFrame(dados_hist)


# --- NAVEGAÇÃO LATERAL ---
st.sidebar.markdown("<h2 style='color:#00C2FF;'>📦 CD Operações</h2>", unsafe_allow_html=True)
st.sidebar.markdown("**Fluxo do Dia:**")

menu_opcoes = {
    1: "1️⃣ Dashboard",
    2: "2️⃣ Seleção de Motoboys",
    3: "3️⃣ Roteirização & Saída",
    4: "4️⃣ Bipagem de Insucessos",
    5: "5️⃣ Reconciliação",
    6: "6️⃣ Resumo Financeiro",
    7: "📊 Relatório (40 Dias)"
}

for num, nome in menu_opcoes.items():
    if st.sidebar.button(nome, use_container_width=True, type="primary" if st.session_state.etapa == num else "secondary"):
        st.session_state.etapa = num
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reiniciar Dia Atual", use_container_width=True):
    st.session_state.motoboys_hoje = []
    st.session_state.configs_motoboys = {}
    st.session_state.pacotes_saida = []
    st.session_state.pacotes_insucesso = []
    st.session_state.etapa = 1
    st.rerun()


# ==========================================
# TELA 1: DASHBOARD
# ==========================================
if st.session_state.etapa == 1:
    st.title("Bom dia, futuros Milionários 🚀")
    
    agora = datetime.now()
    st.markdown(f"### 📅 **Data:** {agora.strftime('%d/%m/%Y')} | ⏰ **Hora:** {agora.strftime('%H:%M:%S')}")
    st.write("Seja bem-vindo ao painel do CD. Clique no botão abaixo para começar a operação de hoje!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Começar Uma Nova Rota", type="primary", use_container_width=True):
        st.session_state.etapa = 2
        st.rerun()


# ==========================================
# TELA 2: SELEÇÃO E CADASTRO DE MOTOBOYS
# ==========================================
elif st.session_state.etapa == 2:
    st.title("2️⃣ Seleção da Equipe do Dia")
    st.write("Escolha os motoboys que vão pra rua hoje ou cadastre um novo parceiro.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("👥 Motoboys Cadastrados")
        nomes_disponiveis = [m["Nome"] for m in st.session_state.motoboys_cadastrados]
        
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
            if st.form_submit_button("Cadastrar"):
                if novo_nome:
                    st.session_state.motoboys_cadastrados.append({"Nome": novo_nome, "Placa": nova_placa, "Telefone": novo_tel})
                    st.success(f"{novo_nome} cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Digite pelo menos o nome!")

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
    st.write("Selecione o motoboy. Bipe no leitor ou digite o código e aperte ENTER para salvar na hora!")
    
    moto_atual = st.selectbox("🎯 Escolha o Motoboy para Bipar:", st.session_state.motoboys_hoje, key="moto_atual_sel")
    
    if moto_atual:
        c_conf1, c_conf2 = st.columns([1, 2])
        with c_conf1:
            val_p = st.number_input(
                f"Valor Pago por Pacote para {moto_atual} (R$):",
                min_value=0.0, value=st.session_state.configs_motoboys[moto_atual]["valor_pacote"], step=0.10
            )
            st.session_state.configs_motoboys[moto_atual]["valor_pacote"] = val_p
        with c_conf2:
            obs_p = st.text_input(
                f"Observações / Combinados do dia para {moto_atual}:",
                value=st.session_state.configs_motoboys[moto_atual]["obs"]
            )
            st.session_state.configs_motoboys[moto_atual]["obs"] = obs_p

        st.markdown("---")
        
        st.text_input(
            "⚡ Bipe no leitor USB ou digite e aperte ENTER:",
            key="input_bip_saida",
            on_change=add_pacote_saida,
            placeholder="Clique aqui para começar a bipar..."
        )
        st.caption("💡 Ao bipar no leitor ou apertar ENTER, o código entra no sistema e a caixinha limpa para o próximo!")

        pacotes_moto = [p for p in st.session_state.pacotes_saida if p["motoboy"] == moto_atual]
        st.subheader(f"📋 Pacotes Bipados para {moto_atual}: Total de {len(pacotes_moto)} volumes")
        
        if pacotes_moto:
            df_m = pd.DataFrame(pacotes_moto)
            st.dataframe(df_m[['codigo', 'hora']], use_container_width=True, hide_index=True)

    st.markdown("---")
    c_esp, c_btn = st.columns([3, 1])
    with c_btn:
        if st.button("Finalizar Rotas ➡️", type="primary", use_container_width=True):
            if not st.session_state.pacotes_saida:
                st.warning("Nenhum pacote foi bipado ainda!")
            else:
                st.session_state.etapa = 4
                st.rerun()


# ==========================================
# TELA 4: BIPAGEM DE INSUCESSOS
# ==========================================
elif st.session_state.etapa == 4:
    st.title("4️⃣ Bipagem de Insucessos e Devoluções (Rua + Agência)")
    st.write("Bipe aqui todos os pacotes que retornaram da rua OU que sobraram na agência (não saíram).")
    
    st.text_input(
        "⚠️ Bipe o insucesso no leitor USB ou digite e aperte ENTER:",
        key="input_bip_insucesso",
        on_change=add_pacote_insucesso,
        placeholder="Clique aqui e bipe o insucesso..."
    )
    st.caption("💡 Cada bip no leitor ou ENTER no teclado salva o insucesso e limpa a caixa na hora!")

    st.markdown("---")
    
    # Separação visual instantânea de Insucessos
    set_saidas = set(p["codigo"] for p in st.session_state.pacotes_saida)
    insucesso_rua = [c for c in st.session_state.pacotes_insucesso if c in set_saidas]
    insucesso_agencia = [c for c in st.session_state.pacotes_insucesso if c not in set_saidas]
    
    c_i1, c_i2, c_i3 = st.columns(3)
    c_i1.metric("Total Insucessos Bipados", f"{len(st.session_state.pacotes_insucesso)} un")
    c_i2.metric("Insucessos de Rua (Motoboys)", f"{len(insucesso_rua)} un")
    c_i3.metric("Sobras na Agência (Não Saíram)", f"{len(insucesso_agencia)} un")

    if st.session_state.pacotes_insucesso:
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Código do Insucesso": st.session_state.pacotes_insucesso}), use_container_width=True, hide_index=True)

    st.markdown("---")
    c_esp, c_btn = st.columns([3, 1])
    with c_btn:
        if st.button("Finalizar e Reconciliar ➡️", type="primary", use_container_width=True):
            st.session_state.etapa = 5
            st.rerun()


# ==========================================
# TELA 5: RECONCILIAÇÃO / EVIDENCIAÇÃO
# ==========================================
elif st.session_state.etapa == 5:
    st.title("5️⃣ Reconciliação de Entregas e Insucessos")
    st.write("O sistema cruzou os pacotes que saíram com os insucessos bipados no final do dia.")
    
    dict_saidas = {p["codigo"]: p["motoboy"] for p in st.session_state.pacotes_saida}
    set_insucessos = set(st.session_state.pacotes_insucesso)
    
    todos_codigos = set(dict_saidas.keys()).union(set_insucessos)
    
    lista_conferencia = []
    for cod in todos_codigos:
        if cod in dict_saidas:
            moto = dict_saidas[cod]
            if cod in set_insucessos:
                status = "🔴 INSUCESSO DE RUA (Devolvido)"
            else:
                status = "🟢 ENTREGUE COM SUCESSO"
        else:
            moto = "--- (Não Saiu)"
            status = "🟡 SOBRA DE AGÊNCIA (Ficou no CD)"
            
        lista_conferencia.append({
            "Código Pacote": cod,
            "Motoboy": moto,
            "Status Final": status
        })
        
    df_conf = pd.DataFrame(lista_conferencia)
    
    st.subheader("🔍 Evidenciação de Todos os Códigos do Dia")
    if not df_conf.empty:
        st.dataframe(df_conf[['Código Pacote', 'Motoboy', 'Status Final']], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum pacote bipado hoje.")
    
    st.markdown("---")
    st.subheader("💰 Pagamento dos Motoboys (Paga APENAS Sucessos de Rua)")
    
    resumo_motos = []
    for m in st.session_state.motoboys_hoje:
        if not df_conf.empty:
            df_m = df_conf[df_conf["Motoboy"] == m]
            tot_saida = len(df_m)
            tot_insucesso = len(df_m[df_m["Status Final"].str.contains("INSUCESSO")])
        else:
            tot_saida = 0
            tot_insucesso = 0
        
        tot_entregue = max(0, tot_saida - tot_insucesso)
        taxa = st.session_state.configs_motoboys[m]["valor_pacote"]
        obs = st.session_state.configs_motoboys[m]["obs"]
        valor_final_pago = tot_entregue * taxa
        
        resumo_motos.append({
            "Motoboy": m,
            "Saíram pra Rua": tot_saida,
            "Insucessos de Rua": tot_insucesso,
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
    
    set_saida = set(p["codigo"] for p in st.session_state.pacotes_saida)
    set_insucesso = set(st.session_state.pacotes_insucesso)
    
    # Categorias do Dia
    entregues_set = set_saida - set_insucesso
    insucessos_rua_set = set_saida.intersection(set_insucesso)
    sobras_agencia_set = set_insucesso - set_saida
    
    tot_entregues = len(entregues_set)
    tot_insucessos_rua = len(insucessos_rua_set)
    tot_sobras_agencia = len(sobras_agencia_set)
    tot_insucessos_geral = tot_insucessos_rua + tot_sobras_agencia
    tot_processados_dia = tot_entregues + tot_insucessos_geral
    
    taxa_sucesso = (tot_entregues / tot_processados_dia * 100) if tot_processados_dia > 0 else 0.0
    
    st.subheader("📊 Resumo Geral do CD")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Processado no Dia", f"{tot_processados_dia} un")
    m2.metric("Entregues com Sucesso", f"{tot_entregues} un")
    m3.metric("Insucessos de Rua", f"{tot_insucessos_rua} un")
    m4.metric("Sobras na Agência", f"{tot_sobras_agencia} un")
    m5.metric("% Taxa de Sucesso", f"{taxa_sucesso:.1f}%")

    st.markdown("---")
    st.subheader("💵 Cálculo do Repasse do Mercado Livre")
    
    # Mercado Livre paga 2,60 (ou 2,90) por entregue + 1,30 por insucesso (seja rua ou sobra da agência)
    fat_normal = (tot_entregues * 2.60) + (tot_insucessos_geral * 1.30)
    fat_bonus = (tot_entregues * 2.90) + (tot_insucessos_geral * 1.30)
    
    if taxa_sucesso >= 98.0 and tot_processados_dia > 0:
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
        tot_pago_motos = 0
        for m in st.session_state.motoboys_hoje:
            pacotes_m = [p for p in st.session_state.pacotes_saida if p["motoboy"] == m and p["codigo"] not in set_insucesso]
            tot_pago_motos += len(pacotes_m) * st.session_state.configs_motoboys[m]['valor_pacote']

        fat_final = fat_bonus if taxa_sucesso >= 98 else fat_normal

        novo_registro = pd.DataFrame([{
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Data_Obj": date.today(),
            "Total Pacotes": tot_processados_dia,
            "Entregues": tot_entregues,
            "Insucessos": tot_insucessos_geral,
            "% Sucesso": round(taxa_sucesso, 1),
            "Faturamento ML (R$)": round(fat_final, 2),
            "Pago Motoboys (R$)": round(tot_pago_motos, 2),
            "Lucro CD (R$)": round(fat_final - tot_pago_motos, 2)
        }])
        st.session_state.historico_40_dias = pd.concat([novo_registro, st.session_state.historico_40_dias], ignore_index=True)
        st.success("Dia finalizado e salvo no histórico com sucesso!")


# ==========================================
# TELA 7: RELATÓRIO MENSAL (ÚLTIMOS 40 DIAS)
# ==========================================
elif st.session_state.etapa == 7:
    st.title("📊 Relatório de Desempenho e Histórico")
    st.write("Acompanhe o histórico dos últimos 40 dias com filtro de datas personalizado.")
    
    col_d1, col_d2 = st.columns(2)
    dt_inicio = col_d1.date_input("Data Inicial:", date.today() - timedelta(days=30))
    dt_fim = col_d2.date_input("Data Final:", date.today())
    
    df_hist = st.session_state.historico_40_dias.copy()
    if 'Data_Obj' in df_hist.columns:
        df_filtrado = df_hist[(df_hist['Data_Obj'] >= dt_inicio) & (df_hist['Data_Obj'] <= dt_fim)]
    else:
        df_filtrado = df_hist

    st.markdown("---")
    st.subheader("Resultados no Período Selecionado")
    
    if not df_filtrado.empty:
        st.dataframe(df_filtrado.drop(columns=['Data_Obj'], errors='ignore'), use_container_width=True, hide_index=True)
        
        st.subheader("📈 Evolução do Faturamento")
        st.line_chart(df_filtrado.set_index('Data')['Faturamento ML (R$)'])
    else:
        st.warning("Nenhum dado encontrado para o período selecionado.")