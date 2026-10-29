import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Chess Game Dataset (Lichess)",
    layout="wide",
)

st.title("Chess Game Dataset (Lichess)")

df = load_data()

# Variáveis quantitativas do estudo (mesma lista VARS_QUANT do notebook de EDA)
VARS_QUANT = ["turns", "white_rating", "black_rating", "opening_ply"]

# Sidebar: filtros do Dashboard 1 (variáveis + intervalo)
with st.sidebar:
    st.header("Filtros")
    st.caption("Controlam a aba Correlação e Distribuição.")

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


# Dashboard 1 (conforme rascunho): sidebar de filtros | heatmap de correlação | histograma de distribuição
COR_DESTAQUE = "#c1121f"  # mesmo vermelho do primaryColor em .streamlit/config.toml
CORES_RESULTADO = {"Brancas venceram": COR_DESTAQUE, "Outro resultado": "#6c757d"}


@st.cache_data
def calcular_correlacao(dados, colunas):
    """Matriz de Spearman em formato longo (var_x, var_y, rho), pronta para o Altair."""
    matriz = dados[colunas].corr(method="spearman")
    longa = matriz.reset_index(names="var_x").melt(id_vars="var_x", var_name="var_y", value_name="rho")
    return longa


@st.cache_data
def calcular_histograma(dados, coluna, separar, n_bins=30):
    """Pré-calcula as faixas do histograma no pandas (o Altair só desenha as barras)."""
    valores = dados[coluna]
    bordas = np.histogram_bin_edges(valores, bins=n_bins)
    grupos = dados.groupby("brancas_venceram") if separar else [("Todas as partidas", dados)]
    partes = []
    for nome, grupo in grupos:
        contagem, _ = np.histogram(grupo[coluna], bins=bordas)
        partes.append(
            pd.DataFrame(
                {"inicio": bordas[:-1], "fim": bordas[1:], "partidas": contagem, "resultado": nome}
            )
        )
    return pd.concat(partes, ignore_index=True)


def grafico_heatmap(corr_longa, colunas):
    base = alt.Chart(corr_longa).encode(
        x=alt.X("var_x:N", sort=colunas, title=None, axis=alt.Axis(labelAngle=-30)),
        y=alt.Y("var_y:N", sort=colunas, title=None),
    )
    celulas = base.mark_rect().encode(
        color=alt.Color(
            "rho:Q",
            scale=alt.Scale(scheme="redblue", domain=[-1, 1], reverse=True),
            legend=alt.Legend(title="ρ de Spearman"),
        ),
        tooltip=[
            alt.Tooltip("var_x:N", title="Variável X"),
            alt.Tooltip("var_y:N", title="Variável Y"),
            alt.Tooltip("rho:Q", title="ρ", format=".2f"),
        ],
    )
    rotulos = base.mark_text(fontSize=13).encode(
        text=alt.Text("rho:Q", format=".2f"),
        color=alt.condition("abs(datum.rho) > 0.5", alt.value("white"), alt.value("black")),
    )
    return (celulas + rotulos).properties(height=380)


def grafico_histograma(hist, coluna, separar):
    if separar:
        cor = alt.Color(
            "resultado:N",
            scale=alt.Scale(domain=list(CORES_RESULTADO), range=list(CORES_RESULTADO.values())),
            legend=alt.Legend(title="Resultado", orient="bottom"),
        )
    else:
        cor = alt.value(COR_DESTAQUE)
    return (
        alt.Chart(hist)
        .mark_bar(opacity=0.75 if separar else 0.9, binSpacing=0)
        .encode(
            x=alt.X("inicio:Q", bin="binned", title=coluna),
            x2="fim:Q",
            y=alt.Y("partidas:Q", title="Partidas", stack=None),
            color=cor,
            tooltip=[
                alt.Tooltip("inicio:Q", title="De", format=".0f"),
                alt.Tooltip("fim:Q", title="Até", format=".0f"),
                alt.Tooltip("partidas:Q", title="Partidas"),
                alt.Tooltip("resultado:N", title="Resultado"),
            ],
        )
        .properties(title=coluna, height=200)
    )


aba_dashboard1, aba_dashboard2 = st.tabs(["Correlação e Distribuição", "KPIs das Partidas"])

# Dashboard 1 (conforme rascunho): heatmap de correlação | histograma de distribuição
with aba_dashboard1:
    st.caption(f"{len(df_filtrado)} de {len(df)} partidas dentro dos intervalos escolhidos.")

    col_correlacao, col_distribuicao = st.columns([1, 1.25])

    with col_correlacao:
        st.subheader("Correlação (Heatmap)")

        if len(variaveis) < 2:
            st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
        elif len(df_filtrado) < 2:
            st.warning("Partidas insuficientes nos intervalos escolhidos para calcular a correlação.")
        else:
            corr_longa = calcular_correlacao(df_filtrado, variaveis)
            st.altair_chart(grafico_heatmap(corr_longa, variaveis), width="stretch")
            st.caption("Correlação de Spearman (por postos), robusta às caudas longas de turns e opening_ply.")

    with col_distribuicao:
        st.subheader("Distribuição (Histograma)")

        if not variaveis:
            st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
        elif df_filtrado.empty:
            st.warning("Nenhuma partida dentro dos intervalos escolhidos.")
        else:
            # Grade de 2 colunas: um histograma por variável selecionada
            grade = st.columns(2)
            for i, var in enumerate(variaveis):
                hist = calcular_histograma(df_filtrado, var, separar_por_resultado)
                with grade[i % 2]:
                    st.altair_chart(grafico_histograma(hist, var, separar_por_resultado), width="stretch")

# Dashboard 2 (conforme rascunho): widgets -> métricas (st.metric) -> visuais em Altair
with aba_dashboard2:
    # TODO: Aula 22 - widgets do Dashboard 2 (faixa de rating, tipo de partida, abertura)
    # TODO: Aula 22 - 4 st.metric: partidas, % vitória das brancas, duração mediana, % xeque-mate
    # TODO: Aula 22 - visuais em Altair com crossfilter (ver ALTAIR-CROSSFILTER.md)
    st.info("Dashboard 2 em construção.")