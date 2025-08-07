import plotly.graph_objects as go

# Dicionário de coordenadas (latitude, longitude) para todos os TJs do Brasil
coordenadas_tj = {
    "TJAC": [-9.97499, -67.8243],
    "TJAL": [-9.66599, -35.7350],
    "TJAM": [-3.10719, -60.0261],
    "TJAP": [0.034934, -51.0694],
    "TJBA": [-12.9714, -38.5014],
    "TJCE": [-3.71722, -38.5433],
    "TJDFT": [-15.77972, -47.92972],
    "TJES": [-20.3155, -40.3128],
    "TJGO": [-16.6864, -49.2643],
    "TJMA": [-2.52972, -44.3028],
    "TJMG": [-19.9167, -43.9345],
    "TJMS": [-20.4428, -54.6464],
    "TJMT": [-15.5989, -56.0949],
    "TJPA": [-1.45583, -48.5039],
    "TJPB": [-7.1150, -34.8641],
    "TJPE": [-8.04756, -34.8770],
    "TJPI": [-5.08917, -42.8019],
    "TJPR": [-25.4284, -49.2733],
    "TJRJ": [-22.9035, -43.2096],
    "TJRN": [-5.79448, -35.2110],
    "TJRO": [-8.76194, -63.9039],
    "TJRR": [2.81972, -60.6733],
    "TJRS": [-30.0346, -51.2177],
    "TJSC": [-27.5969, -48.5495],
    "TJSE": [-10.9111, -37.0717],
    "TJSP": [-23.5505, -46.6333],
    "TJTO": [-10.1841, -48.3336]
}

def mostrar_mapa_casais(casais):
    fig = go.Figure()

    for c in casais:
        coords = []
        for tj in [c["Origem A"], c["Destino A"]]:
            if tj in coordenadas_tj:
                coords.append(coordenadas_tj[tj])

        if len(coords) == 2:
            lats = [c[0] for c in coords]
            lons = [c[1] for c in coords]
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines+markers',
                line=dict(width=3, color='green'),
                marker=dict(size=8, color='darkgreen'),
                name=f"{c['Juiz A']} ↔ {c['Juiz B']}"
            ))

    fig.update_layout(
        title={
            'text': "🔁 Permutas Diretas entre Juízes no Mapa do Brasil",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'serif', 'color': '#2c3e50'}
        },
        geo=dict(
            scope='south america',
            projection_type='mercator',
            showland=True,
            landcolor='rgb(253, 246, 227)',  # Cor bege
            countrycolor='rgb(139, 125, 107)',
            coastlinecolor='rgb(139, 125, 107)',
            showlakes=True,
            lakecolor='rgb(173, 216, 230)'
        ),
        font=dict(family="serif", size=12, color="#2c3e50"),
        paper_bgcolor='rgba(253, 246, 227, 0.5)'
    )
    return fig

def mostrar_mapa_triangulacoes(triangulos):
    fig = go.Figure()

    for t in triangulos:
        coords = []
        # Vamos considerar ORIGEM dos juízes para fechar o triângulo corretamente
        for tj in [t["Origem A"], t["Origem B"], t["Origem C"], t["Origem A"]]:
            if tj in coordenadas_tj:
                coords.append(coordenadas_tj[tj])

        if len(coords) == 4:
            lats = [c[0] for c in coords]
            lons = [c[1] for c in coords]
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines+markers',
                line=dict(width=3, color='blue'),
                marker=dict(size=8, color='darkblue'),
                name=f"{t['Juiz A']} ➝ {t['Juiz B']} ➝ {t['Juiz C']}"
            ))

    fig.update_layout(
        title={
            'text': "🔺 Triangulações entre Juízes no Mapa do Brasil",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'serif', 'color': '#2c3e50'}
        },
        geo=dict(
            scope='south america',
            projection_type='mercator',
            showland=True,
            landcolor='rgb(253, 246, 227)',  # Cor bege
            countrycolor='rgb(139, 125, 107)',
            coastlinecolor='rgb(139, 125, 107)',
            showlakes=True,
            lakecolor='rgb(173, 216, 230)'
        ),
        font=dict(family="serif", size=12, color="#2c3e50"),
        paper_bgcolor='rgba(253, 246, 227, 0.5)'
    )
    return fig

def mostrar_mapa_ciclos_n(ciclos, n):
    """
    Exibe ciclos de N pessoas no mapa
    """
    fig = go.Figure()
    
    # Cores diferentes para cada tipo de ciclo
    cores = {
        4: 'purple',
        5: 'orange', 
        6: 'red'
    }
    
    cor = cores.get(n, 'black')
    
    for idx, ciclo in enumerate(ciclos):
        coords = []
        letras = ['A', 'B', 'C', 'D', 'E', 'F']
        
        # Coletar coordenadas do ciclo
        for i in range(n):
            letra = letras[i]
            origem_key = f"Origem {letra}"
            if origem_key in ciclo:
                tj = ciclo[origem_key]
                if tj in coordenadas_tj:
                    coords.append(coordenadas_tj[tj])
        
        # Fechar o ciclo voltando ao primeiro ponto
        if coords:
            coords.append(coords[0])
        
        if len(coords) > 2:
            lats = [c[0] for c in coords]
            lons = [c[1] for c in coords]
            
            # Nome do ciclo baseado nos juízes
            nomes_juizes = []
            for i in range(min(3, n)):  # Mostrar apenas os 3 primeiros nomes
                letra = letras[i]
                juiz_key = f"Juiz {letra}"
                if juiz_key in ciclo:
                    nome = ciclo[juiz_key]
                    if len(nome) > 15:
                        nome = nome[:15] + "..."
                    nomes_juizes.append(nome)
            
            nome_ciclo = " ➝ ".join(nomes_juizes)
            if n > 3:
                nome_ciclo += f" ➝ ... (+{n-3})"
            
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines+markers',
                line=dict(width=3, color=cor),
                marker=dict(size=8, color=cor, opacity=0.8),
                name=nome_ciclo,
                hovertemplate=f'<b>Ciclo {idx+1}</b><br>%{{text}}<extra></extra>',
                text=[f"Ponto {i+1}" for i in range(len(lats))]
            ))

    # Título baseado no tipo de ciclo
    titulos = {
        4: "◊ Quadrangulações",
        5: "⬟ Pentagulações", 
        6: "⬢ Hexagulações"
    }
    
    titulo = titulos.get(n, f"Ciclos de {n} Pessoas")
    
    fig.update_layout(
        title={
            'text': f"{titulo} no Mapa do Brasil",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'serif', 'color': '#2c3e50'}
        },
        geo=dict(
            scope='south america',
            projection_type='mercator',
            showland=True,
            landcolor='rgb(253, 246, 227)',  # Cor bege
            countrycolor='rgb(139, 125, 107)',
            coastlinecolor='rgb(139, 125, 107)',
            showlakes=True,
            lakecolor='rgb(173, 216, 230)'
        ),
        font=dict(family="serif", size=12, color="#2c3e50"),
        paper_bgcolor='rgba(253, 246, 227, 0.5)',
        height=600
    )
    
    return fig