import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import unicodedata

from algoritmo import (
    buscar_permutas_diretas, 
    buscar_triangulacoes, 
    buscar_quadrangulacoes,
    calcular_estatisticas_tribunais
)
from mapa import mostrar_mapa_triangulacoes, mostrar_mapa_casais

# ===============================
# Configuração da página
# ===============================
st.set_page_config(
    page_title="Permuta Magistratura v2.0",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# Estilo da aplicação
# ===============================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #fefefe;
        color: #2c3e50;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .permutrometro-section {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e0e8ff;
        margin: 2rem 0;
    }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# Funções auxiliares
# ===============================
def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto_norm = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = ''.join(c for c in texto_norm if not unicodedata.combining(c))
    return texto_sem_acento.strip().lower()

@st.cache_data(ttl=300)
def carregar_dados():
    try:
        creds_dict = st.secrets["google_service_account"]
        gc = gspread.service_account_from_dict(creds_dict)
        sheet = gc.open("Permuta - Magistratura Estadual").sheet1
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        if "Entrância" not in df.columns:
            df["Entrância"] = "Não informada"
        for coluna in ["Destino 1", "Destino 2", "Destino 3", "E-mail", "Entrância"]:
            if coluna in df.columns:
                df[coluna] = df[coluna].apply(lambda x: str(x).strip() if pd.notnull(x) and str(x).strip() != "" else None)
        df["Nome"] = df["Nome"].str.strip()
        df["Origem"] = df["Origem"].str.strip()
        df["Nome_Normalizado"] = df["Nome"].apply(normalizar_texto)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# ===============================
