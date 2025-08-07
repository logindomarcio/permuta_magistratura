import unicodedata

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto_norm = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = ''.join(c for c in texto_norm if not unicodedata.combining(c))
    return texto_sem_acento.strip().lower()

def buscar_permutas_diretas(df, origem_user=None, destino_user=None):
    casais = []
    
    # Normalizar entrada do usuário
    origem_user = normalizar_texto(origem_user) if origem_user else None
    destino_user = normalizar_texto(destino_user) if destino_user else None

    for i, linha_a in df.iterrows():
        origem_a = normalizar_texto(linha_a.get("Origem"))
        entrancia_a = linha_a.get("Entrância", "Não informada")
        destinos_a = [
            normalizar_texto(linha_a.get("Destino 1")),
            normalizar_texto(linha_a.get("Destino 2")),
            normalizar_texto(linha_a.get("Destino 3"))
        ]
        destinos_a = [d for d in destinos_a if d]

        for j, linha_b in df.iterrows():
            if i == j:
                continue

            origem_b = normalizar_texto(linha_b.get("Origem"))
            entrancia_b = linha_b.get("Entrância", "Não informada")
            destinos_b = [
                normalizar_texto(linha_b.get("Destino 1")),
                normalizar_texto(linha_b.get("Destino 2")),
                normalizar_texto(linha_b.get("Destino 3"))
            ]
            destinos_b = [d for d in destinos_b if d]

            if origem_b in destinos_a and origem_a in destinos_b:
                casal = {
                    "Juiz A": linha_a.get("Nome"),
                    "Entrância A": entrancia_a,
                    "Origem A": linha_a.get("Origem"),
                    "Destino A": linha_b.get("Origem"),

                    "Juiz B": linha_b.get("Nome"),
                    "Entrância B": entrancia_b,
                    "Origem B": linha_b.get("Origem"),
                    "Destino B": linha_a.get("Origem")
                }

                if origem_user and destino_user:
                    if not (
                        (origem_a == origem_user and origem_b == destino_user) or
                        (origem_b == origem_user and origem_a == destino_user)
                    ):
                        continue

                casais.append(casal)

    return casais

def buscar_triangulacoes(df, origem_user=None, destino_user=None):
    triangulos = []

    origem_user = normalizar_texto(origem_user) if origem_user else None
    destino_user = normalizar_texto(destino_user) if destino_user else None

    for i, linha_a in df.iterrows():
        origem_a = normalizar_texto(linha_a.get("Origem"))
        entrancia_a = linha_a.get("Entrância", "Não informada")
        destinos_a = [
            normalizar_texto(linha_a.get("Destino 1")),
            normalizar_texto(linha_a.get("Destino 2")),
            normalizar_texto(linha_a.get("Destino 3"))
        ]
        destinos_a = [d for d in destinos_a if d]

        for j, linha_b in df.iterrows():
            if i == j:
                continue

            origem_b = normalizar_texto(linha_b.get("Origem"))
            entrancia_b = linha_b.get("Entrância", "Não informada")
            destinos_b = [
                normalizar_texto(linha_b.get("Destino 1")),
                normalizar_texto(linha_b.get("Destino 2")),
                normalizar_texto(linha_b.get("Destino 3"))
            ]
            destinos_b = [d for d in destinos_b if d]

            if origem_b not in destinos_a:
                continue

            for k, linha_c in df.iterrows():
                if k in [i, j]:
                    continue

                origem_c = normalizar_texto(linha_c.get("Origem"))
                entrancia_c = linha_c.get("Entrância", "Não informada")
                destinos_c = [
                    normalizar_texto(linha_c.get("Destino 1")),
                    normalizar_texto(linha_c.get("Destino 2")),
                    normalizar_texto(linha_c.get("Destino 3"))
                ]
                destinos_c = [d for d in destinos_c if d]

                if origem_c not in destinos_b:
                    continue

                if origem_a in destinos_c:
                    triangulo = {
                        "Juiz A": linha_a.get("Nome"),
                        "Entrância A": entrancia_a,
                        "Origem A": linha_a.get("Origem"),
                        "A ➝": linha_b.get("Origem"),

                        "Juiz B": linha_b.get("Nome"),
                        "Entrância B": entrancia_b,
                        "Origem B": linha_b.get("Origem"),
                        "B ➝": linha_c.get("Origem"),

                        "Juiz C": linha_c.get("Nome"),
                        "Entrância C": entrancia_c,
                        "Origem C": linha_c.get("Origem"),
                        "C ➝": linha_a.get("Origem")
                    }

                    if origem_user and destino_user:
                        if not (
                            (origem_a == origem_user and origem_b == destino_user) or
                            (origem_b == origem_user and origem_c == destino_user) or
                            (origem_c == origem_user and origem_a == destino_user)
                        ):
                            continue

                    triangulos.append(triangulo)

    return triangulos

def buscar_ciclos_n(df, tamanho_ciclo, origem_user=None, destino_user=None):
    """
    Função genérica para buscar ciclos de qualquer tamanho (4, 5, 6, etc.)
    """
    if tamanho_ciclo < 4:
        return []
    
    origem_user = normalizar_texto(origem_user) if origem_user else None
    destino_user = normalizar_texto(destino_user) if destino_user else None
    
    ciclos = []
    indices_processados = set()
    
    def buscar_ciclo_recursivo(caminho_atual, indices_usados, tamanho_alvo):
        if len(caminho_atual) == tamanho_alvo:
            # Verificar se o último elemento pode voltar ao primeiro
            ultimo_juiz = caminho_atual[-1]
            primeiro_juiz = caminho_atual[0]
            
            destinos_ultimo = [
                normalizar_texto(ultimo_juiz.get("Destino 1")),
                normalizar_texto(ultimo_juiz.get("Destino 2")),
                normalizar_texto(ultimo_juiz.get("Destino 3"))
            ]
            destinos_ultimo = [d for d in destinos_ultimo if d]
            
            origem_primeiro = normalizar_texto(primeiro_juiz.get("Origem"))
            
            if origem_primeiro in destinos_ultimo:
                # Criar o resultado do ciclo
                ciclo_resultado = {}
                letras = ['A', 'B', 'C', 'D', 'E', 'F']
                
                for idx, juiz in enumerate(caminho_atual):
                    letra = letras[idx]
                    proximo_idx = (idx + 1) % len(caminho_atual)
                    proximo_juiz = caminho_atual[proximo_idx]
                    
                    ciclo_resultado[f"Juiz {letra}"] = juiz.get("Nome")
                    ciclo_resultado[f"Entrância {letra}"] = juiz.get("Entrância", "Não informada")
                    ciclo_resultado[f"Origem {letra}"] = juiz.get("Origem")
                    ciclo_resultado[f"{letra} ➝"] = proximo_juiz.get("Origem")
                
                # Verificar filtro do usuário se especificado
                if origem_user and destino_user:
                    usuario_encontrado = False
                    for juiz in caminho_atual:
                        origem_juiz = normalizar_texto(juiz.get("Origem"))
                        if origem_juiz == origem_user:
                            # Verificar se algum dos próximos na cadeia tem o destino desejado
                            for outro_juiz in caminho_atual:
                                origem_outro = normalizar_texto(outro_juiz.get("Origem"))
                                if origem_outro == destino_user:
                                    usuario_encontrado = True
                                    break
                            break
                    
                    if not usuario_encontrado:
                        return
                
                ciclos.append(ciclo_resultado)
            return
        
        # Continuar construindo o caminho
        if not caminho_atual:
            # Primeiro juiz do caminho
            for i, linha in df.iterrows():
                if i not in indices_processados:
                    buscar_ciclo_recursivo([linha], {i}, tamanho_alvo)
                    indices_processados.add(i)
        else:
            # Juízes subsequentes
            ultimo_juiz = caminho_atual[-1]
            destinos_ultimo = [
                normalizar_texto(ultimo_juiz.get("Destino 1")),
                normalizar_texto(ultimo_juiz.get("Destino 2")),
                normalizar_texto(ultimo_juiz.get("Destino 3"))
            ]
            destinos_ultimo = [d for d in destinos_ultimo if d]
            
            for j, linha in df.iterrows():
                if j in indices_usados:
                    continue
                
                origem_linha = normalizar_texto(linha.get("Origem"))
                if origem_linha in destinos_ultimo:
                    novo_caminho = caminho_atual + [linha]
                    novos_indices = indices_usados | {j}
                    buscar_ciclo_recursivo(novo_caminho, novos_indices, tamanho_alvo)
    
    # Iniciar busca
    buscar_ciclo_recursivo([], set(), tamanho_ciclo)
    
    # Remover duplicatas (mesmo ciclo começando de pontos diferentes)
    ciclos_unicos = []
    assinaturas_vistas = set()
    
    for ciclo in ciclos:
        # Criar assinatura baseada nas origens ordenadas
        origens = []
        letras = ['A', 'B', 'C', 'D', 'E', 'F']
        for letra in letras[:tamanho_ciclo]:
            key = f"Origem {letra}"
            if key in ciclo:
                origens.append(normalizar_texto(ciclo[key]))
        
        assinatura = tuple(sorted(origens))
        if assinatura not in assinaturas_vistas:
            assinaturas_vistas.add(assinatura)
            ciclos_unicos.append(ciclo)
    
    return ciclos_unicos

def buscar_quadrangulacoes(df, origem_user=None, destino_user=None):
    """Buscar ciclos de 4 pessoas"""
    return buscar_ciclos_n(df, 4, origem_user, destino_user)

def buscar_pentagulacoes(df, origem_user=None, destino_user=None):
    """Buscar ciclos de 5 pessoas"""
    return buscar_ciclos_n(df, 5, origem_user, destino_user)

def buscar_hexagulacoes(df, origem_user=None, destino_user=None):
    """Buscar ciclos de 6 pessoas"""
    return buscar_ciclos_n(df, 6, origem_user, destino_user)

def calcular_estatisticas_tribunais(df):
    """
    Calcula estatísticas sobre tribunais mais procurados, exportadores e conectados
    """
    tribunais_stats = {}
    
    # Inicializar contadores
    for _, linha in df.iterrows():
        origem = linha.get("Origem", "").strip()
        if origem and origem not in tribunais_stats:
            tribunais_stats[origem] = {
                'procurado': 0,  # quantas pessoas querem ir para lá
                'exportador': 0,  # quantas pessoas querem sair de lá
                'conectividade': 0  # total de conexões
            }
    
    # Contar preferências
    for _, linha in df.iterrows():
        origem = linha.get("Origem", "").strip()
        
        # Contar como exportador (pessoas querendo sair)
        if origem in tribunais_stats:
            tribunais_stats[origem]['exportador'] += 1
        
        # Contar destinos desejados (procurados)
        destinos = [
            linha.get("Destino 1", ""),
            linha.get("Destino 2", ""),
            linha.get("Destino 3", "")
        ]
        
        for destino in destinos:
            destino = destino.strip() if destino else ""
            if destino and destino in tribunais_stats:
                tribunais_stats[destino]['procurado'] += 1
    
    # Calcular conectividade (soma de procurado + exportador)
    for tribunal in tribunais_stats:
        tribunais_stats[tribunal]['conectividade'] = (
            tribunais_stats[tribunal]['procurado'] + 
            tribunais_stats[tribunal]['exportador']
        )
    
    return tribunais_stats