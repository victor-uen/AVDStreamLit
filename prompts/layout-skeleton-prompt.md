# Template: rascunho de layout → esqueleto do app

Preencha cada bloco e envie à ferramenta de IA.

## Contexto

Sou um aluno de Ciência da Computação montando um dashboard baseado no dataset que encontrei no kaggle.com. O link para o dataset é: https://www.kaggle.com/datasets/datasnaek/chess .O Objetivo do Dashboard é: Mostrar a correlação e distribuição das variáveis quantitativas dos resultados das partidas.

## Entrada
C:\Users\victo\OneDrive\Área de Trabalho\cc\Per_5\AVD\StreamlitVictorUen\AVD-20262-pratica-streamlit\entregas\DashBoard1.png

Colunas relevantes do dataset:
- Quantitativas: `turns` (lances), `white_rating`, `black_rating`, `opening_ply` (profundidade de abertura)
- Qualitativas: `rated`, `victory_status`, `opening_eco`, `faixa_rating`
- Alvo: `brancas_venceram` ("Brancas venceram" / "Outro resultado")

Perguntas que o dashboard deve responder:
- Como as variáveis quantitativas das partidas se correlacionam entre si (ex.: `white_rating` x `black_rating`)?
- Qual a distribuição de cada variável, e ela muda entre "Brancas venceram" e "Outro resultado"?
- Como essas distribuições mudam quando eu filtro por um intervalo de valores (ex.: só partidas com `turns` entre X e Y)?   

## Restrições

- Streamlit; Altair preferido para os gráficos (Seaborn permitido), mas **nesta etapa (Aula 21) não implemente os gráficos ainda** — só o esqueleto com os widgets.
- Carregar dados só via `src/data_loader.py` (`load_data()`, já com `@st.cache_data`), sem mexer nesse arquivo.
- Editar apenas `app.py`.
- Pelo menos 1 seletor de variáveis (multiselect) e 1 slider de intervalo, funcionando.
- Sem caminho absoluto para o CSV.

## Formato de saída

Código completo do `app.py` (não só comentários), comentado em português, com `# TODO: Aula 22` nos lugares onde os gráficos de correlação e distribuição vão entrar.