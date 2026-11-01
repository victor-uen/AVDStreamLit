# Justificativa das métricas — Dashboard 2

A pergunta que eu quis responder com o Dashboard 2 foi: **o que aumenta a chance de as brancas vencerem uma partida online no Lichess?**

Pensei o dashboard para jogadores amadores e intermediários de xadrez online, e também para quem treina esses jogadores. Escolhi quatro métricas tentando cobrir os tipos que vimos na aula de Métricas Básicas: uma de volume (contagem), duas de proporção (taxas) e uma de tendência central (mediana). Todas mudam conforme os filtros de faixa de rating e tipo de partida, e também quando clico numa abertura no gráfico de barras.

## Métrica 1: <Partidas analisadas>
- **Variável:** contagem de partidas do dataset filtrado (`id`)
- **O que mede:** quantas partidas entram no cálculo com os filtros e a seleção atuais.
- **Por que foi escolhida:** coloquei essa métrica primeiro porque ela dá contexto para as outras. Uma taxa de vitória de 60% em 40 partidas não quer dizer muita coisa, mas em 4.000 partidas já é um resultado bem mais confiável. Sem ela, quem olha o dashboard não sabe se pode confiar nos outros números.
- **Público-alvo:** jogadores e treinadores que vão usar o dashboard para comparar cenários.
- **Qual decisão pode ser apoiada por essa métrica?** Saber se um recorte tem dados suficientes para tirar alguma conclusão. Por exemplo, uma abertura pouco jogada em partidas casuais pode ter tão poucas partidas que não vale a pena basear o estudo nela.
- **O que comunica ao público-alvo:** mostra o tamanho da amostra por trás dos números. Com todos os filtros são 19.629 partidas. Quando selecionei a English Opening, caiu para 715.

## Métrica 2: <Vitória das brancas (%)>
- **Variável:** `brancas_venceram` (proporção de "Brancas venceram"), com o delta em pontos percentuais em relação ao dataset inteiro
- **O que mede:** a porcentagem de partidas que as brancas venceram no recorte selecionado.
- **Por que foi escolhida:** é a métrica que responde diretamente a minha pergunta. Coloquei o delta em relação à média geral (49,9%) para dar para ver na hora se o cenário favorece ou atrapalha as brancas, sem precisar ficar lembrando qual é a média.
- **Público-alvo:** jogadores que querem escolher aberturas e entender em que situações jogar de brancas é mais vantajoso.
- **Qual decisão pode ser apoiada por essa métrica?** Escolher quais aberturas estudar e usar de brancas, comparando a taxa de cada uma com a média.
- **O que comunica ao público-alvo:** se, naquele cenário, as brancas ganham mais ou menos do que o normal. Uma coisa que me chamou atenção: quando o jogador de brancas tem rating abaixo de 1200, as brancas vencem só 34,4% das partidas. Com rating de 1800 ou mais, vencem 56,3%. Ou seja, a vantagem de começar jogando só aparece de verdade nos níveis mais altos.

## Métrica 3: <Duração mediana (lances)>
- **Variável:** `turns`
- **O que mede:** quantos lances tem uma partida típica no recorte selecionado.
- **Por que foi escolhida:** queria mostrar o ritmo das partidas. Usei a **mediana** em vez da média porque, no histograma do Dashboard 1, deu para ver que `turns` tem uma cauda bem longa (chega a 349 lances). A média acabaria puxada para cima por poucas partidas muito longas.
- **Público-alvo:** jogadores que querem entender como são as partidas no nível deles, e treinadores planejando o que treinar.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir onde focar o estudo. Se as partidas são curtas, elas costumam ser decididas cedo, então vale mais estudar abertura e tática. Se são longas, meio-jogo e final pesam mais.
- **O que comunica ao público-alvo:** quanto dura uma partida normal naquele cenário. A mediana vai de 48 lances (brancas abaixo de 1200) para 60 lances (brancas com 1800 ou mais), o que mostra que as partidas ficam mais disputadas conforme o nível sobe.

## Métrica 4: <Partidas que terminam em xeque-mate (%)>
- **Variável:** `victory_status` (proporção de "mate")
- **O que mede:** a porcentagem de partidas que terminam em xeque-mate, e não por desistência, tempo esgotado ou empate.
- **Por que foi escolhida:** a taxa de vitória mostra quem ganha, mas não mostra **como** a partida termina, e essa métrica completa isso. No dataset inteiro, 31,5% das partidas acabam em mate e 55,7% em desistência. O gráfico "Como as partidas terminam" mostra esse detalhe por faixa de rating.
- **Público-alvo:** jogadores que estão evoluindo e treinadores.
- **Qual decisão pode ser apoiada por essa métrica?** Entender o nível de maturidade dos jogadores e o que treinar. Muito xeque-mate indica erros graves que passam despercebidos, então faz sentido priorizar tática e defesa. Pouco mate indica que os jogadores percebem quando a posição está perdida e desistem antes.
- **O que comunica ao público-alvo:** se, naquele nível, as partidas vão até o fim ou se quem está perdendo desiste antes. A taxa cai de 42,5% (brancas abaixo de 1200) para 21,2% (brancas com 1800 ou mais).

## Observação sobre os filtros
Conferindo o dataset, percebi que a coluna `faixa_rating` foi criada a partir do rating de quem joga de **brancas** (`white_rating`). Então, no Dashboard 2, o filtro de faixa de rating se refere ao nível do jogador de brancas.