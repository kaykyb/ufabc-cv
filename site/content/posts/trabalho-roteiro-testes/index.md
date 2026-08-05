---
title: "[5] Trabalho Final - Roteiro de Testes"
authors:
  [
    "Kayky de Brito dos Santos",
    "Andre Marques da Silva",
    "Rafael de Souza Coelho",
  ]
date: 2026-08-05
summary: "Quinta etapa do trabalho final: o roteiro de testes com voluntários, com a lista de tarefas a realizar no sistema de reconhecimento de cédulas, as condições do teste, a ficha de registro dos resultados e as perguntas de feedback pós-teste."
tags: ["trabalho"]
---

**Equipe:** Sem Título

**Integrantes:**

- Kayky de Brito dos Santos
- André Marques da Silva
- Rafael de Souza Coelho

**Data de publicação:** 5 de agosto de 2026

**Título do trabalho:** Programa de Reconhecimento de Valores de Cédulas

## 1. Introdução

Esta é a quinta etapa do trabalho final: o **roteiro de testes com voluntários**. A [modelagem funcional]({{< ref "trabalho-modelagem-funcional" >}}) previu, como parte da avaliação, um teste com pessoas reais seguindo um roteiro de tarefas; este documento é esse roteiro. Ele será aplicado sobre a [maquete e o software da etapa 4]({{< ref "trabalho-maquete" >}}), com o sistema **já configurado e em execução pela equipe** antes da chegada do voluntário: maquete montada, câmera posicionada, modelo carregado e detecção ao vivo rodando. O voluntário não instala nem configura nada; seu papel é usar o sistema como um cliente ou comerciante usaria no balcão.

## 2. Objetivo do Teste

Verificar, com pessoas de fora da equipe, três coisas que os testes internos não conseguem responder sozinhos:

1. **Robustez de reconhecimento:** o sistema acerta a denominação quando quem apresenta a nota não conhece os "jeitos" que a equipe aprendeu durante o desenvolvimento?
2. **Naturalidade da interação:** a instrução "coloque a nota na área central da bancada" é suficiente, sem treinamento prévio?
3. **Confiança no resultado:** o voluntário confiaria no sistema para conferir dinheiro de verdade?

## 3. Condições do Teste

- **Estado inicial:** sistema rodando (`detectar.py` com o modelo treinado, limiar padrão de 80%), bancada vazia, iluminação fixada pela equipe. O voluntário chega com tudo pronto.
- **Papéis:** um integrante conduz a sessão (dá as instruções e entrega as cédulas), outro registra os resultados na ficha da seção 6. O condutor **não corrige nem ajuda** durante as tarefas, exceto se o voluntário travar por mais de um minuto.
- **Retorno do sistema:** a resposta principal é o **anúncio falado** do valor ("cinquenta reais"), com debounce de 7 segundos para a mesma nota (uma nota diferente é anunciada na hora). Em paralelo, a tela exibe "NOTA X DETECTADA" com a confiança, que o registrador usa para conferência.
- **Cédulas do teste:** um conjunto separado pela equipe com as seis denominações cobertas pelo modelo atual (R$ 2, 5, 10, 20, 50 e 100), incluindo exemplares bem conservados e exemplares desgastados/amassados. A nota de R$ 200 fica fora do teste até entrar no dataset de treino.
- **Registro:** cada sessão é gravada em vídeo (com autorização do voluntário) e anotada na ficha de registro. O vídeo captura a bancada e a tela, não o rosto do voluntário.
- **Duração alvo:** 10 a 15 minutos por voluntário.

## 4. Instruções Dadas ao Voluntário

Antes de começar, o condutor lê a explicação abaixo, e nada além dela (a interação precisa se sustentar sem tutorial):

> "Este sistema reconhece o valor de cédulas de Real. Para usar, coloque uma nota na área central da bancada preta e aguarde a resposta. Vou pedir para você fazer algumas tarefas simples com estas notas. Não existe resposta certa ou errada da sua parte; quem está sendo testado é o sistema, não você."

## 5. Lista de Tarefas

As tarefas são executadas na ordem abaixo. Entre uma tarefa e outra, o condutor retira as cédulas da bancada e aguarda o sistema voltar a indicar bancada vazia.

