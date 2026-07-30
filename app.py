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

.resultado {
    background: #11181F;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: .4rem;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
}
.resultado .bloco { display: flex; flex-direction: column; }
.resultado .rot {
    font-size: .68rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #8A99AB;
    font-weight: 600;
}
.resultado .val {
    font-size: 1.05rem;
    font-weight: 700;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
}
.resultado .destaque { font-size: 1.5rem; color: var(--cor); }
.resultado.negativa .destaque { color: #FF6B5A; }

/* campos maiores para toque */
div[data-testid="stNumberInput"] input { font-size: 1rem; padding: .5rem .6rem; }
div[data-testid="stNumberInput"] label { font-size: .78rem; color: #5A6672; }
</style>
""",
    unsafe_allow_html=True,
)


def num_br(valor, casas=4):
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".")


st.markdown('<h1 class="topo">Margem bruta de combustíveis</h1>', unsafe_allow_html=True)

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
        classe = "resultado negativa" if margem < 0 else "resultado"

        st.markdown(
            f"""
<div class="{classe}" style="--cor:{cor}">
    <div class="bloco">
        <span class="rot">Custo</span>
        <span class="val">R$ {num_br(custo)}</span>
    </div>
    <div class="bloco">
        <span class="rot">Margem R$</span>
        <span class="val destaque">{num_br(margem)}</span>
    </div>
    <div class="bloco">
        <span class="rot">Margem %</span>
        <span class="val destaque">{num_br(pct, 2)}%</span>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
