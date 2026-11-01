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
FAIXAS_RATING = ["<1200", "1200-1499", "1500-1799", "1800+"]
ORDEM_DESFECHO = ["mate", "resign", "outoftime", "draw"]
NOMES_DESFECHO = {"mate": "Xeque-mate", "resign": "Desistência", "outoftime": "Tempo esgotado", "draw": "Empate"}
CORES_DESFECHO = [COR_DESTAQUE, "#6c757d", "#adb5bd", "#dee2e6"]


@st.cache_data
def preparar_kpis(dados):
    """Colunas derivadas do Dashboard 2: família da abertura, vantagem de rating e desfecho legível."""
    base = dados.copy()
    base["familia_abertura"] = (
        base["opening_name"].str.split(":").str[0].str.split("|").str[0]
        .str.replace(r"\s*#\d+$", "", regex=True).str.strip()
    )
    base["vantagem_rating"] = base["white_rating"] - base["black_rating"]
    base["vitoria_brancas"] = (base["brancas_venceram"] == "Brancas venceram").astype(int)
    base["desfecho"] = base["victory_status"].map(NOMES_DESFECHO)
    base["ordem_desfecho"] = base["victory_status"].map({d: i for i, d in enumerate(ORDEM_DESFECHO)})
    return base


@st.cache_data
def vitoria_por_abertura(dados, top_n):
    """Taxa de vitória das brancas nas top_n aberturas mais jogadas."""
    tabela = (
        dados.groupby("familia_abertura")
        .agg(partidas=("vitoria_brancas", "size"), taxa_vitoria=("vitoria_brancas", "mean"))
        .reset_index()
        .nlargest(top_n, "partidas")
    )
    return tabela