# Cabeçalho
# ===============================
st.markdown(
    """
    <div class="main-header">
        <h1>⚖️ Permuta - Magistratura Estadual v2.0</h1>
        <p>Sistema Aprimorado de Análise de Permutas Judiciais</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
# Botão para forçar atualização
# ===============================
if st.button("🔄 Atualizar Base de Dados"):
    st.cache_data.clear()
    st.success("✅ Base de dados atualizada!")
    st.rerun()

# ===============================
# Carregar dados
# ===============================
df = carregar_dados()

if df.empty:
    st.error("❌ Não foi possível carregar os dados.")
    st.stop()

# ===============================
# Login
# ===============================
st.markdown("### 🔐 Acesso Restrito")
email_user = st.text_input("Digite seu e-mail para acessar a aplicação:")

emails_autorizados = set(df["E-mail"].dropna().unique())

if email_user and email_user not in emails_autorizados:
    st.warning("⚠️ Acesso restrito. Seu e-mail não está cadastrado.")
    st.stop()
elif not email_user:
    st.info("ℹ️ Digite seu e-mail para acessar a aplicação.")
    st.stop()
else:
    st.success(f"✅ Acesso liberado para: {email_user}")

# ===============================
# Busca por Nome do Juiz
# ===============================
st.markdown("### 👤 Selecione seu nome na lista para verificar possíveis permutas")

nomes_disponiveis = df["Nome"].dropna().unique()
nome_selecionado = st.selectbox("🔍 Buscar juiz:", sorted(nomes_disponiveis))

if not nome_selecionado:
    st.warning("Selecione um nome para continuar.")
    st.stop()

# Obter dados do juiz selecionado
juiz = df[df["Nome"] == nome_selecionado].iloc[0]
origem = juiz["Origem"]
destinos = [juiz.get("Destino 1"), juiz.get("Destino 2"), juiz.get("Destino 3")]
entrancia_juiz = juiz.get("Entrância", "Não informada")

st.markdown(f"**Origem:** 📍 `{origem}` &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; **Entrância:** `{entrancia_juiz}`")
st.markdown(f"**Destinos pretendidos:** 🎯 {', '.join([d for d in destinos if d])}")

# ===============================
# Execução dos Algoritmos
# ===============================
with st.spinner("🔄 Buscando permutas possíveis..."):

    resultados_casais = buscar_permutas_diretas(df, nome_selecionado)
    resultados_triangulacoes = buscar_triangulacoes(df, nome_selecionado)
    resultados_quadrangulacoes = buscar_quadrangulacoes(df, nome_selecionado)

# ===============================
# Visualização de Resultados
# ===============================
st.markdown("## 🔁 Resultados de Permutas")

# ---- Permutas Diretas
st.markdown("### 🤝 Permutas Diretas Encontradas")
if resultados_casais:
    for idx, par in enumerate(resultados_casais, 1):
        st.markdown(f"**{idx}.** {par}")
else:
    st.info("Nenhuma permuta direta encontrada.")

# ---- Triangulações
st.markdown("### 🔺 Triangulações Encontradas")
if resultados_triangulacoes:
    for idx, triang in enumerate(resultados_triangulacoes, 1):
        st.markdown(f"**{idx}.** {triang}")
else:
    st.info("Nenhuma triangulação encontrada.")

# ---- Quadrangulações
st.markdown("### 🔸 Quadrangulações Encontradas")
if resultados_quadrangulacoes:
    for idx, quad in enumerate(resultados_quadrangulacoes, 1):
        st.markdown(f"**{idx}.** {quad}")
else:
    st.info("Nenhuma quadrangulação encontrada.")

# ===============================
# Visualização Estilizada (Tabelas)
# ===============================

import pandas as pd

def estilizar_resultados(titulo, dados, tipo):
    if not dados:
        return

    st.markdown(f"### {titulo}")

    linhas = []
    for item in dados:
        if tipo == "casal":
            juiz_a, juiz_b = item.split(" ⇄ ")
            linha = {
                "Juiz A": juiz_a,
                "Entrância A": df[df["Nome"] == juiz_a].Entrância.values[0] if juiz_a in df["Nome"].values else "N/I",
                "Origem A": df[df["Nome"] == juiz_a].Origem.values[0] if juiz_a in df["Nome"].values else "N/I",
                "Destino A": df[df["Nome"] == juiz_a][["Destino 1", "Destino 2", "Destino 3"]].values.tolist()[0],
                "Juiz B": juiz_b,
                "Entrância B": df[df["Nome"] == juiz_b].Entrância.values[0] if juiz_b in df["Nome"].values else "N/I",
                "Origem B": df[df["Nome"] == juiz_b].Origem.values[0] if juiz_b in df["Nome"].values else "N/I",
                "Destino B": df[df["Nome"] == juiz_b][["Destino 1", "Destino 2", "Destino 3"]].values.tolist()[0],
            }
            linhas.append(linha)
        else:
            # Para triangulações e quadrangulações
            partes = item.split(" → ")
            nomes = [p.split("(")[0].strip() for p in partes]
            linha = {f"Juiz {chr(65+i)}": nome for i, nome in enumerate(nomes)}
            linhas.append(linha)

    df_resultado = pd.DataFrame(linhas)
    st.dataframe(df_resultado, use_container_width=True)

# Tabelas de exibição
estilizar_resultados("📄 Tabela de Permutas Diretas", resultados_casais, "casal")
estilizar_resultados("📄 Tabela de Triangulações", resultados_triangulacoes, "outra")
estilizar_resultados("📄 Tabela de Quadrangulações", resultados_quadrangulacoes, "outra")

# ===============================
# Exportação CSV e Rodapé
# ===============================

def exportar_csv(nome_arquivo, dados, tipo):
    linhas = []
    for item in dados:
        if tipo == "casal":
            juiz_a, juiz_b = item.split(" ⇄ ")
            linha = {
                "Juiz A": juiz_a,
                "Juiz B": juiz_b,
            }
            linhas.append(linha)
        else:
            partes = item.split(" → ")
            linha = {f"Juiz {chr(65+i)}": p for i, p in enumerate(partes)}
            linhas.append(linha)

    df_export = pd.DataFrame(linhas)
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Baixar {nome_arquivo}.csv",
        data=csv,
        file_name=f"{nome_arquivo}.csv",
        mime="text/csv",
    )


st.markdown("---")
st.markdown("## 📁 Exportar Resultados")

col1, col2, col3 = st.columns(3)

with col1:
    exportar_csv("casais", resultados_casais, "casal")
with col2:
    exportar_csv("triangulacoes", resultados_triangulacoes, "outra")
with col3:
    exportar_csv("quadrangulacoes", resultados_quadrangulacoes, "outra")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; font-size: 0.85em; color: grey;'>
        Sistema desenvolvido para fins de simulação e organização de permutas na magistratura.<br>
        Resultados obtidos a partir da base fornecida e cruzamento automático de dados.
    </div>
    """,
    unsafe_allow_html=True,
)

# =======================
# Painel de Métricas Gerais
# =======================

st.markdown("## 📊 Painel Geral de Indicadores")
col1, col2, col3 = st.columns(3)

# Indicador: Total de Juízes
total_juizes = len(df)
col1.metric(label="👩‍⚖️ Total de Juízes", value=f"{total_juizes}")

# Indicador: Total de Permutas Geradas (Casais + Triangulações + Quadrangulações)
total_permuta = len(casais) + len(triangulos) + len(quadrangulos)
col2.metric(label="🔁 Total de Permutas", value=f"{total_permuta}")

# Indicador: Total de Tribunais distintos
tribunais_env = set(df['Origem']).union(df['Destino1']).union(df['Destino2']).union(df['Destino3'])
col3.metric(label="🏛️ Tribunais Envolvidos", value=f"{len(tribunais_env)}")

st.markdown("---")
