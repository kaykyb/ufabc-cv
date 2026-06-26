---
title: "[0] Trabalho Final - Entrevistas Empáticas"
authors:
  [
    "Kayky de Brito dos Santos",
    "Andre Marques da Silva",
    "Rafael de Souza Coelho",
  ]
date: 2026-06-20
summary: "Entrevistas empáticas conduzidas por cada integrante para identificar dores reais que possam ser resolvidas por visão computacional em tempo real."
tags: ["trabalho"]
---

**Autores:**

- Kayky de Brito dos Santos
- André Marques da Silva
- Rafael de Souza Coelho

**Data de publicação:** 20 de junho de 2026

## Introdução

A primeira etapa do trabalho final da disciplina consiste na **fase de empatia**, em que cada integrante entrevista pelo menos duas pessoas externas para identificar uma "dor" que possa ser endereçada por um sistema de visão computacional em tempo real. Este relatório consolida as entrevistas conduzidas pelos integrantes da equipe, mantendo um formato uniforme de apresentação.

As entrevistas a seguir servirão de base para a definição do tema do trabalho, sua justificativa, motivação e os benefícios pretendidos pelo sistema final.

---

## Entrevistas conduzidas por Kayky

### Entrevista 1: Identificação de Cédulas no Comércio

**Entrevistada:** Dona Marlene, 61 anos, dona de uma casa de ração de bairro.

**Kayky:** Dona Marlene, como é a lida aqui com o dinheiro no balcão?

**Marlene:** É puxado. No fim de semana enche, todo mundo querendo o saco de ração.

**Kayky:** E acontece de errar o troco?

**Marlene:** Acontece. Minha vista já não é a mesma, tenho uma catarata num olho.

**Marlene:** Com luz boa eu me viro. No escuro ou com a nota amassada eu me confundo.

**Kayky:** Confunde quais notas?

**Marlene:** A de 50 com a de 100, direto. As novas são muito parecidas.

**Marlene:** Antes o tamanho diferente ajudava, eu reconhecia quase no tato.

**Kayky:** E como a senhora resolve hoje?

**Marlene:** Chamo minha filha ou peço para o cliente confirmar. Fico constrangida.

**Marlene:** Já me passaram nota trocada de propósito, sabendo que eu não enxergo bem.

**Kayky:** E se uma câmera lesse a nota e dissesse o valor para a senhora?

**Marlene:** Ajudaria muito. Mas teria que ser fácil e na hora.

**Marlene:** Estou sempre com a mão ocupada, não dá para ficar mirando e alinhando. Teria que ser só encostar.

**Enquadramento nos Requisitos:** A baixa visão de Marlene (catarata inicial) é o problema: ela não distingue denominações com segurança, sobretudo sob luz ruim ou com cédulas amassadas, ficando exposta a erros de troco e a fraudes. Como ela não consegue enquadrar a nota com precisão, o sistema precisa tolerar imagens tortas e mal alinhadas, o que torna a **calibração** indispensável. A classificação da denominação (R$ 2, 5, 10, 20, 50, 100, 200) será feita por uma **rede neural (CNN)**, treinada com cédulas em condições variadas para a robustez exigida, com saída em **áudio (TTS)** anunciando o valor em voz alta.

### Entrevista 2: A Perspectiva do Auxiliar de Caixa

**Entrevistado:** Kauã, 19 anos, filho da proprietária e auxiliar no caixa.

**Kayky:** Kauã, como você ajuda sua mãe no caixa?

**Kauã:** No fim de semana eu fico na conferência. Ela atende e eu confiro o dinheiro e o troco, por causa da vista dela.

**Kayky:** Se um sistema fizesse esse papel, o que não podia faltar?

**Kauã:** Teria que ser simples e não errar.

**Kauã:** Ela só encosta a nota e ele fala o valor.

**Kauã:** E precisa funcionar com nota velha e desgastada, que é o que mais aparece aqui.

