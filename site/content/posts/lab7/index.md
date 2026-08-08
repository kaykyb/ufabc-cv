---
title: "Laboratório 7"
authors:
  [
    "Kayky de Brito dos Santos",
    "Andre Marques da Silva",
    "Rafael de Souza Coelho",
  ]
experimentDate: 2026-07-22
date: 2026-08-03
summary: "Introdução às Redes Neurais Convolucionais (CNNs) com TensorFlow/Keras para reconhecimento em imagens. Comparamos filtros espaciais manuais com filtros aprendidos, treinamos a RobotVisionNet no dataset CIFAR-10, analisamos os feature maps e testamos robustez e latência em tempo real com a webcam, incluindo limiares de segurança para prevenção de falsos positivos."
tags: ["lab"]
math: true
---

> Execução: o pipeline completo foi desenvolvido e executado no Google Colab, disponível [neste link](https://colab.research.google.com/drive/14YkcBCW6ieiLDhu-p8Ucuqj-h2fAd8yk?usp=sharing).

**Autores:**

- Kayky de Brito dos Santos
- André Marques da Silva
- Rafael de Souza Coelho

Equipe 8 - "Sem Título"

**Data de realização dos experimentos:** 22 de julho de 2026

**Data de publicação do relatório:** 03 de agosto de 2026

## Introdução

Este relatório descreve os experimentos do Laboratório 7 de Visão Computacional, cujo foco é a transição dos métodos clássicos de processamento de imagens baseados em filtros manuais para a extração de características baseada em dados usando Redes Neurais Convolucionais (CNNs).

Ao longo deste laboratório exploramos o framework TensorFlow/Keras para construir, treinar e avaliar uma arquitetura de rede (RobotVisionNet) treinada no dataset CIFAR-10. O objetivo final é aplicar essa percepção visual ao contexto da robótica móvel, avaliando o desempenho da rede não apenas em um ambiente validado e controlado, mas também no mundo físico real através da captura de vídeo ao vivo (webcam). O experimento culmina no desenvolvimento de mecanismos de segurança, como *Data Augmentation* e Limiares de Rejeição por Confiança (*Safety Threshold*), vitais para o processo de tomada de decisão de um robô.

## Fundamentação Teórica

### Filtros Manuais vs. Filtros Aprendidos

No processamento clássico, a extração de características depende de kernels cujos pesos são rigidamente definidos por especialistas. Um exemplo clássico é o filtro de Sobel, utilizado para a detecção de bordas espaciais por meio da aproximação de gradientes. Embora computacionalmente leves e determinísticos, esses filtros carecem de generalização em cenários onde a iluminação, a perspectiva e a escala variam drasticamente, limitando sua utilidade em ambientes externos não estruturados.

As Redes Neurais Convolucionais (CNNs), conforme descrito por Szeliski (Cap. 5.4), superam essa limitação transformando os valores dos kernels em parâmetros ajustáveis (pesos). Através do algoritmo de retropropagação (*backpropagation*) e do gradiente descendente, a rede "aprende" automaticamente quais filtros extraem as características mais discriminativas para a tarefa de classificação, partindo de bordas simples nas primeiras camadas até abstrações complexas nas camadas mais profundas.

### Arquitetura de uma CNN

A construção de um modelo convolucional para percepção robótica baseia-se em uma hierarquia espacial com três operações fundamentais:

1.  **Convolução (Conv2D):** aplicação dos múltiplos filtros aprendidos para extrair *feature maps* da imagem.
2.  **Agrupamento (MaxPooling2D):** redução da dimensionalidade espacial, que não apenas reduz o custo computacional, mas confere à rede a propriedade de invariância a pequenas translações do objeto no campo de visão.
3.  **Classificação Densa (Dense):** o vetor unidimensional final (Flatten) alimenta uma rede perceptron multicamadas que processa as características espaciais combinadas para emitir a distribuição de probabilidade das classes (função Softmax).

## Procedimentos Experimentais

Os experimentos foram desenvolvidos no ambiente Google Colab, com aceleração por hardware ativada (GPU T4) para otimizar os tempos de treinamento e inferência.

**1. Convolução clássica (OpenCV):**
Começamos extraindo uma imagem RGB (32x32) do dataset CIFAR-10, convertendo-a para tons de cinza e aplicando o filtro Sobel X (bordas verticais) com a função `cv2.filter2D`. Geramos e comparamos o processamento para três amostras distintas por aluno, evidenciando as restrições da operação puramente determinística.

**2. Preparação do dataset (CIFAR-10):**
Carregamos o dataset de 10 classes e normalizamos os pixels, dividindo os valores matriciais por 255.0.

**3. Construção e treinamento da CNN (RobotVisionNet):**
Instanciamos uma rede sequencial com duas camadas de convolução (32 e 64 filtros, função de ativação ReLU), cada uma seguida de um Max Pooling (2x2). A saída espacial foi vetorizada (`Flatten`) e conectada a uma camada densa de 128 neurônios, com regularização `Dropout` de 30% para mitigar o sobreajuste (*overfitting*), finalizando na camada de saída com 10 classes. O treinamento ocorreu por 10 épocas com o otimizador Adam e a função de custo *Sparse Categorical Crossentropy*.

**4. Extração de feature maps:**
Seccionamos a arquitetura original para extrair o tensor de saída (ativações) da camada `conv_1`, visualizando os 16 primeiros canais (filtros) aprendidos pela rede.

**5. Inferência em tempo real e desafio prático:**
Utilizamos uma ponte JavaScript/Python para injetar frames da webcam no Colab. O sistema captura a imagem, redimensiona para 32x32, normaliza e alimenta o método `model.predict`.
Para robustez, implementamos as exigências do desafio prático:

*   **Data Augmentation:** inserção de uma camada de pré-processamento aplicando espelhamento horizontal, rotação e zoom aleatórios na entrada da rede.
*   **Filtro de rejeição:** inclusão de um desvio condicional (`if confidence < 0.60`) que impede a rede de classificar objetos com baixa probabilidade, substituindo a predição pela flag visual "Objeto Não Identificado / Incerto".

---

## Análise e Discussão

Ao longo da execução, analisamos o comportamento do modelo e reunimos as seguintes discussões e respostas aos questionamentos do roteiro:

**1. Limitação dos filtros clássicos:** a principal limitação matemática e prática de filtros rígidos (como Sobel) num robô em ambiente externo é a sua inflexibilidade. Eles são sensíveis a ruídos, requerem calibração manual de limiares baseada em suposições (como iluminação e contraste ideais) e não se adaptam dinamicamente a novos tipos de texturas ou deformações.

**2. O que a CNN aprende:** a rede neural substitui o design manual ao aprender, através do treinamento, os valores ótimos da matriz do kernel de convolução. Ela descobre autonomamente as estruturas matemáticas que melhor separam e identificam as classes daquele banco de dados.

**3. Necessidade de normalização ($/255.0$):** a normalização dos inputs para o intervalo contínuo $[0, 1]$ estabiliza os cálculos numéricos durante o gradiente descendente. Sem ela, grandes variações nos valores de ativação causam saltos bruscos nos pesos ou saturação precoce nas funções de ativação, dificultando ou impedindo a convergência do erro.

**4. Impacto do hardware (resolução 4K):** se alimentássemos imagens 4K ($3840 \times 2160$) diretamente na rede sem drástica redução espacial via Pooling, a camada *Flatten* resultaria em dezenas de milhões de atributos. Conectar isso a uma camada Densa geraria bilhões de parâmetros de peso a serem carregados na VRAM. Em hardware embarcado (como microcontroladores ou Raspberry Pi em robôs móveis), isso causaria falta de memória (OOM - *Out of Memory*) e tornaria o processamento impraticável em tempo real.

**5. Organização da arquitetura (Conv2D antes de Dense):** as camadas `Conv2D` operam extraindo representações espaciais (onde os pixels formam linhas e formas geométricas contíguas). Se a imagem fosse achatada e passada para a camada `Dense` primeiro, a topologia 2D e as relações espaciais seriam destruídas prematuramente. A camada Densa no final atua como um classificador analítico unindo as características abstratas montadas pelas convoluções.

**6. Interpretação das curvas de aprendizado (Loss):** a função de perda mede o quão distante a predição da rede está da classificação real (o "erro"). Quando a perda de treinamento despenca enquanto a perda de validação estagna ou sobe, ocorre o sobreajuste (*overfitting*). Na prática robótica, isso significa que a máquina decorou perfeitamente as imagens do laboratório, mas falhará em reconhecer os mesmos objetos no mundo real.

**7. Matriz de confusão e semântica visual:** na matriz gerada, as classes com maiores índices de falsos positivos foram "Automóvel" e "Caminhão", e frequentemente "Gato" e "Cachorro". Isso decorre da alta semelhança semântica de suas características espaciais sob a baixa resolução de 32x32: automóveis e caminhões possuem chassi, rodas e rodam em superfícies parecidas (estradas de asfalto/fundo cinza), dificultando a separação das métricas geométricas apenas por um kernel simples.

**8. Peso de gravidade no erro do robô:** em um sistema de frenagem, errar "Automóvel" classificando-o como "Caminhão" mantém uma predição semântica de "veículo grande em movimento", o que ainda acionaria o freio. No entanto, confundir um "Cachorro" (objeto dinâmico, vulnerável) com um "Caminhão", ou pior, com fundo inanimado, pode resultar em atropelamento. A Matriz de Confusão permite ao engenheiro mapear os falsos negativos críticos e auditar a segurança limitando a predição.

**9. Feature maps (complexidade vs. profundidade):** na camada inicial `conv_1`, observamos que os canais reagem a estímulos básicos (bordas, contrastes locais). Devido ao aumento progressivo do campo receptivo da rede, se inspecionássemos a última convolução antes do classificador, os *feature maps* conteriam padrões altamente abstratos (partes de um rosto animal ou uma roda montada), criados pela justaposição hierárquica das características simples mapeadas nas camadas anteriores.

**10. Domain Shift no teste ao vivo:** a acurácia caiu durante os testes na webcam devido ao *Domain Shift*. O ambiente do mundo físico difere das imagens estabilizadas do CIFAR-10 em ao menos três aspectos: 1) fundo complexo (ruído visual no quarto/laboratório versus focos isolados), 2) iluminação não controlada (luz fluorescente criando sombras no objeto) e 3) escala e perspectiva (a distância do objeto até a lente altera o tamanho aparente, algo não totalmente abordado no CIFAR original).

