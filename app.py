import streamlit as st
import gspread
import pandas as pd
from algoritmo import (
    buscar_permutas_diretas, 
    buscar_triangulacoes, 
    buscar_quadrangulacoes,
    buscar_pentagulacoes,
    buscar_hexagulacoes,
    calcular_estatisticas_tribunais
)
from mapa import mostrar_mapa_triangulacoes, mostrar_mapa_casais, mostrar_mapa_ciclos_n
from graficos import (
    criar_grafico_tribunais_procurados,
    criar_grafico_tribunais_exportadores,
    criar_grafico_tribunais_conectados,
    criar_grafico_estatisticas_gerais
)
import unicodedata

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
# Estilo moderno e simplificado
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

# ===============================
# Função para carregar dados
# ===============================
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
# Botão atualizar
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
# Métricas gerais
# ===============================
st.markdown("## 📊 Panorama Geral da Base de Dados")

tribunais_stats = calcular_estatisticas_tribunais(df)
total_juizes = len(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">👨‍⚖️ {total_juizes}</div>
            <p>Juízes Cadastrados</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with col2:
    total_tribunais = len(tribunais_stats)
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">🏛️ {total_tribunais}</div>
            <p>Tribunais Envolvidos</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with col3:
    total_preferencias = sum(v['procurado'] for v in tribunais_stats.values())
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">🎯 {total_preferencias}</div>
            <p>Preferências Registradas</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with col4:
    casais_rapidos = len(buscar_permutas_diretas(df))
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">💫 {casais_rapidos}</div>
            <p>Permutas Diretas</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ===============================
# Gráficos (protegidos contra erro)
# ===============================
st.markdown("## 📈 Análises Visuais Automáticas")

try:
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Mais Procurados", "📤 Exportadores", "🔗 Conectados", "📊 Distribuição"])

    with tab1:
        fig_procurados = criar_grafico_tribunais_procurados(tribunais_stats)
        st.plotly_chart(fig_procurados, use_container_width=True)

    with tab2:
        fig_exportadores = criar_grafico_tribunais_exportadores(tribunais_stats)
        st.plotly_chart(fig_exportadores, use_container_width=True)

    with tab3:
        fig_conectados = criar_grafico_tribunais_conectados(tribunais_stats)
        st.plotly_chart(fig_conectados, use_container_width=True)

    with tab4:
        fig_distribuicao = criar_grafico_estatisticas_gerais(tribunais_stats, total_juizes)
        st.plotly_chart(fig_distribuicao, use_container_width=True)
        
except Exception as e:
    st.error(f"Erro ao carregar gráficos: {str(e)}")
    st.info("Os gráficos serão corrigidos na próxima atualização.")

# ===============================
# Busca personalizada
# ===============================
st.markdown("## 🔍 Escolha seus critérios")

lista_tjs = sorted([
    "TJAC", "TJAL", "TJAM", "TJAP", "TJBA", "TJCE", "TJDFT", "TJES", "TJGO", "TJMA",
    "TJMG", "TJMS", "TJMT", "TJPA", "TJPB", "TJPE", "TJPI", "TJPR", "TJRJ", "TJRN",
    "TJRO", "TJRR", "TJRS", "TJSC", "TJSE", "TJSP", "TJTO"
])

col1, col2 = st.columns(2)
with col1:
    origem_user = st.selectbox("📍 Sua Origem", lista_tjs)
with col2:
    destino_user = st.selectbox("🎯 Seu Destino Preferencial", lista_tjs)

# ===============================
# Botão de busca e resultados
# ===============================
if st.button("🔍 Buscar Permutas e Triangulações para meu caso", use_container_width=True):
    if not origem_user or not destino_user:
        st.warning("⚠️ Selecione origem e destino.")
    else:
        st.markdown(f"### Resultados para: {origem_user} → {destino_user}")
        
        # Buscar permutas
        casais = buscar_permutas_diretas(df, origem_user, destino_user)
        triangulos = buscar_triangulacoes(df, origem_user, destino_user)
        
        try:
            quadrangulos = buscar_quadrangulacoes(df, origem_user, destino_user)
            pentagulos = buscar_pentagulacoes(df, origem_user, destino_user)
            hexagulos = buscar_hexagulacoes(df, origem_user, destino_user)
        except:
            quadrangulos = []
            pentagulos = []
            hexagulos = []
        
        # Mostrar resultados
        if casais:
            st.success(f"🎯 {len(casais)} permuta(s) direta(s) encontrada(s):")
            st.dataframe(pd.DataFrame(casais), use_container_width=True)
            try:
                fig_casais = mostrar_mapa_casais(casais)
                st.plotly_chart(fig_casais, use_container_width=True)
            except:
                st.info("Mapa temporariamente indisponível")
        else:
            st.info("⚠️ Nenhuma permuta direta encontrada.")

        if triangulos:
            st.success(f"🔺 {len(triangulos)} triangulação(ões) encontrada(s):")
            st.dataframe(pd.DataFrame(triangulos), use_container_width=True)
            try:
                fig_triangulos = mostrar_mapa_triangulacoes(triangulos)
                st.plotly_chart(fig_triangulos, use_container_width=True)
            except:
                st.info("Mapa temporariamente indisponível")
        else:
            st.info("⚠️ Nenhuma triangulação encontrada.")
            
        if quadrangulos:
            st.success(f"◊ {len(quadrangulos)} quadrangulação(ões) encontrada(s):")
            st.dataframe(pd.DataFrame(quadrangulos), use_container_width=True)
            
        if pentagulos:
            st.success(f"⬟ {len(pentagulos)} pentagulação(ões) encontrada(s):")
            st.dataframe(pd.DataFrame(pentagulos), use_container_width=True)
            
        if hexagulos:
            st.success(f"⬢ {len(hexagulos)} hexagulação(ões) encontrada(s):")
            st.dataframe(pd.DataFrame(hexagulos), use_container_width=True)

# ===============================
# Base completa
# ===============================
st.markdown("---")
with st.expander("📂 Ver base de dados completa"):
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados em CSV",
        data=csv,
        file_name='permuta_magistratura_dados.csv',
        mime='text/csv'
    )

# ===============================
# Rodapé
# ===============================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;'>
        <p><strong>Aplicação gratuita e colaborativa para magistrados.</strong></p>
        <p>💡 Dúvidas? <a href="mailto:marciocarneirodemesquitajunior@gmail.com">Entre em contato!</a></p>
    </div>
    """,
    unsafe_allow_html=True
)