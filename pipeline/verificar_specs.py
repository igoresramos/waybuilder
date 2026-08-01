#!/usr/bin/env python3
"""Portao das specs -- o frontmatter e um contrato, e este script cobra.

Por que existe
--------------
Ate 2026-08-01 o campo `status` nao informava nada: 73 das 75 specs diziam
`aprovada`, incluindo as que ja estavam no ar ha uma semana e as que eram so
intencao. Uma spec (`slots-e-candidatos`) precisou de um paragrafo no CORPO para
dizer que o proprio campo estava errado.

E o campo `todo: NN` apontava para o `TODO.md`, que saiu do repo no commit
`58658db`. Setenta e cinco ponteiros para um arquivo que nao viaja junto.

As duas coisas se resolvem com um contrato de frontmatter -- e contrato sem
portao e decoracao, como o portao 3 ja ensinou aqui (ele varria `requires` e
nunca `subclasses[].opcoes`, justamente o campo que o passo 7c conserta).

O que ele cobra
---------------
1. `req` existe, e unico e tem a forma `WB-NNN`.
2. `status` esta no vocabulario de quatro valores.
3. `status: substituida` exige `substituida_por` apontando para um `req` real.
4. `altera` aponta so para `req` que existe.
5. **`status: implementada` exige PROVA no disco.** Nao basta declarar: a spec
   tem de citar ao menos um artefato (script, componente, identificador) que
   exista de fato no repo. E a mesma regra que o projeto aplica ao dado --
   nao declarar sem verificar.
6. Contrato grande citado por `altera` tem de listar quem o altera (a
   referencia e nos DOIS sentidos -- instrucao do Alexandre no item SPEC-06).

Uso:
    python3 pipeline/verificar_specs.py            # falha com exit 1
    python3 pipeline/verificar_specs.py --listar   # so mostra o estado
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SPECS = RAIZ / "specs"

STATUS_VALIDOS = ("rascunho", "aprovada", "implementada", "substituida")

# Onde um artefato citado por uma spec pode estar. Nao varre o repo inteiro:
# `node_modules` e `pipeline/base` sao ruido de milhares de arquivos.
ARVORES = ("pipeline", "motor", "app/src", "app/verificacao", "app/public")
IGNORAR = ("node_modules", "dados_brutos", "pipeline/base", "app/public/base")

RE_ARQUIVO = re.compile(r"[\w\-/]+\.(?:py|mjs|ts|tsx|sh|json)")
RE_SIMBOLO = re.compile(r"`(_?[a-z][a-z0-9_]{4,})`")

# Arquivo que TODA spec cita nao prova nada. A prova tem de ser especifica --
# um script proprio, um componente proprio, um termo que a spec criou.
GENERICOS = {
    "motor.py", "personagem.ts", "build.sh", "portoes.py", "comum.py",
    "doc.ts", "App.tsx", "tipos.ts", "base.ts", "teste_motor.py",
    "reconciliar.py", "index.json", "ficha.py", "gerar_fixtures.py",
}


def frontmatter(txt: str) -> dict[str, str]:
    """Le o bloco YAML simples do topo. Nao e um parser de YAML -- as specs
    usam so `chave: valor` escalar e lista curta em linha."""
    if not txt.startswith("---"):
        return {}
    fm: dict[str, str] = {}
    for linha in txt.split("---", 2)[1].splitlines():
        chave, sep, valor = linha.partition(":")
        if sep and not chave.startswith(" "):
            fm[chave.strip()] = valor.strip()
    return fm


def lista(valor: str) -> list[str]:
    """`[WB-001, WB-002]` ou `WB-001` -> lista de ids."""
    return re.findall(r"WB-\d{3}", valor or "")


def indexar_disco() -> tuple[set[str], str]:
    """Nomes de arquivo que existem, e o texto do codigo todo concatenado.

    O texto serve para a prova por SIMBOLO: uma spec de motor nao cita
    arquivo, cita o termo que ela criou (`grant_actor`, `_avaliando_em`).
    """
    nomes: set[str] = set()
    partes: list[str] = []
    for arvore in ARVORES:
        raiz = RAIZ / arvore
        if not raiz.exists():
            continue
        for p in raiz.rglob("*"):
            if not p.is_file() or p.suffix not in (".py", ".mjs", ".ts", ".tsx", ".sh", ".json"):
                continue
            rel = p.relative_to(RAIZ).as_posix()
            if any(ig in rel for ig in IGNORAR):
                continue
            nomes.add(p.name)
            if p.suffix != ".json":
                try:
                    partes.append(p.read_text(encoding="utf-8", errors="ignore"))
                except OSError:
                    pass
    return nomes, "\n".join(partes)


VAZIAS = {"de", "do", "da", "dos", "das", "e", "o", "a", "os", "as", "por",
          "no", "na", "com", "sem", "em", "um", "uma", "para", "que"}


def prova_por_nome_de_script(slug: str, wiring: str) -> str | None:
    """Script LIGADO no build.sh cujo nome sai do assunto da spec.

    Nasceu de um falso negativo: `variante-por-subclasse` saiu `aprovada`
    porque a spec nao cita `derivar_variante_por_subclasse.py` em lugar nenhum
    -- o script existe, esta no passo 7d3 do build, e ninguem escreveu o nome
    dele no texto. Casar por assunto pega esse caso sem afrouxar a regra: o
    script tem de estar no `build.sh` E dividir duas palavras com o slug.

    Duas e o piso certo. Uma casaria `derivar_eixo_por_tag` com qualquer spec
    que tenha "tag" no nome.
    """
    palavras = {p for p in slug.split("-") if p not in VAZIAS and len(p) > 2}
    for script in set(re.findall(r"([a-z_]+)\.py", wiring)):
        if len(palavras & set(script.split("_"))) >= 2:
            return f"{script}.py"
    return None


def provas(txt: str, nomes: set[str], codigo: str, wiring: str = "",
           slug: str = "") -> list[str]:
    """Artefatos citados pela spec que existem de fato -- e so os FORTES.

    A primeira versao desta funcao aceitava qualquer nome citado e qualquer
    palavra entre crases. Rodada na base, ela marcou **as 75 specs** como
    implementadas -- ou seja, reintroduziu exatamente o defeito que este portao
    existe para matar (um campo que diz a mesma coisa para todo mundo nao diz
    nada). `requires`, `trained` e `eidolon` casavam com o codigo por serem
    vocabulario do dominio, nao por serem prova.

    Sobraram duas provas, as duas dificeis de falsear:

    1. **script proprio ligado ao pipeline** -- o arquivo existe E aparece no
       `build.sh`, ou e uma verificacao de navegador em `app/verificacao/`;
    2. **identificador com `_`** -- `grant_actor`, `_avaliando_em`,
       `_orcamento_de_pericia`. O underscore e o que separa termo criado pela
       spec de palavra que ja existia no jogo.
    """
    achados: list[str] = []
    if slug:
        por_nome = prova_por_nome_de_script(slug, wiring)
        if por_nome:
            achados.append(por_nome)
    for citado in dict.fromkeys(RE_ARQUIVO.findall(txt)):
        nome = citado.rsplit("/", 1)[-1]
        if nome not in nomes or nome in GENERICOS:
            continue
        if nome in wiring or nome.endswith(".mjs"):
            achados.append(nome)
    for simbolo in dict.fromkeys(RE_SIMBOLO.findall(txt)):
        if "_" in simbolo and simbolo in codigo:
            achados.append(simbolo)
        if len(achados) >= 3:
            break
    return achados


_BASE_CACHE: str | None = None


def texto_da_base() -> str:
    """`base/index.json` como TEXTO, carregado sob demanda.

    Serve para a prova explicita: uma spec de DADO nao produz script nem
    identificador de codigo -- ela produz registro. `nomear-o-balaio-por-tag`
    e o caso: a prova dela e o eixo `exemplar-root-epithet` existir na base, e
    nenhuma das outras duas provas alcanca isso.

    Texto e nao JSON de proposito: busca por substring resolve, e parsear 40 MB
    a cada rodada de portao nao se paga.
    """
    global _BASE_CACHE
    if _BASE_CACHE is None:
        caminho = RAIZ / "pipeline" / "base" / "index.json"
        _BASE_CACHE = (
            caminho.read_text(encoding="utf-8", errors="ignore")
            if caminho.exists() else ""
        )
    return _BASE_CACHE


def prova_explicita(fm: dict[str, str], codigo: str) -> str | None:
    """O campo `prova:` -- escape para quando a deteccao automatica erra.

    Ele NAO e uma declaracao livre: o portao confere que o que foi declarado
    existe mesmo, no codigo ou na base. Declarar `prova: coisa-que-nao-existe`
    falha igual a nao declarar nada.
    """
    declarada = fm.get("prova", "").strip().strip("`")
    if not declarada:
        return None
    if declarada in codigo or declarada in texto_da_base():
        return declarada
    return None


def wiring_do_build() -> str:
    """O `build.sh` inteiro -- serve para saber se um script esta LIGADO."""
    caminho = RAIZ / "pipeline" / "build.sh"
    return caminho.read_text(encoding="utf-8", errors="ignore") if caminho.exists() else ""


INICIO = "<!-- specs-que-alteram:start -->"
FIM = "<!-- specs-que-alteram:end -->"


def atualizar_tabelas(fichas) -> int:
    """Reescreve, em cada contrato grande, a lista de quem o altera.

    A instrucao era "devem poder se referenciar" -- nos DOIS sentidos. A spec
    pequena declara `altera: WB-002`; o contrato grande precisa dizer de volta
    quem mexeu nele, senao quem le o contrato continua lendo a versao de 26/07
    sem saber que cinco termos novos entraram depois.

    Gerado, nunca escrito a mao: lista a mao ja errou tres vezes neste projeto
    (as 16 classes que dao class feat no nivel 1 foram 3 -> 6 -> 16).
    """
    por_req = {fm.get("req"): (c, fm, t) for c, fm, t in fichas}
    quem_altera: dict[str, list[tuple[str, str]]] = {}
    for caminho, fm, _ in fichas:
        for alvo in lista(fm.get("altera", "")):
            quem_altera.setdefault(alvo, []).append(
                (fm.get("req", ""), fm.get("spec", caminho.stem))
            )

    escritos = 0
    for alvo, alteradores in sorted(quem_altera.items()):
        if alvo not in por_req:
            continue
        caminho, _, txt = por_req[alvo]
        linhas = [
            INICIO,
            "",
            "## Specs que alteram este contrato",
            "",
            "> Gerado por `pipeline/verificar_specs.py --tabelas`. Nao editar a mao.",
            "> Uma spec entra aqui quando declara `altera:` apontando para este `req`.",
            "",
            "| req | spec |",
            "|---|---|",
        ]
        for req, spec in sorted(alteradores):
            linhas.append(f"| `{req}` | `{spec}` |")
        linhas += ["", FIM]
        bloco = "\n".join(linhas)

        if INICIO in txt and FIM in txt:
            antes = txt[: txt.index(INICIO)]
            depois = txt[txt.index(FIM) + len(FIM):]
            novo = antes + bloco + depois
        else:
            novo = txt.rstrip() + "\n\n---\n\n" + bloco + "\n"
        if novo != txt:
            caminho.write_text(novo, encoding="utf-8")
            escritos += 1
    return escritos


def main() -> int:
    nomes, codigo = indexar_disco()
    wiring = wiring_do_build()
    # Uma spec e um `.md` com `spec:` no frontmatter. `CONVENCAO.md` e outros
    # documentos de apoio moram na mesma pasta e nao sao specs -- a primeira
    # versao deste portao reprovou a propria convencao que ele documenta.
    fichas = []
    for caminho in sorted(SPECS.glob("*.md")):
        txt = caminho.read_text(encoding="utf-8")
        fm = frontmatter(txt)
        if "spec" in fm:
            fichas.append((caminho, fm, txt))

    if "--tabelas" in sys.argv:
        n = atualizar_tabelas(fichas)
        print(f"tabelas de referencia cruzada reescritas em {n} contrato(s)")
        fichas = [(c, frontmatter(c.read_text(encoding="utf-8")),
                   c.read_text(encoding="utf-8")) for c, _, _ in fichas]

    por_req = {fm.get("req"): c for c, fm, _ in fichas if fm.get("req")}
    falhas: list[str] = []

    for caminho, fm, txt in fichas:
        nome = caminho.name
        req = fm.get("req", "")

        if not re.fullmatch(r"WB-\d{3}", req):
            falhas.append(f"{nome}: `req` ausente ou fora do formato WB-NNN ({req!r})")
            continue

        status = fm.get("status", "")
        if status not in STATUS_VALIDOS:
            falhas.append(
                f"{nome}: `status: {status}` fora do vocabulario "
                f"{'|'.join(STATUS_VALIDOS)}"
            )

        if status == "substituida":
            alvo = fm.get("substituida_por", "")
            if not lista(alvo):
                falhas.append(f"{nome}: `substituida` sem `substituida_por`")
            elif lista(alvo)[0] not in por_req:
                falhas.append(f"{nome}: `substituida_por: {alvo}` nao existe")

        for alvo in lista(fm.get("altera", "")):
            if alvo not in por_req:
                falhas.append(f"{nome}: `altera: {alvo}` nao existe")
            else:
                grande = por_req[alvo].read_text(encoding="utf-8")
                if req not in grande:
                    falhas.append(
                        f"{nome}: declara `altera: {alvo}` mas "
                        f"{por_req[alvo].name} nao cita {req} de volta"
                    )

        if status == "implementada":
            if not provas(txt, nomes, codigo, wiring, caminho.stem)                     and not prova_explicita(fm, codigo):
                falhas.append(
                    f"{nome}: `implementada` sem prova -- nenhum artefato "
                    f"citado por ela existe no disco, e o campo `prova:` "
                    f"esta ausente ou aponta para algo inexistente"
                )

    contagem: dict[str, int] = {}
    for _, fm, _ in fichas:
        contagem[fm.get("status", "?")] = contagem.get(fm.get("status", "?"), 0) + 1

    if "--listar" in sys.argv:
        for caminho, fm, txt in fichas:
            print(
                f"{fm.get('req','?????'):8} {fm.get('status','?'):13} "
                f"{caminho.name}  {' '.join(provas(txt, nomes, codigo, wiring, caminho.stem)[:2])}"
            )
        print()

    print(f"specs: {len(fichas)} -- " + ", ".join(f"{v} {k}" for k, v in sorted(contagem.items())))
    if falhas:
        print(f"\nPORTAO DE SPECS: {len(falhas)} falha(s)\n")
        for f in falhas:
            print("  -", f)
        return 1
    print("portao de specs: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