**11. Latência e velocidade de decisão:** o tempo de computação de inferência gera um atraso sistêmico. Se o robô anda a $2 \text{ m/s}$ e a inferência custa $0.5 \text{ s}$, ele percorrerá $\Delta S = v \cdot t = 2 \cdot 0.5 = 1 \text{ metro}$ inteiramente "às cegas". Isso impõe um compromisso de engenharia clássico: uma rede gigantesca pode ser mais acurada, mas sua latência elevada a torna um perigo mecânico fatal. O tempo de resposta deve nortear o design da arquitetura.

## Conclusões

Este laboratório validou o funcionamento da cadeia completa de percepção visual inteligente em contexto robótico. Fica claro que as CNNs eliminam a engenharia de requisitos manuais dos filtros de imagem, mas introduzem complexidades baseadas em dados empíricos.

A transição do modelo treinado no CIFAR-10 para a webcam expôs os desafios práticos das aplicações no mundo real (*Domain Shift*). Estratégias adicionadas no desafio prático, como o aumento artificial de dados (*Data Augmentation*) e o bloqueio estrito de predições incertas sob baixa confiança, provaram-se mecanismos de segurança vitais. A métrica de acurácia em ambiente isolado pode ser ilusória; para a robótica móvel em tempo real, o equilíbrio fino entre a leveza da topologia (para baixa latência) e a generalização dos parâmetros determina o sucesso ou a falha da máquina.

## Declaração de uso de Inteligência Artificial Generativa

Em atendimento à Portaria CNPq 2664/2026, declaramos que ferramentas de Inteligência Artificial Generativa (IAG) foram utilizadas como apoio secundário na organização estrutural, revisão gramatical da escrita deste relatório e conversão tipográfica para Markdown. Toda a concepção analítica das respostas, manipulação empírica dos dados da rede neural, treinamento no Google Colab e as deduções obtidas a partir dos resultados matemáticos foram conduzidas integralmente pela capacidade cognitiva dos autores. O código implementado foi programado manualmente sem injeção cega via LLMs. A equipe atesta a total veracidade e responsabiliza-se integralmente pelos apontamentos científicos registrados.

## Referências

- [1] Szeliski, R. _Computer Vision: Algorithms and Applications (2nd Ed.)._ <https://szeliski.org/Book/>
- [2] TensorFlow. _Documentação oficial do TensorFlow / Keras._ <https://www.tensorflow.org/api_docs/python/tf/keras>
- [3] UFABC. _Material da disciplina UFABC, Visão Computacional, Laboratório 7._ <https://www.ufabc.edu.br>
