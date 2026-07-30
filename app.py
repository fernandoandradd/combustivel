# -*- coding: utf-8 -*-
"""
Margem Bruta de Combustíveis — UFISCAL
App Streamlit para analisar a margem bruta por litro de Gasolina Comum,
Diesel S10 e Diesel S500.

Execução:
    pip install streamlit pandas altair
    streamlit run margem_combustiveis.py
"""

import inspect
import io

import altair as alt
import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# Configuração
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Margem Bruta de Combustíveis | UFISCAL",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

FRETE_PADRAO = 0.17

# Compatibilidade: Streamlit >= 1.49 usa width="stretch"; versoes anteriores,
# use_container_width=True.
LARGURA_TOTAL = (
    {"width": "stretch"}
    if "width" in inspect.signature(st.button).parameters
    else {"use_container_width": True}
)

# Cores dos bicos de abastecimento (padrão de identificação do posto)
CORES = {
    "Gasolina Comum": "#F2B01E",
    "Diesel S10": "#33A06B",
    "Diesel S500": "#93A7BC",
}

PRODUTOS = list(CORES.keys())

COL_COMPRA = "Preço de compra (R$/L)"
COL_FRETE = "Frete (R$/L)"
COL_CUSTO = "Custo de compra (R$/L)"
COL_VENDA = "Preço de venda (R$/L)"
COL_MARG_RS = "Margem bruta (R$/L)"
COL_MARG_PC = "Margem bruta (%)"
COL_VOLUME = "Volume (L/mês)"
COL_LUCRO = "Margem bruta do mês (R$)"


# ──────────────────────────────────────────────────────────────────────────────
# Estilo
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
:root {
    --ink:      #111820;
    --panel:    #19212C;
    --panel-2:  #212B38;
    --line:     #2E3A49;
    --paper:    #F4F5F3;
    --text-dim: #93A2B4;
    --alert:    #E2503C;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1280px; }

/* Cabeçalho ------------------------------------------------------------- */
.totem-head {
    border-left: 6px solid var(--ink);
    padding: 0 0 0 18px;
    margin-bottom: 6px;
}
.totem-head .eyebrow {
    font-family: 'Barlow Condensed', sans-serif;
    text-transform: uppercase;
    letter-spacing: .22em;
    font-size: .82rem;
    font-weight: 600;
    color: #6B7C90;
    margin: 0;
}
.totem-head h1 {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.9rem;
    line-height: 1.02;
    font-weight: 700;
    letter-spacing: -.01em;
    text-transform: uppercase;
    color: var(--ink);
    margin: 2px 0 4px 0;
}
.totem-head p.sub { color: #5C6B7D; font-size: .93rem; margin: 0; }

/* Painéis de bomba ------------------------------------------------------ */
.pump {
    background: var(--panel);
    border-radius: 10px;
    padding: 18px 20px 16px 20px;
    border-top: 5px solid var(--stripe, #888);
    height: 100%;
    box-shadow: 0 1px 2px rgba(17,24,32,.18);
}
.pump .nome {
    font-family: 'Barlow Condensed', sans-serif;
    text-transform: uppercase;
    letter-spacing: .14em;
    font-size: .95rem;
    font-weight: 600;
    color: var(--stripe, #fff);
    margin-bottom: 10px;
}
.pump .digits {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.35rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
    font-variant-numeric: tabular-nums;
}
.pump .digits small {
    font-size: .95rem;
    font-weight: 500;
    color: var(--text-dim);
    margin-left: 6px;
}
.pump .pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--stripe, #fff);
    margin-top: 4px;
    font-variant-numeric: tabular-nums;
}
.pump .rodape {
    border-top: 1px solid var(--line);
    margin-top: 14px;
    padding-top: 10px;
    display: flex;
    justify-content: space-between;
    font-size: .78rem;
    color: var(--text-dim);
    font-variant-numeric: tabular-nums;
}
.pump.negativa .digits, .pump.negativa .pct { color: var(--alert); }

/* Faixa de resumo ------------------------------------------------------- */
.faixa {
    background: var(--paper);
    border: 1px solid #E2E5E0;
    border-radius: 10px;
    padding: 16px 22px;
    display: flex;
    gap: 46px;
    flex-wrap: wrap;
}
.faixa .item .rot {
    font-family: 'Barlow Condensed', sans-serif;
    text-transform: uppercase;
    letter-spacing: .16em;
    font-size: .74rem;
    color: #7A8798;
    font-weight: 600;
}
.faixa .item .val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--ink);
    font-variant-numeric: tabular-nums;
}

/* Títulos de seção ------------------------------------------------------ */
.secao {
    font-family: 'Barlow Condensed', sans-serif;
    text-transform: uppercase;
    letter-spacing: .18em;
    font-size: 1rem;
    font-weight: 600;
    color: #46556A;
    border-bottom: 1px solid #DDE1DC;
    padding-bottom: 6px;
    margin: 34px 0 14px 0;
}

section[data-testid="stSidebar"] { background: var(--paper); }
#MainMenu, footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────────────────────────────────────
def num_br(valor: float, casas: int = 4) -> str:
    """Formata número no padrão brasileiro (1.234,5678)."""
    if pd.isna(valor):
        return "—"
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".")


