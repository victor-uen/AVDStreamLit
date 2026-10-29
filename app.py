import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Chess Game Dataset (Lichess) — Correlação e Distribuição",
    layout="wide",
)

st.title("Chess Game Dataset (Lichess) — Correlação e Distribuição")

df = load_data()

# Variáveis quantitativas do estudo (mesma lista VARS_QUANT do notebook de EDA)
VARS_QUANT = ["turns", "white_rating", "black_rating", "opening_ply"]

# Sidebar: filtros (variáveis + intervalo)
with st.sidebar:
    st.header("Filtros")

    variaveis = st.multiselect(
        "Variáveis Quantitativas",
        options=VARS_QUANT,
        default=VARS_QUANT,
        help="Selecione as variáveis quantitativas que deseja analisar no dashboard.",
    )

    separar_por_resultado = st.toggle(
        "Distinguir por Resultado",
        value=False,
        help="Colore a distribuição pelo resultado (brancas_venceram: Brancas venceram ou Outro resultado).",
    )

    # Um slider de intervalo para cada variável selecionada
    intervalos = {}
    for var in variaveis:
        if pd.api.types.is_integer_dtype(df[var]):
            minimo, maximo, passo = int(df[var].min()), int(df[var].max()), 1
        else:
            minimo, maximo, passo = float(df[var].min()), float(df[var].max()), 0.1
        intervalos[var] = st.slider(
            f"Intervalo de {var}",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=passo,
            key=f"intervalo_{var}",
        )

# Mantém só as partidas dentro de todos os intervalos escolhidos
df_filtrado = df
for var, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[df_filtrado[var].between(inicio, fim)]

st.caption(f"{len(df_filtrado)} de {len(df)} partidas dentro dos intervalos escolhidos.")

# Dashboard 1 (conforme rascunho): sidebar de filtros | heatmap de correlação | histograma de distribuição
col_correlacao, col_distribuicao = st.columns([1, 1.25])

with col_correlacao:
    st.subheader("Correlação (Heatmap)")

    if len(variaveis) < 2:
        st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
    else:
        # TODO: Aula 22 - montar o heatmap de correlação de Spearman com Altair
        # (ver app.py de referência da professora e ALTAIR-CROSSFILTER.md para o padrão esperado)
        st.info("Heatmap de correlação entra na Aula 22 — por enquanto, placeholder.")
        st.dataframe(df_filtrado[variaveis].corr(method="spearman"))

with col_distribuicao:
    st.subheader("Distribuição (Histograma)")

    if not variaveis:
        st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
    elif df_filtrado.empty:
        st.warning("Nenhuma partida dentro dos intervalos escolhidos.")
    else:
        # TODO: Aula 22 - trocar por histogramas de verdade em Altair (um por variável,
        # em grade de 2 colunas), coloridos por brancas_venceram quando separar_por_resultado
        # estiver ativo — ver ALTAIR-CROSSFILTER.md para a reatividade entre gráficos.
        st.info("Histogramas de distribuição entram na Aula 22 — por enquanto, placeholder.")
        for var in variaveis:
            st.caption(f"{var}")
            contagem = df_filtrado[var].value_counts(bins=10).sort_index()
            contagem.index = contagem.index.astype(str)  # rótulos em texto para o placeholder
            st.bar_chart(contagem)

# TODO: Aula 22 - Dashboard 2 (KPIs)