| # | Tarefa (instrução ao voluntário) | O que verificamos |
| --- | --- | --- |
| T1 | "Antes de qualquer nota: olhe a resposta do sistema com a bancada vazia." | O sistema indica "vazio" e não inventa detecção sem cédula |
| T2 | "Coloque esta nota na bancada, do jeito que achar natural." (nota de R$ 50 bem conservada, entregue com a frente para cima) | Caso base: reconhecimento com apresentação espontânea |
| T3 | "Agora esta." (repetir para R$ 2, 5, 10, 20 e 100, uma por vez, em ordem embaralhada) | Cobertura das seis denominações do modelo |
| T4 | "Coloque esta nota virada, com o outro lado para cima." (duas denominações à escolha do condutor) | Reconhecimento pelo verso |
| T5 | "Coloque esta nota torta, em qualquer ângulo, sem alinhar com nada." | Invariância à rotação |
| T6 | "Esta nota está amassada. Coloque assim mesmo, sem desamassar." (exemplar desgastado/amassado) | Robustez a cédulas em condição real de circulação |
| T7 | "Largue a nota na bancada de qualquer jeito, sem capricho, como se estivesse com pressa." | Apresentação desleixada, prevista desde as entrevistas |
| T8 | "Troque a nota que está na bancada por esta outra, sem esperar." | Transição entre notas: o sistema atualiza a resposta sem confundir os valores |
| T9 | "Coloque este cartão (ou papel) na bancada, no lugar da nota." (objeto claro que não é cédula) | Falso positivo: o sistema não deve anunciar valor para algo que não é nota |
| T10 | "Simule um pagamento: apresente estas três notas, uma de cada vez, e me diga o total usando só a resposta do sistema." (ex.: 50 + 10 + 5) | Tarefa de uso realista: leitura sequencial e soma a partir do que o sistema informa |
| T11 | "Para terminar: use o sistema livremente por um minuto, do jeito que quiser." | Comportamentos espontâneos não previstos pelo roteiro |

Observação sobre a T9: como a localização clássica destaca qualquer objeto claro sobre o fundo preto, esta tarefa testa justamente o corte por confiança da rede. O resultado esperado é a ausência de anúncio de valor (classificação "vazio" ou confiança abaixo do limiar).

## 6. Ficha de Registro

Uma ficha por voluntário. Para cada tarefa, quem registra anota:

| Tarefa | Resposta do sistema | Correta? (sim/não/sem resposta) | Tempo até a resposta | Observações |
| --- | --- | --- | --- | --- |
| T1 | | | | |
| T2 | | | | |
| ... | | | | |

Critérios de preenchimento:

- **Correta:** o sistema anunciou a denominação certa (ou, em T1 e T9, permaneceu sem anunciar valor).
- **Sem resposta:** passados 10 segundos com a nota posicionada, nenhuma detecção acima do limiar. Vale como falha branda: pela decisão de projeto da modelagem, silêncio é preferível a valor errado.
- **Incorreta:** o sistema anunciou uma denominação diferente da apresentada. É a falha grave; registrar qual confusão ocorreu (ex.: 50 anunciado como 100).
- **Tempo até a resposta:** cronometrado do momento em que a nota toca a bancada até o anúncio falado do valor (com a detecção na tela como apoio de conferência).

## 7. Perguntas Pós-Teste

Ao final das tarefas, o condutor faz as perguntas abaixo e registra as respostas literais:

1. De 1 a 5, quão fácil foi usar o sistema sem ninguém explicar os detalhes?
2. De 1 a 5, quanto você confiaria neste sistema para conferir dinheiro no seu dia a dia?
3. Alguma resposta do sistema te surpreendeu ou confundiu? Qual?
4. Se você dependesse só da voz, sem olhar a tela, o sistema funcionaria para você? O que precisaria mudar? (volume, clareza, momento e frequência dos anúncios)
5. O que você mudaria no sistema?

## 8. Consolidação dos Resultados

Com as fichas de todos os voluntários, os resultados alimentam as métricas definidas na modelagem funcional:

- **Taxa de acerto por tarefa e por denominação**, destacando as confusões par a par (quais valores foram trocados por quais).
- **Tempo médio até a resposta**, como aproximação prática da latência percebida.
- **Notas das perguntas 1 e 2** (facilidade e confiança) e a lista qualitativa de dificuldades e sugestões, que orientam os ajustes finais do protótipo.

Os resultados consolidados, junto com a matriz de confusão do modelo e as medições de desempenho, entram no relatório técnico da etapa final.
