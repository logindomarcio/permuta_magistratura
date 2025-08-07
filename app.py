import streamlit as st
import gspread
import pandas as pd
from algoritmo import (
    buscar_permutas_diretas, 
    buscar_triangulacoes, 
    buscar_quadrangulacoes,
    calcular_estatisticas_tribunais
)
from mapa import mostrar_mapa_triangulacoes, mostrar_mapa_casais, mostrar_mapa_ciclos_n
import plotly.graph_objects as go
import plotly.express as px
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

def obter_prioridade_destino(df, juiz_nome, tribunal_destino):
    """
    Determina se um destino é prioritário (1), secundário (2), terciário (3) ou não encontrado
    """
    juiz_linha = df[df['Nome'] == juiz_nome]
    
    if juiz_linha.empty:
        return 0
    
    juiz_dados = juiz_linha.iloc[0]
    
    if str(juiz_dados.get('Destino 1', '')).strip() == tribunal_destino:
        return 1
    elif str(juiz_dados.get('Destino 2', '')).strip() == tribunal_destino:
        return 2  
    elif str(juiz_dados.get('Destino 3', '')).strip() == tribunal_destino:
        return 3
    else:
        return 0

def adicionar_sinalizadores_prioridade(resultados, df, tipo_resultado='casais'):
    """
    Adiciona sinalizadores de prioridade aos resultados
    """
    if not resultados:
        return resultados
        
    resultados_com_sinalizadores = []
    
    for resultado in resultados:
        resultado_novo = resultado.copy()
        
        if tipo_resultado == 'casais':
            # Para casais
            prioridade_a = obter_prioridade_destino(df, resultado['Juiz A'], resultado['Destino A'])
            prioridade_b = obter_prioridade_destino(df, resultado['Juiz B'], resultado['Destino B'])
            
            # Adicionar sinalizadores
            if prioridade_a == 2:
                resultado_novo['Destino A'] = f"{resultado['Destino A']} ²"
            elif prioridade_a == 3:
                resultado_novo['Destino A'] = f"{resultado['Destino A']} ³"
                
            if prioridade_b == 2:
                resultado_novo['Destino B'] = f"{resultado['Destino B']} ²"
            elif prioridade_b == 3:
                resultado_novo['Destino B'] = f"{resultado['Destino B']} ³"
                
        elif tipo_resultado == 'triangulos':
            # Para triangulações
            prioridade_a = obter_prioridade_destino(df, resultado['Juiz A'], resultado['A ➝'])
            prioridade_b = obter_prioridade_destino(df, resultado['Juiz B'], resultado['B ➝'])
            prioridade_c = obter_prioridade_destino(df, resultado['Juiz C'], resultado['C ➝'])
            
            if prioridade_a == 2:
                resultado_novo['A ➝'] = f"{resultado['A ➝']} ²"
            elif prioridade_a == 3:
                resultado_novo['A ➝'] = f"{resultado['A ➝']} ³"
                
            if prioridade_b == 2:
                resultado_novo['B ➝'] = f"{resultado['B ➝']} ²"
            elif prioridade_b == 3:
                resultado_novo['B ➝'] = f"{resultado['B ➝']} ³"
                
            if prioridade_c == 2:
                resultado_novo['C ➝'] = f"{resultado['C ➝']} ²"
            elif prioridade_c == 3:
                resultado_novo['C ➝'] = f"{resultado['C ➝']} ³"
        
        resultados_com_sinalizadores.append(resultado_novo)
    
    return resultados_com_sinalizadores

