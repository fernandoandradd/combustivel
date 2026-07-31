# -*- coding: utf-8 -*-
"""
Margem Bruta de Combustíveis — versão para celular
Gasolina Comum · Diesel S10 · Diesel S500

Execução:
    pip install streamlit
    streamlit run margem_combustiveis.py
"""

import streamlit as st

st.set_page_config(
    page_title="Margem de Combustíveis",
    page_icon="⛽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

FRETE_PADRAO = 0.17
IRPJ_PADRAO = 0.24   # % sobre a receita bruta
CSLL_PADRAO = 1.20   # % sobre a receita bruta

PRODUTOS = [
    ("Gasolina Comum", "#E8A317", 5.8500, 6.2900),
    ("Diesel S10", "#2F9E68", 5.9500, 6.4900),
    ("Diesel S500", "#7B8794", 5.8000, 6.3500),
]

st.markdown(
    """
<style>
.block-container { padding: 1.4rem .9rem 3rem .9rem; max-width: 560px; }
#MainMenu, footer, header { visibility: hidden; }

h1.topo {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -.01em;
    margin: 0 0 1.1rem 0;
    color: #11181F;
}

.rotulo {
    font-size: 1rem;
    font-weight: 700;
    color: #11181F;
    border-left: 5px solid var(--cor);
    padding-left: 10px;
    margin: 0 0 .7rem 0;
}
.rotulo.cinza { border-left-color: #C3CBD4; font-weight: 600; color: #46525F; }

.painel {
    background: #11181F;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: .4rem;
}
.linha {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
}
.linha + .linha {
    border-top: 1px solid #2B3644;
    margin-top: 10px;
    padding-top: 10px;
}
.bloco { display: flex; flex-direction: column; min-width: 0; }
.rot {
    font-size: .64rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #8A99AB;
    font-weight: 600;
    white-space: nowrap;
}
.val {
    font-size: .98rem;
    font-weight: 700;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
}
.val.bruta { color: var(--cor); }
.val.liquido { font-size: 1.32rem; color: var(--cor); }
.val.imposto { color: #B9C4D0; font-weight: 600; }
.painel.negativa .val.bruta, .painel.negativa .val.liquido { color: #FF6B5A; }

div[data-testid="stNumberInput"] input { font-size: 1rem; padding: .5rem .6rem; }
div[data-testid="stNumberInput"] label { font-size: .78rem; color: #5A6672; }
</style>
""",
    unsafe_allow_html=True,
)


def num_br(valor, casas=4):
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".")


st.markdown('<h1 class="topo">Margem de combustíveis</h1>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown(
        '<div class="rotulo cinza">Impostos sobre a receita</div>',
        unsafe_allow_html=True,
    )
    t1, t2 = st.columns(2)
    irpj_pct = t1.number_input(
        "IRPJ (%)", min_value=0.0, value=IRPJ_PADRAO, step=0.01,
        format="%.2f", key="irpj_pct",
    )
    csll_pct = t2.number_input(
        "CSLL (%)", min_value=0.0, value=CSLL_PADRAO, step=0.01,
        format="%.2f", key="csll_pct",
    )

for nome, cor, compra_ini, venda_ini in PRODUTOS:
    chave = nome.lower().replace(" ", "_")
    with st.container(border=True):
        st.markdown(
            f'<div class="rotulo" style="--cor:{cor}">{nome}</div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        compra = c1.number_input(
            "Compra (R$/L)", min_value=0.0, value=compra_ini,
            step=0.01, format="%.4f", key=f"compra_{chave}",
        )
        frete = c2.number_input(
            "Frete (R$/L)", min_value=0.0, value=FRETE_PADRAO,
            step=0.01, format="%.4f", key=f"frete_{chave}",
        )
        venda = st.number_input(
            "Venda (R$/L)", min_value=0.0, value=venda_ini,
            step=0.01, format="%.4f", key=f"venda_{chave}",
        )

        custo = compra + frete
        margem = venda - custo
        pct = (margem / venda * 100) if venda else 0.0
        irpj = venda * irpj_pct / 100
        csll = venda * csll_pct / 100
        liquido = margem - irpj - csll
        classe = "painel negativa" if liquido < 0 else "painel"

        st.markdown(
            f"""
<div class="{classe}" style="--cor:{cor}">
    <div class="linha">
        <div class="bloco"><span class="rot">Custo</span>
            <span class="val">R$ {num_br(custo)}</span></div>
        <div class="bloco"><span class="rot">Margem bruta</span>
            <span class="val bruta">R$ {num_br(margem)}</span></div>
        <div class="bloco"><span class="rot">Margem %</span>
            <span class="val bruta">{num_br(pct, 2)}%</span></div>
    </div>
    <div class="linha">
        <div class="bloco"><span class="rot">IRPJ</span>
            <span class="val imposto">R$ {num_br(irpj)}</span></div>
        <div class="bloco"><span class="rot">CSLL</span>
            <span class="val imposto">R$ {num_br(csll)}</span></div>
        <div class="bloco"><span class="rot">Lucro líquido</span>
            <span class="val liquido">R$ {num_br(liquido)}</span></div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