@st.cache_data
def vitoria_por_vantagem(dados, passo=100, limite=400, minimo_partidas=30):
    """Taxa de vitória das brancas por faixa de vantagem de rating (-400 a +400)."""
    recorte = dados[dados["vantagem_rating"].between(-limite, limite)].copy()
    recorte["faixa"] = (recorte["vantagem_rating"] // passo) * passo + passo / 2  # centro da faixa
    tabela = (
        recorte.groupby("faixa")
        .agg(partidas=("vitoria_brancas", "size"), taxa_vitoria=("vitoria_brancas", "mean"))
        .reset_index()
    )
    return tabela[tabela["partidas"] >= minimo_partidas]


def grafico_aberturas(tabela, selecao, media_geral):
    barras = (
        alt.Chart(tabela)
        .mark_bar()
        .encode(
            x=alt.X("taxa_vitoria:Q", title="Vitória das brancas", axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("familia_abertura:N", sort="-x", title=None),
            color=alt.value(COR_DESTAQUE),
            opacity=alt.condition(selecao, alt.value(1), alt.value(0.3)),
            tooltip=[
                alt.Tooltip("familia_abertura:N", title="Abertura"),
                alt.Tooltip("taxa_vitoria:Q", title="Vitória das brancas", format=".1%"),
                alt.Tooltip("partidas:Q", title="Partidas"),
            ],
        )
        .add_params(selecao)
    )
    referencia = (
        alt.Chart(pd.DataFrame({"media": [media_geral]}))
        .mark_rule(strokeDash=[4, 4], color="#6c757d")
        .encode(x="media:Q", tooltip=[alt.Tooltip("media:Q", title="Média do filtro", format=".1%")])
    )
    return (barras + referencia).properties(height=360)


def grafico_desfechos(dados):
    return (
        alt.Chart(dados)
        .mark_bar()
        .encode(
            x=alt.X("faixa_rating:N", sort=FAIXAS_RATING, title="Faixa de rating",
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y("count():Q", stack="normalize", title="Partidas", axis=alt.Axis(format="%")),
            color=alt.Color(
                "desfecho:N",
                scale=alt.Scale(domain=[NOMES_DESFECHO[d] for d in ORDEM_DESFECHO], range=CORES_DESFECHO),
                legend=alt.Legend(title="Desfecho", orient="bottom"),
            ),
            order=alt.Order("ordem_desfecho:Q", sort="ascending"),
            tooltip=[
                alt.Tooltip("faixa_rating:N", title="Faixa"),
                alt.Tooltip("desfecho:N", title="Desfecho"),
                alt.Tooltip("count():Q", title="Partidas"),
            ],
        )
        .properties(height=360)
    )


def grafico_vantagem(tabela):
    base = alt.Chart(tabela).encode(
        x=alt.X("faixa:Q", title="Vantagem de rating das brancas (brancas − pretas)",
                scale=alt.Scale(domain=[-400, 400])),
        y=alt.Y("taxa_vitoria:Q", title="Vitória das brancas", axis=alt.Axis(format="%"),
                scale=alt.Scale(domain=[0, 1])),
        tooltip=[
            alt.Tooltip("faixa:Q", title="Centro da faixa"),
            alt.Tooltip("taxa_vitoria:Q", title="Vitória das brancas", format=".1%"),
            alt.Tooltip("partidas:Q", title="Partidas"),
        ],
    )
    linha = base.mark_line(color=COR_DESTAQUE, point=alt.OverlayMarkDef(color=COR_DESTAQUE, size=60))
    meio = alt.Chart(pd.DataFrame({"y": [0.5]})).mark_rule(strokeDash=[4, 4], color="#6c757d").encode(y="y:Q")
    return (meio + linha).properties(height=280)


with aba_dashboard2:
    df_kpis = preparar_kpis(df)

    # 1) Widgets: controlam só esta aba
    w1, w2, w3 = st.columns([2, 1.2, 1])
    with w1:
        faixas = st.multiselect("Faixa de rating", FAIXAS_RATING, default=FAIXAS_RATING, key="d2_faixas")
    with w2:
        tipo = st.radio("Tipo de partida", ["Todas", "Ranqueadas", "Casuais"], horizontal=True, key="d2_tipo")
    with w3:
        top_n = st.slider("Aberturas no ranking", min_value=5, max_value=15, value=10, key="d2_top_n")

    df_d2 = df_kpis[df_kpis["faixa_rating"].isin(faixas)]
    if tipo == "Ranqueadas":
        df_d2 = df_d2[df_d2["rated"]]
    elif tipo == "Casuais":
        df_d2 = df_d2[~df_d2["rated"]]

    if df_d2.empty:
        st.warning("Nenhuma partida com os filtros escolhidos. Selecione pelo menos uma faixa de rating.")
    else:
        # O gráfico de aberturas é desenhado antes das métricas para que o clique nele
        # (on_select) já filtre as métricas e os outros gráficos no mesmo rerun.
        clique = alt.selection_point(name="abertura", fields=["familia_abertura"])
        tabela_aberturas = vitoria_por_abertura(df_d2, top_n)

        area_metricas = st.container()
        col_aberturas, col_desfechos = st.columns(2)

        with col_aberturas:
            st.subheader("Vitória das brancas por abertura")
            evento = st.altair_chart(
                grafico_aberturas(tabela_aberturas, clique, df_d2["vitoria_brancas"].mean()),
                key="grafico_aberturas",
                on_select="rerun",
                width="stretch",
            )
            st.caption("Clique numa barra para filtrar o painel (shift + clique seleciona várias). "
                       "Linha tracejada: média com os filtros atuais.")

        # Seleção do gráfico -> Python (exemplo 3 do ALTAIR-CROSSFILTER.md)
        aberturas = [item["familia_abertura"] for item in evento.selection.get("abertura", [])]
        selecionado = df_d2[df_d2["familia_abertura"].isin(aberturas)] if aberturas else df_d2

        # 2) Métricas
        with area_metricas:
            if aberturas:
                st.caption(f"Filtrando pela abertura: {', '.join(aberturas)}")
            taxa_geral = df_kpis["vitoria_brancas"].mean()
            taxa_sel = selecionado["vitoria_brancas"].mean()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Partidas analisadas", f"{len(selecionado):,}".replace(",", "."),
                      border=True)
            m2.metric("Vitória das brancas", f"{taxa_sel:.1%}",
                      delta=f"{(taxa_sel - taxa_geral) * 100:+.1f} p.p. vs. dataset", border=True)
            m3.metric("Duração mediana", f"{selecionado['turns'].median():.0f} lances", border=True)
            m4.metric("Terminam em xeque-mate", f"{(selecionado['victory_status'] == 'mate').mean():.1%}",
                      border=True)

        # 3) Visuais ligados à seleção
        with col_desfechos:
            st.subheader("Como as partidas terminam")
            st.altair_chart(grafico_desfechos(selecionado), width="stretch")

        st.subheader("Vitória das brancas × vantagem de rating")
        tabela_vantagem = vitoria_por_vantagem(selecionado)
        if tabela_vantagem.empty:
            st.info("Partidas insuficientes para traçar a curva (mínimo de 30 por faixa).")
        else:
            st.altair_chart(grafico_vantagem(tabela_vantagem), width="stretch")
            st.caption("Faixas de 100 pontos de rating; só aparecem faixas com pelo menos 30 partidas. "
                       "Linha tracejada: 50% (equilíbrio).")