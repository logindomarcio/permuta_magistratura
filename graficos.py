import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def criar_grafico_tribunais_procurados(tribunais_stats):
    """
    Cria gráfico de barras dos tribunais mais procurados
    """
    # Ordenar por mais procurados
    dados_procurados = [(k, v['procurado']) for k, v in tribunais_stats.items() if v['procurado'] > 0]
    dados_procurados.sort(key=lambda x: x[1], reverse=True)
    
    # Pegar top 10
    top_10 = dados_procurados[:10]
    
    if not top_10:
        # Se não houver dados, criar gráfico vazio
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    tribunais = [x[0] for x in top_10]
    valores = [x[1] for x in top_10]
    
    # Criar cores degradê
    cores = px.colors.sequential.Blues_r[:len(tribunais)]
    
    fig = go.Figure(data=[
        go.Bar(
            x=tribunais,
            y=valores,
            text=valores,
            textposition='auto',
            marker_color=cores,
            hovertemplate='<b>%{x}</b><br>Procurado por: %{y} juízes<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': '🎯 Top 10 Tribunais Mais Procurados',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Inter', 'color': '#2c3e50'}
        },
        xaxis_title='Tribunais',
        yaxis_title='Número de Preferências',
        plot_bgcolor='rgba(255, 255, 255, 0.8)',
        paper_bgcolor='rgba(255, 255, 255, 0.5)',
        font=dict(family="Inter", size=12, color="#2c3e50"),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    fig.update_xaxis(tickangle=-45)
    
    return fig

def criar_grafico_tribunais_exportadores(tribunais_stats):
    """
    Cria gráfico de barras dos tribunais mais exportadores (mais saídas)
    """
    # Ordenar por mais exportadores
    dados_exportadores = [(k, v['exportador']) for k, v in tribunais_stats.items() if v['exportador'] > 0]
    dados_exportadores.sort(key=lambda x: x[1], reverse=True)
    
    # Pegar top 10
    top_10 = dados_exportadores[:10]
    
    if not top_10:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    tribunais = [x[0] for x in top_10]
    valores = [x[1] for x in top_10]
    
    # Criar cores degradê vermelhas
    cores = px.colors.sequential.Reds_r[:len(tribunais)]
    
    fig = go.Figure(data=[
        go.Bar(
            x=tribunais,
            y=valores,
            text=valores,
            textposition='auto',
            marker_color=cores,
            hovertemplate='<b>%{x}</b><br>Juízes querendo sair: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': '📤 Top 10 Tribunais Mais Exportadores',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Inter', 'color': '#2c3e50'}
        },
        xaxis_title='Tribunais',
        yaxis_title='Número de Juízes Querendo Sair',
        plot_bgcolor='rgba(255, 255, 255, 0.8)',
        paper_bgcolor='rgba(255, 255, 255, 0.5)',
        font=dict(family="Inter", size=12, color="#2c3e50"),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    fig.update_xaxis(tickangle=-45)
    
    return fig

def criar_grafico_tribunais_conectados(tribunais_stats):
    """
    Cria gráfico de barras dos tribunais mais conectados (mais procurados + mais exportadores)
    """
    # Ordenar por conectividade
    dados_conectividade = [(k, v['conectividade'], v['procurado'], v['exportador']) 
                          for k, v in tribunais_stats.items() if v['conectividade'] > 0]
    dados_conectividade.sort(key=lambda x: x[1], reverse=True)
    
    # Pegar top 10
    top_10 = dados_conectividade[:10]
    
    if not top_10:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    tribunais = [x[0] for x in top_10]
    conectividade_total = [x[1] for x in top_10]
    procurados = [x[2] for x in top_10]
    exportadores = [x[3] for x in top_10]
    
    fig = go.Figure()
    
    # Barra para procurados (azul)
    fig.add_trace(go.Bar(
        name='Procurados',
        x=tribunais,
        y=procurados,
        marker_color='rgba(31, 119, 180, 0.8)',
        hovertemplate='<b>%{x}</b><br>Procurado: %{y}<extra></extra>'
    ))
    
    # Barra para exportadores (vermelho)
    fig.add_trace(go.Bar(
        name='Exportadores',
        x=tribunais,
        y=exportadores,
        marker_color='rgba(214, 39, 40, 0.8)',
        hovertemplate='<b>%{x}</b><br>Exportador: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '🔗 Top 10 Tribunais Mais Conectados',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Inter', 'color': '#2c3e50'}
        },
        xaxis_title='Tribunais',
        yaxis_title='Número de Conexões',
        barmode='stack',
        plot_bgcolor='rgba(255, 255, 255, 0.8)',
        paper_bgcolor='rgba(255, 255, 255, 0.5)',
        font=dict(family="Inter", size=12, color="#2c3e50"),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxis(tickangle=-45)
    
    return fig

def criar_grafico_estatisticas_gerais(tribunais_stats, total_juizes):
    """
    Cria gráfico de pizza com estatísticas gerais
    """
    if not tribunais_stats:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Calcular dados
    total_procurados = sum(v['procurado'] for v in tribunais_stats.values())
    total_exportadores = sum(v['exportador'] for v in tribunais_stats.values())
    
    # Tribunais com alta demanda (mais procurados que exportadores)
    alta_demanda = sum(1 for v in tribunais_stats.values() if v['procurado'] > v['exportador'])
    
    # Tribunais exportadores líquidos
    exportadores_liquidos = sum(1 for v in tribunais_stats.values() if v['exportador'] > v['procurado'])
    
    # Tribunais equilibrados
    equilibrados = sum(1 for v in tribunais_stats.values() if v['procurado'] == v['exportador'])
    
    labels = ['Alta Demanda', 'Exportadores Líquidos', 'Equilibrados']
    values = [alta_demanda, exportadores_liquidos, equilibrados]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        marker_colors=colors,
        textinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>Tribunais: %{value}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': '📊 Distribuição dos Tribunais por Perfil',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Inter', 'color': '#2c3e50'}
        },
        plot_bgcolor='rgba(255, 255, 255, 0.8)',
        paper_bgcolor='rgba(255, 255, 255, 0.5)',
        font=dict(family="Inter", size=12, color="#2c3e50"),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig