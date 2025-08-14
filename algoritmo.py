import pandas as pd
from typing import List, Tuple, Dict, Set


DEBUG_MODE = True  # ✅ Ative/desative aqui


class Juiz:
    def __init__(self, nome, origem, destinos, entrancia):
        self.nome = nome.strip()
        self.origem = origem.strip()
        self.destinos = [d.strip() for d in destinos if isinstance(d, str) and d.strip()]
        self.entrancia = entrancia.strip() if isinstance(entrancia, str) else "Não informada"

    def quer_ir_para(self, local):
        return local.strip() in self.destinos

    def __repr__(self):
        return f"{self.nome} ({self.origem} → {self.destinos})"


def criar_juizes(df: pd.DataFrame) -> List[Juiz]:
    juizes = []
    for _, row in df.iterrows():
        juiz = Juiz(
            nome=row["Nome"],
            origem=row["Origem"],
            destinos=[row.get("Destino1", ""), row.get("Destino2", ""), row.get("Destino3", "")],
            entrancia=row.get("Entrância", "Não informada")
        )
        juizes.append(juiz)
    return juizes


def encontrar_casais(juizes: List[Juiz]) -> List[Tuple[Juiz, Juiz]]:
    casais = []
    for i, juiz_a in enumerate(juizes):
        for j, juiz_b in enumerate(juizes):
            if i >= j:
                continue
            if juiz_a.origem == juiz_b.origem:
                continue
            if juiz_a.quer_ir_para(juiz_b.origem) and juiz_b.quer_ir_para(juiz_a.origem):
                casais.append((juiz_a, juiz_b))
    return casais


def encontrar_triangulacoes(juizes: List[Juiz]) -> List[Tuple[Juiz, Juiz, Juiz]]:
    triangulacoes = []
    for a in juizes:
        for b in juizes:
            for c in juizes:
                if len({a.nome, b.nome, c.nome}) < 3:
                    continue
                if len({a.origem, b.origem, c.origem}) < 3:
                    continue
                if a.quer_ir_para(b.origem) and b.quer_ir_para(c.origem) and c.quer_ir_para(a.origem):
                    triangulacoes.append((a, b, c))
    return triangulacoes


def encontrar_quadrangulacoes(juizes: List[Juiz]) -> List[Tuple[Juiz, Juiz, Juiz, Juiz]]:
    quadrangulacoes = []
    for a in juizes:
        for b in juizes:
            for c in juizes:
                for d in juizes:
                    if len({a.nome, b.nome, c.nome, d.nome}) < 4:
                        continue
                    if len({a.origem, b.origem, c.origem, d.origem}) < 4:
                        continue
                    if a.quer_ir_para(b.origem) and b.quer_ir_para(c.origem) and c.quer_ir_para(d.origem) and d.quer_ir_para(a.origem):
                        quadrangulacoes.append((a, b, c, d))
    return quadrangulacoes


def formatar_nome_e_info(juiz: Juiz) -> str:
    destino = " / ".join(juiz.destinos)
    return f"{juiz.nome} ({juiz.origem} → {destino}) | Entrância: {juiz.entrancia}"


def formatar_casal(casal: Tuple[Juiz, Juiz]) -> str:
    a, b = casal
    return f"{formatar_nome_e_info(a)} ⇄ {formatar_nome_e_info(b)}"


def formatar_triangulacao(t: Tuple[Juiz, Juiz, Juiz]) -> str:
    return " → ".join(formatar_nome_e_info(j) for j in t)


def formatar_quadrangulacao(q: Tuple[Juiz, Juiz, Juiz, Juiz]) -> str:
    return " → ".join(formatar_nome_e_info(j) for j in q)


# ==========================
# 🧪 TESTES INTERNOS
# ==========================

def analisar_cobertura(juizes: List[Juiz], casais, triangulacoes, quadrangulacoes) -> Dict[str, Set[str]]:
    envolvidos = set()

    for casal in casais:
        envolvidos.update([casal[0].nome, casal[1].nome])
    for tri in triangulacoes:
        envolvidos.update([tri[0].nome, tri[1].nome, tri[2].nome])
    for quad in quadrangulacoes:
        envolvidos.update([quad[0].nome, quad[1].nome, quad[2].nome, quad[3].nome])

    nomes_todos = set(j.nome for j in juizes)
    nomes_nao_alcancados = nomes_todos - envolvidos

    if DEBUG_MODE:
        print("🔎 Total de juízes:", len(nomes_todos))
        print("✅ Juízes envolvidos em permutas:", len(envolvidos))
        print("❌ Juízes não envolvidos em nenhuma formação:", len(nomes_nao_alcancados))
        for nome in sorted(nomes_nao_alcancados):
            print(" -", nome)

    return {
        "todos": nomes_todos,
        "envolvidos": envolvidos,
        "nao_envolvidos": nomes_nao_alcancados
    }
