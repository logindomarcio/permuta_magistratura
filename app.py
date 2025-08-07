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
# Estilo moderno e sofisticado
# ===============================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Fundo geral - branco-gelo */
    .stApp {
        background: linear-gradient(135deg, #fefefe 0%, #f8f9fa 100%);
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
    }
    
    /* Reset de todos os textos para fonte moderna */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Títulos modernos */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        color: #1a202c;
        font-weight: 600;
        letter-spacing: -0.025em;
    }
    
    /* Texto geral moderno */
    .stMarkdown, .stText, p, div, span, label {
        font-family: 'Inter', sans-serif;
        color: #4a5568;
        line-height: 1.6;
    }
    
    /* Header moderno */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin: -1rem -1rem 3rem -1rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        margin-top: 1rem;
        font-weight: 400;
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Cards de métricas modernos */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #718096;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Seções modernas */
    .section-header {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        border-left: 4px solid #667eea;
        margin: 2rem 0 1rem 0;
    }
    
    .section-header h2 {
        margin: 0;
        color: #2d3748;
        font-size: 1.5rem;
    }
    
    /* Inputs modernos */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextInput > div > div {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Tabelas modernas */
    .stDataFrame {
        background: white;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }
    
    .stDataFrame > div {
        border-radius: 16px;
    }
    
    /* Tabs modernos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        color: #4a5568;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Alertas modernos */
    .stAlert {
        font-family: 'Inter', sans-serif;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        border-left: 4px solid #38a169;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
        border-left: 4px solid #3182ce;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fffbeb 0%, #fef5e7 100%);
        border-left: 4px solid #d69e2e;
    }
    
    /* Expander moderno */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    /* Animações suaves */
    * {
        transition: all 0.3s ease;
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

def limpar_celula(x):
    if not isinstance(x, str):
        return None
    x = unicodedata.normalize('NFKD', x)
    x = ''.join(c for c in x if not unicodedata.combining(c))
    x = x.replace('\xa0', ' ').strip()
    return x if x else None

# ===============================
# Função para carregar dados via st.secrets
# ===============================
@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_dados():
    try:
        creds_dict = st.secrets["google_service_account"]
        gc = gspread.service_account_from_dict(creds_dict)
        sheet = gc.open("Permuta - Magistratura Estadual").sheet1
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])

        # Garantir que a coluna Entrância existe
        if "Entrância" not in df.columns:
            df["Entrância"] = "Não informada"

        # Limpeza reforçada de colunas relevantes
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
# Interface - Cabeçalho moderno
# ===============================
st.markdown(
    """
    <div class="main-header">
        <h1>⚖️ Permuta - Magistratura Estadual v2.0</h1>
        <p>Sistema Aprimorado de Análise de Permutas Judiciais</p>
        <p style="font-size: 0.95rem; opacity: 0.8;">Versão com Quadrangulações, Pentagulações e Análises Avançadas</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
# Botão para atualizar dados
# ===============================
col_update1, col_update2, col_update3 = st.columns([1, 1, 1])
with col_update2:
    if st.button("🔄 Atualizar Base de Dados", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Base de dados atualizada com sucesso!")
        st.rerun()

# ===============================
# Carregar dados
# ===============================
df = carregar_dados()

if df.empty:
    st.error("❌ Não foi possível carregar os dados. Verifique a conexão.")
    st.stop()

# Lista de e-mails autorizados
emails_autorizados = set(df["E-mail"].dropna().unique())

# ===============================
# Login por e-mail
# ===============================
st.markdown('<div class="section-header"><h2>🔐 Acesso Restrito</h2></div>', unsafe_allow_html=True)
email_user = st.text_input("Digite seu e-mail para acessar a aplicação:", placeholder="exemplo@email.com")

if email_user and email_user not in emails_autorizados:
    st.warning("⚠️ Acesso restrito. Seu e-mail não está cadastrado na base de dados.")
    st.stop()
elif not email_user:
    st.info("ℹ️ Digite seu e-mail para acessar a aplicação.")
    st.stop()
else:
    st.success(f"✅ Acesso liberado para: {email_user}")

# ===============================
# Estatísticas automáticas (sempre visíveis após login)
# ===============================
st.markdown('<div class="section-header"><h2>📊 Panorama Geral da Base de Dados</h2></div>', unsafe_allow_html=True)

# Calcular estatísticas
tribunais_stats = calcular_estatisticas_tribunais(df)
total_juizes = len(df)

# Métricas gerais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">👨‍⚖️ {total_juizes}</div>
            <div class="metric-label">Juízes Cadastrados</div>
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
            <div class="metric-label">Tribunais Envolvidos</div>
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
            <div class="metric-label">Preferências Registradas</div>
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
            <div class="metric-label">Permutas Diretas Possíveis</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Gráficos automáticos
st.markdown('<div class="section-header"><h2>📈 Análises Visuais Automáticas</h2></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Mais Procurados", "📤 Mais Exportadores", "🔗 Mais Conectados", "📊 Distribuição"])

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

# ===============================
# Lista fixa de todos os TJs do Brasil
# ===============================
lista_tjs = sorted([
    "TJAC", "TJAL", "TJAM", "TJAP", "TJBA", "TJCE", "TJDFT", "TJES", "TJGO", "TJMA",
    "TJMG", "TJMS", "TJMT", "TJPA", "TJPB", "TJPE", "TJPI", "TJPR", "TJRJ", "TJRN",
    "TJRO", "TJRR", "TJRS", "TJSC", "TJSE", "TJSP", "TJTO"
])

# ===============================
# Busca personalizada - SEMPRE VISÍVEL APÓS LOGIN
# ===============================
st.markdown('<div class="section-header"><h2>🔍 Escolha seus critérios</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    origem_user = st.selectbox("📍 Sua Origem", lista_tjs)
with col2:
    destino_user = st.selectbox("🎯 Seu Destino Preferencial", lista_tjs)

# Botão de busca SEMPRE visível
if st.button("🔍 Buscar Permutas e Triangulações para meu caso", use_container_width=True):
    if not origem_user or not destino_user:
        st.warning("⚠️ Por favor, selecione tanto a origem quanto o destino.")
    else:
        st.markdown(f"### Resultados para: {origem_user} → {destino_user}")
        
        # Buscar todos os tipos de permuta
        casais = buscar_permutas_diretas(df, origem_user, destino_user)
        triangulos = buscar_triangulacoes(df, origem_user, destino_user)
        quadrangulos = buscar_quadrangulacoes(df, origem_user, destino_user)
        pentagulos = buscar_pentagulacoes(df, origem_user, destino_user)
        hexagulos = buscar_hexagulacoes(df, origem_user, destino_user)
        
        # Exibir resultados
        if casais:
            st.success(f"🎯 {len(casais)} permuta(s) direta(s) encontrada(s) para seu caso:")
            st.dataframe(pd.DataFrame(casais), use_container_width=True)
            st.subheader("🌐 Visualização no Mapa (Casais):")
            fig_casais = mostrar_mapa_casais(casais)
            st.plotly_chart(fig_casais, use_container_width=True)
        else:
            st.info("⚠️ Nenhuma permuta direta encontrada para sua origem e destino.")

        if triangulos:
            st.success(f"🔺 {len(triangulos)} triangulação(ões) possível(is) para seu caso:")
            st.dataframe(pd.DataFrame(triangulos), use_container_width=True)
            st.subheader("🌐 Visualização no Mapa (Triangulações):")
            fig_triangulos = mostrar_mapa_triangulacoes(triangulos)
            st.plotly_chart(fig_triangulos, use_container_width=True)
        else:
            st.info("⚠️ Nenhuma triangulação encontrada para sua origem e destino.")
            
        if quadrangulos:
            st.success(f"◊ {len(quadrangulos)} quadrangulação(ões) possível(is) para seu caso:")
            st.dataframe(pd.DataFrame(quadrangulos), use_container_width=True)
            st.subheader("🌐 Visualização no Mapa (Quadrangulações):")
            fig_quadrangulos = mostrar_mapa_ciclos_n(quadrangulos, 4)
            st.plotly_chart(fig_quadrangulos, use_container_width=True)
            
        if pentagulos:
            st.success(f"⬟ {len(pentagulos)} pentagulação(ões) possível(is) para seu caso:")
            st.dataframe(pd.DataFrame(pentagulos), use_container_width=True)
            st.subheader("🌐 Visualização no Mapa (Pentagulações):")
            fig_pentagulos = mostrar_mapa_ciclos_n(pentagulos, 5)
            st.plotly_chart(fig_pentagulos, use_container_width=True)
            
        if hexagulos:
            st.success(f"⬢ {len(hexagulos)} hexagulação(ões) possível(is) para seu caso:")
            st.dataframe(pd.DataFrame(hexagulos), use_container_width=True)
            st.subheader("🌐 Visualização no Mapa (Hexagulações):")
            fig_hexagulos = mostrar_mapa_ciclos_n(hexagulos, 6)
            st.plotly_chart(fig_hexagulos, use_container_width=True)

# ===============================
# Base completa (sempre ao final)
# ===============================
st.markdown('<div class="section-header"><h2>📂 Base de Dados Completa</h2></div>', unsafe_allow_html=True)

with st.expander("👁️ Ver base de dados completa", expanded=False):
    st.markdown("### 📋 Dados Completos dos Juízes Cadastrados")
    st.dataframe(df, use_container_width=True)
    
    # Opção de download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados em CSV",
        data=csv,
        file_name='permuta_magistratura_dados.csv',
        mime='text/csv',
        use_container_width=True
    )

# ===============================
# Rodapé moderno
# ===============================
st.markdown(
    """
    <div style='text-align: center; padding: 3rem 2rem; 
                background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); 
                margin: 3rem -1rem -1rem -1rem; border-radius: 20px 20px 0 0;
                border-top: 1px solid #e2e8f0;'>
        <p style='color: #718096; font-size: 0.9rem; margin-bottom: 1.5rem; line-height: 1.6;'>
            ⚠️ <strong>Aplicação desenvolvida de forma colaborativa, gratuita e sem fins econômicos.</strong><br>
            🗂️ <strong>Os dados são voluntariamente informados por seus próprios titulares.</strong><br>
            🔒 <strong>Acesso restrito aos cadastrados na base de dados.</strong>
        </p>
        <div style='height: 1px; background: linear-gradient(90deg, transparent, #cbd5e0, transparent); margin: 2rem 0;'></div>
        <p style='color: #4a5568; font-weight: 500; font-size: 1rem;'>
            💡 <strong>Necessita de mentoria em inteligência artificial?</strong><br>
            <a href="mailto:marciocarneirodemesquitajunior@gmail.com" 
               style='color: #667eea; text-decoration: none; font-weight: 600;'>
                📧 Entre em contato conosco!
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)