def exibir_ciclos_didaticamente(ciclos, tipo_ciclo, origem_user, destino_user, df):
    """Exibe os ciclos de forma didática e visual com sinalizadores"""
    if not ciclos:
        return
        
    titulo = "◊ Quadrangulações"
    
    st.success(f"{titulo}: {len(ciclos)} encontrada(s) para seu caso!")
    
    for idx, ciclo in enumerate(ciclos, 1):
        with st.container():
            st.markdown(f"### 🔄 {titulo[2:]} #{idx}")
            
            # Extrair participantes
            participantes = []
            letras = ['A', 'B', 'C', 'D']
            
            for i in range(tipo_ciclo):
                letra = letras[i]
                juiz_key = f"Juiz {letra}"
                origem_key = f"Origem {letra}"
                entrancia_key = f"Entrância {letra}"
                destino_key = f"{letra} ➝"
                
                if juiz_key in ciclo and origem_key in ciclo:
                    vai_para_original = ciclo.get(destino_key, '')
                    prioridade = obter_prioridade_destino(df, ciclo[juiz_key], vai_para_original)
                    
                    # Adicionar sinalizador de prioridade
                    vai_para_com_sinalizador = vai_para_original
                    if prioridade == 2:
                        vai_para_com_sinalizador = f"{vai_para_original} ²"
                    elif prioridade == 3:
                        vai_para_com_sinalizador = f"{vai_para_original} ³"
                    
                    participante = {
                        'nome': ciclo[juiz_key],
                        'entrancia': ciclo.get(entrancia_key, 'Não informada'),
                        'origem': ciclo[origem_key],
                        'vai_para': vai_para_com_sinalizador,
                        'prioridade': prioridade
                    }
                    participantes.append(participante)
            
            # Fluxo visual em colunas
            st.markdown("#### 🔀 Como funciona esta permuta:")
            cols = st.columns(tipo_ciclo)
            
            for i, participante in enumerate(participantes):
                with cols[i]:
                    cor_fundo = "#e8f5e8" if participante['origem'] == origem_user else "#f8f9fa"
                    
                    # Cor do destino baseada na prioridade
                    cor_destino = "#1976d2"  # Azul para prioridade 1
                    if participante['prioridade'] == 2:
                        cor_destino = "#ff9800"  # Laranja para prioridade 2
                    elif participante['prioridade'] == 3:
                        cor_destino = "#f44336"  # Vermelho para prioridade 3
                    
                    st.markdown(
                        f"""
                        <div style='background: {cor_fundo}; padding: 1rem; border-radius: 8px; 
                                    border: 2px solid {"#4caf50" if participante["origem"] == origem_user else "#dee2e6"}; 
                                    text-align: center; margin-bottom: 0.5rem;'>
                            <strong>👨‍⚖️ {participante['nome'][:20]}{"..." if len(participante['nome']) > 20 else ""}</strong><br>
                            <span style='color: #666; font-size: 0.9em;'>{participante['entrancia']}</span><br>
                            <div style='margin: 0.5rem 0; padding: 0.5rem; background: white; border-radius: 4px;'>
                                <strong>📍 Está em:</strong><br>
                                <span style='color: #d32f2f; font-weight: bold;'>{participante['origem']}</span>
                            </div>
                            <div style='margin: 0.5rem 0; padding: 0.5rem; background: white; border-radius: 4px;'>
                                <strong>🎯 Vai para:</strong><br>
                                <span style='color: {cor_destino}; font-weight: bold;'>{participante['vai_para']}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if i < len(participantes) - 1:
                        st.markdown("<div style='text-align: center; font-size: 1.5rem; color: #4caf50;'>➡️</div>", unsafe_allow_html=True)
            
            # Resumo textual
            st.markdown("#### 📋 Resumo da Permuta:")
            for i, participante in enumerate(participantes):
                proximo_idx = (i + 1) % len(participantes)
                proximo = participantes[proximo_idx]
                emoji_user = "🎯 " if participante['origem'] == origem_user else ""
                st.markdown(f"• {emoji_user}**{participante['nome']}** sai do **{participante['origem']}** → vai para **{participante['vai_para']}**")
            
            # Resultado para o usuário
            if origem_user and destino_user:
                usuario_encontrado = None
                for participante in participantes:
                    if participante['origem'] == origem_user:
                        usuario_encontrado = participante
                        break
                
                if usuario_encontrado:
                    st.markdown("#### ✨ Resultado para Você:")
                    destino_limpo = usuario_encontrado['vai_para'].replace(' ²', '').replace(' ³', '')
                    if destino_limpo == destino_user:
                        st.success(f"🎯 **Perfeito!** Você conseguirá ir do **{origem_user}** para o **{usuario_encontrado['vai_para']}** nesta permuta!")
                    else:
                        st.info(f"📍 Nesta permuta, você iria do **{origem_user}** para o **{usuario_encontrado['vai_para']}** (não exatamente seu destino preferido, mas pode ser uma oportunidade!)")
            
            if idx < len(ciclos):
                st.markdown("---")

def criar_grafico_simples_tribunais_procurados(df):
    """Cria gráfico simples dos 7 tribunais mais procurados"""
    destinos_count = {}
    
    for _, linha in df.iterrows():
        destinos = [linha.get("Destino 1"), linha.get("Destino 2"), linha.get("Destino 3")]
        for destino in destinos:
            if destino and str(destino).strip():
                destino_clean = str(destino).strip()
                destinos_count[destino_clean] = destinos_count.get(destino_clean, 0) + 1
    
    top_7 = sorted(destinos_count.items(), key=lambda x: x[1], reverse=True)[:7]
    
    if not top_7:
        return None
        
    tribunais = [x[0] for x in top_7]
    valores = [x[1] for x in top_7]
    
    fig = go.Figure(data=[
        go.Bar(
            x=valores,
            y=tribunais,
            orientation='h',
            marker_color=px.colors.sequential.Blues_r[:len(tribunais)],
            text=valores,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="🎯 Top 7 Tribunais Mais Procurados",
        xaxis_title="Número de Preferências",
        height=300,
        margin=dict(l=80, r=50, t=50, b=50),
        plot_bgcolor='rgba(255,255,255,0.8)',
        paper_bgcolor='rgba(255,255,255,0)'
    )
    
    return fig

def criar_grafico_tribunais_conectados(df):
    """Cria gráfico dos 7 tribunais mais conectados (hub)"""
    conectividade = {}
    
    for _, linha in df.iterrows():
        origem = linha.get("Origem")
        if origem and str(origem).strip():
            origem_clean = str(origem).strip()
            if origem_clean not in conectividade:
                conectividade[origem_clean] = 0
            conectividade[origem_clean] += 1
    
    for _, linha in df.iterrows():
        destinos = [linha.get("Destino 1"), linha.get("Destino 2"), linha.get("Destino 3")]
        for destino in destinos:
            if destino and str(destino).strip():
                destino_clean = str(destino).strip()
                if destino_clean not in conectividade:
                    conectividade[destino_clean] = 0
                conectividade[destino_clean] += 1
    
    top_7 = sorted(conectividade.items(), key=lambda x: x[1], reverse=True)[:7]
    
    if not top_7:
        return None
        
    tribunais = [x[0] for x in top_7]
    valores = [x[1] for x in top_7]
    
    fig = go.Figure(data=[
        go.Bar(
            x=valores,
            y=tribunais,
            orientation='h',
            marker_color=px.colors.sequential.Greens_r[:len(tribunais)],
            text=valores,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="🔗 Top 7 Tribunais Mais Conectados (Hub)",
        xaxis_title="Total de Conexões",
        height=300,
        margin=dict(l=80, r=50, t=50, b=50),
        plot_bgcolor='rgba(255,255,255,0.8)',
        paper_bgcolor='rgba(255,255,255,0)'
    )
    
    return fig

def criar_grafico_tribunais_exportadores(df):
    """Cria gráfico dos 5 tribunais mais exportadores"""
    origens_count = {}
    
    for _, linha in df.iterrows():
        origem = linha.get("Origem")
        if origem and str(origem).strip():
            origem_clean = str(origem).strip()
            origens_count[origem_clean] = origens_count.get(origem_clean, 0) + 1
    
    top_5 = sorted(origens_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    if not top_5:
        return None
        
    tribunais = [x[0] for x in top_5]
    valores = [x[1] for x in top_5]
    
    fig = go.Figure(data=[
        go.Bar(
            x=valores,
            y=tribunais,
            orientation='h',
            marker_color=px.colors.sequential.Reds_r[:len(tribunais)],
            text=valores,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="📤 Top 5 Tribunais Mais Exportadores",
        xaxis_title="Juízes Querendo Sair",
        height=250,
        margin=dict(l=80, r=50, t=50, b=50),
        plot_bgcolor='rgba(255,255,255,0.8)',
        paper_bgcolor='rgba(255,255,255,0)'
    )
    
    return fig

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
# PERMUTRÔMETRO
# ===============================
st.markdown(
    """
    <div class="permutrometro-section">
        <h2>🎯 Permutrômetro - Panorama Inteligente da Base de Dados</h2>
        <p>Análise automática e visual dos dados de permuta em tempo real</p>
    </div>
    """,
    unsafe_allow_html=True
)

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
    triangulos_rapidos = len(buscar_triangulacoes(df))
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">✨ {casais_rapidos + triangulos_rapidos}</div>
            <p>Permutas + Triangulações</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ===============================
# Gráficos do Permutrômetro
# ===============================
st.markdown("### 📊 Análise Visual Automática")

col1, col2 = st.columns(2)

with col1:
    try:
        fig_procurados = criar_grafico_simples_tribunais_procurados(df)
        if fig_procurados:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_procurados, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.info("📊 Gráfico de procurados em carregamento...")

with col2:
    try:
        fig_conectados = criar_grafico_tribunais_conectados(df)
        if fig_conectados:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_conectados, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.info("🔗 Gráfico de conectados em carregamento...")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    try:
        fig_exportadores = criar_grafico_tribunais_exportadores(df)
        if fig_exportadores:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_exportadores, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.info("📤 Gráfico de exportadores em carregamento...")

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
# Botão de busca e resultados (OTIMIZADO - SÓ ATÉ QUADRANGULAÇÕES)
# ===============================
if st.button("✨ Buscar Permutas Diretas e Triangulações para meu caso", use_container_width=True):
    if not origem_user or not destino_user:
        st.warning("⚠️ Selecione origem e destino.")
    else:
        st.markdown(f"### Resultados para: {origem_user} → {destino_user}")
        
        # Buscar permutas (SÓ ATÉ QUADRANGULAÇÕES)
        casais = buscar_permutas_diretas(df, origem_user, destino_user)
        triangulos = buscar_triangulacoes(df, origem_user, destino_user)
        quadrangulos = buscar_quadrangulacoes(df, origem_user, destino_user)
        
        # Adicionar legenda dos sinalizadores
        st.markdown(
            """
            <div style='background: #f0f9ff; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #0ea5e9;'>
                <strong>📖 Legenda dos Sinalizadores:</strong><br>
                <span style='color: #1976d2;'>• <strong>Sem sinal</strong> = Destino Prioritário (Destino 1)</span><br>
                <span style='color: #ff9800;'>• <strong>²</strong> = Destino Secundário (Destino 2)</span><br>
                <span style='color: #f44336;'>• <strong>³</strong> = Destino Terciário (Destino 3)</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Mostrar resultados com sinalizadores
        if casais:
            casais_com_sinalizadores = adicionar_sinalizadores_prioridade(casais, df, 'casais')
            st.success(f"🎯 {len(casais_com_sinalizadores)} permuta(s) direta(s) encontrada(s):")
            st.dataframe(pd.DataFrame(casais_com_sinalizadores), use_container_width=True)
            try:
                fig_casais = mostrar_mapa_casais(casais)
                st.plotly_chart(fig_casais, use_container_width=True)
            except:
                st.info("Mapa temporariamente indisponível")
        else:
            st.info("⚠️ Nenhuma permuta direta encontrada.")

        if triangulos:
            triangulos_com_sinalizadores = adicionar_sinalizadores_prioridade(triangulos, df, 'triangulos')
            st.success(f"🔺 {len(triangulos_com_sinalizadores)} triangulação(ões) encontrada(s):")
            st.dataframe(pd.DataFrame(triangulos_com_sinalizadores), use_container_width=True)
            try:
                fig_triangulos = mostrar_mapa_triangulacoes(triangulos)
                st.plotly_chart(fig_triangulos, use_container_width=True)
            except:
                st.info("Mapa temporariamente indisponível")
        else:
            st.info("⚠️ Nenhuma triangulação encontrada.")
            
        # Só quadrangulações (removemos penta e hexa para performance)
        if quadrangulos:
            exibir_ciclos_didaticamente(quadrangulos, 4, origem_user, destino_user, df)

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