**Enquadramento nos Requisitos:** Kauã representa o auxílio manual hoje existente e reforça dois requisitos centrais. O relato evidencia o caráter ruidoso da entrada esperada, justificando a etapa de **calibração**. A exigência de funcionar com cédulas desgastadas orienta o treinamento da **rede neural**, e o pedido de retorno sonoro fundamenta a adoção da síntese de voz (**TTS**) como saída acessível.

---

## Entrevistas conduzidas por André

### Entrevista 1: Controle de Qualidade em Pequena Escala

**Entrevistado:** Marcos, 45 anos, dono de uma pequena fábrica de peças de alumínio.

**André:** Marcos, obrigado por me receber. Pode me contar um pouco sobre como funciona a inspeção final das peças aqui na fábrica?

**Marcos:** Nós produzimos cerca de 100 peças por dia. Hoje, a inspeção é 100% visual e manual. Um funcionário pega peça por peça para ver se há riscos profundos ou amassados antes de embalar. O problema é o cansaço visual, que faz o funcionário deixar passar defeitos sutis no fim do turno.

**André:** Se fôssemos instalar uma câmera na esteira para automatizar isso, como seria o ambiente físico?

**Marcos:** A câmera precisaria ficar em um suporte bem próximo à esteira, angulada. Nós até tentamos gravar testes com uma webcam comum, mas notamos que a lente distorcia muito as bordas das peças, fazendo-as parecerem curvadas. Isso atrapalharia qualquer medição.

**André:** Entendi. Esse efeito de distorção será resolvido matematicamente no sistema. E, uma vez que a imagem esteja corrigida, o que o sistema deve fazer?

**Marcos:** Ele precisa identificar a peça e disparar um alerta visual na tela sempre que detectar um defeito, para que o operador apenas retire a peça da linha.

**Enquadramento nos Requisitos:** O problema relatado por Marcos justifica perfeitamente a **calibração**. O sistema em Python com OpenCV utilizará imagens de um padrão xadrez (_chessboard_) para extrair os parâmetros intrínsecos e extrínsecos da câmera, corrigindo as distorções radiais e tangenciais causadas pela lente próxima e angulada, além de calcular o erro de reprojeção. A funcionalidade principal será de **Deep Learning (CNNs)**: uma rede convolucional como YOLO ou MobileNet, treinada especificamente para classificar e detectar defeitos (arranhões e amassados) nas peças de alumínio que passam pela webcam.

### Entrevista 2: Auxílio à Mobilidade para Deficientes Visuais

**Entrevistado:** Carlos, 35 anos, instrutor de orientação e mobilidade para pessoas com deficiência visual.

**André:** Carlos, como instrutor de mobilidade, qual é a maior "dor" que seus alunos enfrentam ao caminhar pelas ruas hoje?

**Carlos:** A bengala branca é uma ferramenta excelente para varrer o chão e detectar degraus ou buracos, mas ela não detecta obstáculos aéreos, como orelhões, galhos de árvores ou placas baixas de trânsito. Meus alunos frequentemente batem a cabeça nessas estruturas, o que é perigoso e frustrante.

**André:** Se fôssemos criar um dispositivo com câmeras para alertá-los, talvez preso a um boné ou óculos, qual seria o maior desafio técnico na sua visão?

**Carlos:** O sistema precisaria saber com precisão a que distância o obstáculo está para emitir um aviso sonoro no momento certo. Já vi alguns alunos testarem projetos amadores colando duas webcams baratas em um capacete. O problema é que a lente entortava as imagens nas bordas, e o cálculo da distância para a parede falhava completamente.

**André:** Isso acontece por causa do formato das lentes e do desalinhamento físico entre as duas câmeras. No nosso projeto, vamos corrigir isso matematicamente aplicando um processo obrigatório de calibração nas imagens antes de calcular qualquer distância. Com isso resolvido, como o sistema deveria agir?

**Carlos:** Ele deveria usar essas duas câmeras juntas para simular a visão humana, percebendo a profundidade do ambiente e disparando um bipe assim que um galho ou placa entrasse em um raio de 1 metro de distância do rosto da pessoa.

