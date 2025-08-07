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
# Estilo personalizado - ambiente sofisticado e formal
# ===============================
st.markdown(
    """
    <style>
    /* Fundo geral */
    .stApp {
        background-color: #fdf6e3;
        color: #2c3e50;
    }
    
    /* Estilo dos títulos */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Times New Roman', serif;
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* Estilo do texto geral */
    .stMarkdown, .stText, p, div {
        font-family: 'Times New Roman', serif;
        color: #34495e;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f5f0;
    }
    
    /* Botões */
    .stButton > button {
        background-color: #8b7355;
        color: white;
        border: none;
        border-radius: 6px;
        font-family: 'Times New Roman', serif;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #6d5a42;
        box-shadow: 0 4px 8px rgba(139, 115, 85, 0.3);
    }
    
    /* Métricas */
    .metric-card {
        background: linear-gradient(135deg, #f8f5f0 0%, #ede7d9 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #8b7355;
        box-shadow: 0 2px 4px rgba(139, 115, 85, 0.1);
    }
    
    /* Containers de dados */
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 6px;
    }
    
    /* Inputs */
    .stSelectbox > div > div {
        background-color: #ffffff;
        border-color: #8b7355;
    }
    
    .stTextInput > div > div {
        background-color: #ffffff;
        border-color: #8b7355;
    }
    
    /* Avisos e alertas */
    .stAlert {
        font-family: 'Times New Roman', serif;
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
# Interface - Cabeçalho elegante
# ===============================
st.markdown(
    """
    <div style='text-align: center; background: linear-gradient(135deg, #f8f5f0 0%, #ede7d9 100%); 
                padding: 2rem; margin: -1rem -1rem 2rem -1rem; border-radius: 0 0 15px 15px;'>
        <h1 style='font-family: "Times New Roman", serif; font-size: 2.5rem; 
                   color: #2c3e50; margin-bottom: 0.5rem; font-weight: 700;'>
            ⚖️ Permuta - Magistratura Estadual v2.0
        </h1>
        <h4 style='font-family: "Times New Roman", serif; color: #7f8c8d; 
                   font-style: italic; font-weight: 400; line-height: 1.6;'>
            Sistema Aprimorado de Análise de Permutas Judiciais<br>
            <span style='font-size: 0.9rem;'>Versão com Quadrangulações, Pentagulações e Análises Avançadas</span>
        </h4>
        <hr style='border: none; height: 2px; background: linear-gradient(90deg, transparent, #8b7355, transparent); margin: 1rem 0;'>
        <p style='font-size: 0.85rem; color: #95a5a6; font-style: italic;'>
            A presente aplicação tem finalidade meramente ilustrativa, gratuita e não oficial.<br>
            Desenvolvida para facilitar a visualização de oportunidades de permuta entre magistrados.
        </p>
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
st.markdown("### 🔐 Acesso Restrito")
email_user = st.text_input("Digite seu e-mail para acessar a aplicação:", placeholder="exemplo@email.com")

if email_user and email_user not in emails_autorizados:
    st.warning("⚠️ Acesso restrito. Seu e-mail não está cadastrado na base de dados.")
    st.stop()
elif email_user and email_user in emails_autorizados:
    st.success(f"✅ Acesso liberado para: {email_user}")

# ===============================
# Estatísticas automáticas (sempre visíveis após login)
# ===============================
if email_user in emails_autorizados:
    st.markdown("---")
    
    # Calcular estatísticas
    tribunais_stats = calcular_estatisticas_tribunais(df)
    total_juizes = len(df)
    
    # Métricas gerais
    st.markdown("## 📊 Panorama Geral da Base de Dados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="color: #8b7355; margin: 0;">👨‍⚖️ {total_juizes}</h3>
                <p style="margin: 0; font-size: 0.9rem;">Juízes Cadastrados</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        total_tribunais = len(tribunais_stats)
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="color: #8b7355; margin: 0;">🏛️ {total_tribunais}</h3>
                <p style="margin: 0; font-size: 0.9rem;">Tribunais Envolvidos</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        total_preferencias = sum(v['procurado'] for v in tribunais_stats.values())
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="color: #8b7355; margin: 0;">🎯 {total_preferencias}</h3>
                <p style="margin: 0; font-size: 0.9rem;">Preferências Registradas</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        casais_rapidos = len(buscar_permutas_diretas(df))
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="color: #8b7355; margin: 0;">💫 {casais_rapidos}</h3>
                <p style="margin: 0; font-size: 0.9rem;">Permutas Diretas Possíveis</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Gráficos automáticos
    st.markdown("## 📈 Análises Visuais Automáticas")
    
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
# Busca personalizada
# ===============================
if email_user in emails_autorizados:
    st.markdown("---")
    st.markdown("## 🔍 Busca Personalizada de Permutas")
    
    col1, col2 = st.columns(2)
    with col1:
        origem_user = st.selectbox("📍 Sua Origem", [""] + lista_tjs, index=0)
    with col2:
        destino_user = st.selectbox("🎯 Seu Destino Preferencial", [""] + lista_tjs, index=0)

    # Botão de busca
    if st.button("🔍 Buscar Todas as Possibilidades de Permuta", use_container_width=True):
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
            
            # Métricas dos resultados
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("🔁 Permutas Diretas", len(casais))
            with col2:
                st.metric("🔺 Triangulações", len(triangulos))
            with col3:
                st.metric("◊ Quadrangulações", len(quadrangulos))
            with col4:
                st.metric("⬟ Pentagulações", len(pentagulos))
            with col5:
                st.metric("⬢ Hexagulações", len(hexagulos))
            
            # Exibir resultados em tabs
            if any([casais, triangulos, quadrangulos, pentagulos, hexagulos]):
                tabs = []
                tab_names = []
                
                if casais:
                    tab_names.append(f"🔁 Casais ({len(casais)})")
                if triangulos:
                    tab_names.append(f"🔺 Triangulações ({len(triangulos)})")
                if quadrangulos:
                    tab_names.append(f"◊ Quadrangulações ({len(quadrangulos)})")
                if pentagulos:
                    tab_names.append(f"⬟ Pentagulações ({len(pentagulos)})")
                if hexagulos:
                    tab_names.append(f"⬢ Hexagulações ({len(hexagulos)})")
                
                tabs = st.tabs(tab_names)
                tab_index = 0
                
                if casais:
                    with tabs[tab_index]:
                        st.dataframe(pd.DataFrame(casais), use_container_width=True)
                        fig_casais = mostrar_mapa_casais(casais)
                        st.plotly_chart(fig_casais, use_container_width=True)
                    tab_index += 1
                
                if triangulos:
                    with tabs[tab_index]:
                        st.dataframe(pd.DataFrame(triangulos), use_container_width=True)
                        fig_triangulos = mostrar_mapa_triangulacoes(triangulos)
                        st.plotly_chart(fig_triangulos, use_container_width=True)
                    tab_index += 1
                
                if quadrangulos:
                    with tabs[tab_index]:
                        st.dataframe(pd.DataFrame(quadrangulos), use_container_width=True)
                        fig_quadrangulos = mostrar_mapa_ciclos_n(quadrangulos, 4)
                        st.plotly_chart(fig_quadrangulos, use_container_width=True)
                    tab_index += 1
                
                if pentagulos:
                    with tabs[tab_index]:
                        st.dataframe(pd.DataFrame(pentagulos), use_container_width=True)
                        fig_pentagulos = mostrar_mapa_ciclos_n(pentagulos, 5)
                        st.plotly_chart(fig_pentagulos, use_container_width=True)
                    tab_index += 1
                
                if hexagulos:
                    with tabs[tab_index]:
                        st.dataframe(pd.DataFrame(hexagulos), use_container_width=True)
                        fig_hexagulos = mostrar_mapa_ciclos_n(hexagulos, 6)
                        st.plotly_chart(fig_hexagulos, use_container_width=True)
            else:
                st.info("ℹ️ Nenhuma possibilidade de permuta encontrada para os critérios selecionados.")

# ===============================
# Base completa (opcional)
# ===============================
if email_user in emails_autorizados:
    with st.expander("📂 Ver Base de Dados Completa"):
        st.dataframe(df, use_container_width=True)
        
        # Opção de download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar dados em CSV",
            data=csv,
            file_name='permuta_magistratura_dados.csv',
            mime='text/csv'
        )

# ===============================
# Rodapé elegante
# ===============================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f5f0 0%, #ede7d9 100%); 
                margin: 2rem -1rem -1rem -1rem; border-radius: 15px 15px 0 0;'>
        <p style='color: #7f8c8d; font-style: italic; margin-bottom: 1rem;'>
            ⚠️ <strong>Aplicação desenvolvida de forma colaborativa, gratuita e sem fins econômicos.</strong><br>
            🗂️ <strong>Os dados são voluntariamente informados por seus próprios titulares.</strong><br>
            🔒 <strong>Acesso restrito aos cadastrados na base de dados.</strong>
        </p>
        <hr style='border: none; height: 1px; background: linear-gradient(90deg, transparent, #8b7355, transparent); margin: 1rem 0;'>
        <p style='color: #8b7355; font-weight: 600;'>
            💡 <strong>Necessita de mentoria em inteligência artificial?</strong><br>
            <a href="mailto:marciocarneirodemesquitajunior@gmail.com" style='color: #8b7355; text-decoration: none;'>
                📧 Entre em contato conosco!
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)