def base_inicial() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Produto": PRODUTOS,
            COL_COMPRA: [5.8500, 5.9500, 5.8000],
            COL_FRETE: [FRETE_PADRAO] * 3,
            COL_VENDA: [6.2900, 6.4900, 6.3500],
            COL_VOLUME: [30000.0, 40000.0, 12000.0],
        }
    )


def calcular(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for col in (COL_COMPRA, COL_FRETE, COL_VENDA, COL_VOLUME):
        d[col] = pd.to_numeric(d[col], errors="coerce").fillna(0.0)

    d[COL_CUSTO] = d[COL_COMPRA] + d[COL_FRETE]
    d[COL_MARG_RS] = d[COL_VENDA] - d[COL_CUSTO]
    d[COL_MARG_PC] = (d[COL_MARG_RS] / d[COL_VENDA].replace(0, pd.NA)) * 100
    d[COL_LUCRO] = d[COL_MARG_RS] * d[COL_VOLUME]
    return d[
        [
            "Produto",
            COL_COMPRA,
            COL_FRETE,
            COL_CUSTO,
            COL_VENDA,
            COL_MARG_RS,
            COL_MARG_PC,
            COL_VOLUME,
            COL_LUCRO,
        ]
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Estado
# ──────────────────────────────────────────────────────────────────────────────
if "dados" not in st.session_state:
    st.session_state.dados = base_inicial()


# ──────────────────────────────────────────────────────────────────────────────
# Barra lateral
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Parâmetros")

    frete_geral = st.number_input(
        "Frete padrão (R$/L)",
        min_value=0.0,
        value=FRETE_PADRAO,
        step=0.01,
        format="%.4f",
        help="Valor aplicado a todos os produtos. Você pode sobrescrever "
             "o frete de cada item diretamente na tabela.",
    )
    if st.button("Aplicar frete a todos os produtos", **LARGURA_TOTAL):
        st.session_state.dados[COL_FRETE] = frete_geral
        st.rerun()

    st.divider()
    usar_volume = st.toggle(
        "Analisar volume mensal",
        value=False,
        help="Habilita a coluna de litros vendidos e calcula a margem bruta "
             "total do mês por produto.",
    )

    st.divider()
    if st.button("Restaurar valores iniciais", **LARGURA_TOTAL):
        st.session_state.dados = base_inicial()
        st.rerun()

    st.caption(
        "Margem bruta comercial (preço de venda − custo de aquisição). "
        "Não considera despesas operacionais nem tributos recuperáveis."
    )


# ──────────────────────────────────────────────────────────────────────────────
# Cabeçalho
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="totem-head">
    <p class="eyebrow">UFISCAL · Inteligência em Negócios</p>
    <h1>Margem bruta de combustíveis</h1>
    <p class="sub">Preencha compra, frete e venda. O custo, a margem em R$ e a margem em % são calculados por litro.</p>
</div>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# Entrada de dados
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="secao">Tabela de apuração</div>', unsafe_allow_html=True)

tabela = calcular(st.session_state.dados)

colunas_visiveis = [
    "Produto",
    COL_COMPRA,
    COL_FRETE,
    COL_CUSTO,
    COL_VENDA,
    COL_MARG_RS,
    COL_MARG_PC,
]
if usar_volume:
    colunas_visiveis += [COL_VOLUME, COL_LUCRO]

config = {
    "Produto": st.column_config.TextColumn("Produto", width="medium", disabled=True),
    COL_COMPRA: st.column_config.NumberColumn(
        COL_COMPRA, min_value=0.0, step=0.01, format="%.4f",
        help="Preço na nota do distribuidor, por litro.",
    ),
    COL_FRETE: st.column_config.NumberColumn(
        COL_FRETE, min_value=0.0, step=0.01, format="%.4f",
        help=f"Valor sugerido: {num_br(FRETE_PADRAO)} por litro. Editável.",
    ),
    COL_CUSTO: st.column_config.NumberColumn(
        COL_CUSTO, format="%.4f", disabled=True,
        help="Preço de compra + frete.",
    ),
    COL_VENDA: st.column_config.NumberColumn(
        COL_VENDA, min_value=0.0, step=0.01, format="%.4f",
        help="Preço praticado na pista, por litro.",
    ),
    COL_MARG_RS: st.column_config.NumberColumn(
        COL_MARG_RS, format="%.4f", disabled=True,
        help="Preço de venda − custo de compra.",
    ),
    COL_MARG_PC: st.column_config.NumberColumn(
        COL_MARG_PC, format="%.2f%%", disabled=True,
        help="Margem em R$ dividida pelo preço de venda.",
    ),
    COL_VOLUME: st.column_config.NumberColumn(
        COL_VOLUME, min_value=0.0, step=1000.0, format="%.0f",
        help="Litros vendidos no período.",
    ),
    COL_LUCRO: st.column_config.NumberColumn(
        COL_LUCRO, format="%.2f", disabled=True,
        help="Margem em R$/L × volume.",
    ),
}

editado = st.data_editor(
    tabela[colunas_visiveis],
    column_config=config,
    hide_index=True,
    **LARGURA_TOTAL,
    num_rows="fixed",
    key="editor",
)

# Devolve ao estado apenas as colunas de entrada
entrada = st.session_state.dados.copy()
for col in (COL_COMPRA, COL_FRETE, COL_VENDA):
    entrada[col] = editado[col].values
if usar_volume:
    entrada[COL_VOLUME] = editado[COL_VOLUME].values
st.session_state.dados = entrada

df = calcular(entrada)

negativos = df.loc[df[COL_MARG_RS] < 0, "Produto"].tolist()
if negativos:
    st.error(
        "Margem negativa em: " + ", ".join(negativos)
        + ". O preço de venda está abaixo do custo de aquisição."
    )


# ──────────────────────────────────────────────────────────────────────────────
# Painéis por produto
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="secao">Margem por produto</div>', unsafe_allow_html=True)

colunas = st.columns(len(df), gap="medium")
for coluna, (_, linha) in zip(colunas, df.iterrows()):
    cor = CORES.get(linha["Produto"], "#888888")
    classe = "pump negativa" if linha[COL_MARG_RS] < 0 else "pump"
    pct = "—" if pd.isna(linha[COL_MARG_PC]) else num_br(linha[COL_MARG_PC], 2) + "%"
    with coluna:
        st.markdown(
            f"""
<div class="{classe}" style="--stripe:{cor}">
    <div class="nome">{linha['Produto']}</div>
    <div class="digits">R$ {num_br(linha[COL_MARG_RS])}<small>/L</small></div>
    <div class="pct">{pct} sobre a venda</div>
    <div class="rodape">
        <span>Custo R$ {num_br(linha[COL_CUSTO])}</span>
        <span>Venda R$ {num_br(linha[COL_VENDA])}</span>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Resumo
# ──────────────────────────────────────────────────────────────────────────────
media_simples = df[COL_MARG_RS].mean()
melhor = df.loc[df[COL_MARG_RS].idxmax()]
pior = df.loc[df[COL_MARG_RS].idxmin()]

itens = [
    ("Margem média (R$/L)", f"R$ {num_br(media_simples)}"),
    ("Maior margem", f"{melhor['Produto']} · R$ {num_br(melhor[COL_MARG_RS])}"),
    ("Menor margem", f"{pior['Produto']} · R$ {num_br(pior[COL_MARG_RS])}"),
]

if usar_volume and df[COL_VOLUME].sum() > 0:
    total_litros = df[COL_VOLUME].sum()
    total_lucro = df[COL_LUCRO].sum()
    margem_ponderada = total_lucro / total_litros
    itens += [
        ("Volume total", f"{num_br(total_litros, 0)} L"),
        ("Margem bruta do mês", f"R$ {num_br(total_lucro, 2)}"),
        ("Margem ponderada", f"R$ {num_br(margem_ponderada)}/L"),
    ]

html_itens = "".join(
    f'<div class="item"><div class="rot">{rot}</div><div class="val">{val}</div></div>'
    for rot, val in itens
)
st.markdown(f'<div class="faixa">{html_itens}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Gráficos
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="secao">Leitura visual</div>', unsafe_allow_html=True)

escala = alt.Scale(domain=PRODUTOS, range=[CORES[p] for p in PRODUTOS])
g1, g2 = st.columns(2, gap="large")

with g1:
    st.caption("Margem bruta por litro (R$)")
    barras = (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=4, size=34)
        .encode(
            y=alt.Y("Produto:N", sort=PRODUTOS, title=None),
            x=alt.X(f"{COL_MARG_RS}:Q", title="R$ por litro"),
            color=alt.Color("Produto:N", scale=escala, legend=None),
            tooltip=[
                alt.Tooltip("Produto:N"),
                alt.Tooltip(f"{COL_MARG_RS}:Q", format=".4f", title="Margem R$/L"),
                alt.Tooltip(f"{COL_MARG_PC}:Q", format=".2f", title="Margem %"),
            ],
        )
        .properties(height=210)
    )
    rotulos = barras.mark_text(
        align="left", dx=6, fontSize=12, fontWeight="bold", color="#111820"
    ).encode(text=alt.Text(f"{COL_MARG_RS}:Q", format=".4f"), color=alt.value("#111820"))
    st.altair_chart(barras + rotulos, **LARGURA_TOTAL)

with g2:
    st.caption("Composição do preço de venda (R$/L)")
    composicao = df.melt(
        id_vars="Produto",
        value_vars=[COL_COMPRA, COL_FRETE, COL_MARG_RS],
        var_name="Componente",
        value_name="Valor",
    )
    empilhado = (
        alt.Chart(composicao)
        .mark_bar(size=34)
        .encode(
            y=alt.Y("Produto:N", sort=PRODUTOS, title=None),
            x=alt.X("Valor:Q", title="R$ por litro", stack="zero"),
            color=alt.Color(
                "Componente:N",
                scale=alt.Scale(
                    domain=[COL_COMPRA, COL_FRETE, COL_MARG_RS],
                    range=["#19212C", "#7A8798", "#33A06B"],
                ),
                legend=alt.Legend(orient="bottom", title=None, columns=1),
            ),
            tooltip=[
                alt.Tooltip("Produto:N"),
                alt.Tooltip("Componente:N"),
                alt.Tooltip("Valor:Q", format=".4f"),
            ],
        )
        .properties(height=210)
    )
    st.altair_chart(empilhado, **LARGURA_TOTAL)


# ──────────────────────────────────────────────────────────────────────────────
# Exportação e notas
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="secao">Exportar e conferir</div>', unsafe_allow_html=True)

saida = df[colunas_visiveis].copy()
buffer = io.StringIO()
saida.to_csv(buffer, index=False, sep=";", decimal=",", float_format="%.4f")

e1, e2 = st.columns([1, 2])
with e1:
    st.download_button(
        "Baixar apuração (CSV)",
        data=buffer.getvalue().encode("utf-8-sig"),
        file_name="margem_bruta_combustiveis.csv",
        mime="text/csv",
        **LARGURA_TOTAL,
    )
with e2:
    st.caption("Arquivo com separador ponto e vírgula e decimal por vírgula, pronto para abrir no Excel.")

with st.expander("Notas de cálculo"):
    st.markdown(
        f"""
- **Custo de compra** = preço de compra + frete.
- **Margem bruta (R$/L)** = preço de venda − custo de compra.
- **Margem bruta (%)** = margem em R$ ÷ **preço de venda** — é a margem sobre a
  receita, e não o *markup* sobre o custo. Uma margem de R$ 0,2700 sobre venda de
  R$ 6,2900 equivale a 4,29% sobre a venda e 4,48% sobre o custo.
- O frete inicia em **R$ {num_br(FRETE_PADRAO)} por litro** e pode ser alterado
  por produto na tabela ou de uma vez pela barra lateral.
- Os preços de combustível já chegam com ICMS-ST e PIS/COFINS monofásicos
  retidos na origem, então esta apuração trata a margem **comercial** sobre o
  custo de aquisição. Despesas operacionais, quebras, perdas por evaporação e
  taxas de cartão não estão contempladas.
"""
    )