**Enquadramento nos Requisitos:** Para resolver as falhas de cálculo de distância e a imagem "entortada" relatadas por Carlos, o sistema passará por um rigoroso processo de **calibração** usando os modelos da disciplina. O algoritmo em Python com OpenCV será responsável pela extração de parâmetros intrínsecos e extrínsecos das duas webcams, aplicando a correção de distorções radiais e tangenciais geradas pelas lentes. A qualidade desse ajuste espacial será comprovada na documentação por meio da demonstração do erro de reprojeção. A funcionalidade principal será de **Visão Estereoscópica**: duas câmeras trabalhando em conjunto para a geração de mapas de disparidade, com cálculo de profundidade baseado nos algoritmos de referência (como o de Trucco), de modo que o sistema identifique a distância dos obstáculos aéreos e emita o alerta sonoro preventivo.

---

## Entrevistas conduzidas por Rafael

### Entrevista 1: Controle de Fiado no Bar

**Entrevistado:** Gilberto (Giba), 35 anos, dono do Bar Bonsucesso.

**Rafael:** Giba, como você controla o fiado hoje?

**Giba:** No caderno, aquele de capa preta no balcão. Mas dá um trabalho enorme.

**Giba:** Sexta o bar lota e, na correria, esqueço de anotar. Aí fecho o caixa e nem sei quem levou o quê.

**Rafael:** E na hora de cobrar, lembra quem é quem?

**Giba:** O rosto eu conheço todos. Difícil é achar o nome no caderno, ainda mais com nome repetido.

**Giba:** Tem três Felipes e dois Lucas. Semana passada lancei na conta do Lucas errado e deu confusão.

**Rafael:** E se uma câmera reconhecesse o rosto e abrisse a conta certa na tela?

**Giba:** Seria perfeito. Já tentei uma câmera IP em cima do caixa, mas a imagem entorta nas bordas.

**Giba:** O rosto fica esticado se o cliente vira de lado, aquele efeito de olho de peixe. Quase não dá para reconhecer.

**Enquadramento nos Requisitos:** A dor de Giba é o controle manual do fiado: ele reconhece os rostos, mas erra ao casar cliente, nome e conta, perdendo dinheiro no movimento. A câmera angulada e próxima ao caixa gera distorção de lente (efeito "olho de peixe"), o que torna a **calibração** indispensável para corrigir a imagem antes da inferência. A identificação usará uma **rede neural (CNN)** de reconhecimento facial sobre um conjunto cadastrado de fregueses, com a conta exibida na **tela do caixa**.

### Entrevista 2: A Perspectiva do Minimercado

**Entrevistada:** Dona Solange, 52 anos, dona do Minimercado Solange.

**Rafael:** Dona Solange, como funciona o controle do fiado aqui?

**Solange:** Num fichário plástico em ordem alfabética. Mas o caixa vive cheio.

**Solange:** O cliente leva as compras com pressa, eu digo que marco depois, e a anotação se perde.

**Rafael:** E identificar quem é quem nas fichas, dá erro?

**Solange:** Demais. Tenho duas Maria de Fátima cadastradas e fico perguntando qual é, atrasa a fila e constrange.

**Rafael:** E se o sistema reconhecesse o cliente só de parar no balcão?

**Solange:** Maravilhoso. Tenho câmeras de segurança, mas para rosto são ruins.

**Solange:** Se a pessoa fica de lado, a imagem deforma nas pontas, parece dentro de uma bola de vidro.

**Enquadramento nos Requisitos:** Solange reforça os mesmos requisitos: a quebra de fluxo no caixa causa perdas, e a confusão entre nomes parecidos mostra a necessidade de identificação automática. O relato descreve distorção radial do tipo barril nas câmeras de baixo custo próximas ao balcão, justificando a etapa de **calibração** e a retificação da imagem em tempo real. A funcionalidade central é a **rede neural (CNN)** de reconhecimento facial, que dispara a consulta ao saldo devedor e o exibe na **tela do PDV**.
