# ufabc-cv

Notebooks, scripts e relatórios da disciplina de Visão Computacional (UFABC).

Site publicado: <https://kaykyb.github.io/ufabc-cv/>

## Estrutura

```
laboratorios/        # notebooks Jupyter, um diretório por laboratório
scripts/             # utilitários Python
data/                # dados (amostras pequenas; grandes ficam fora do git)
site/                # site Hugo (tema PaperMod)
  content/posts/     # relatórios - um page bundle por laboratório
```

## Fluxo de um relatório

1. Desenvolver o notebook em `laboratorios/labN/labN.ipynb`.
2. Criar `site/content/posts/labN/index.md`.
3. Exportar figuras relevantes para o mesmo diretório do `index.md` e referenciá-las como `![](figura.png)`.
4. Incluir no topo do post o link para o notebook no GitHub.

Os relatórios são escritos à mão (prosa, blocos de código, imagens). Não há conversão automática de `.ipynb`.

## Desenvolvimento local

```
make serve     # hugo server em http://localhost:1313
make build     # gera site/public
make clean
```

Clonar com submódulos: `git clone --recurse-submodules ...` (o tema PaperMod é um submódulo).

## Deploy

GitHub Actions (`.github/workflows/deploy.yml`) faz build e publica no GitHub Pages a cada push em `main`. Em **Settings → Pages**, definir _Source_ como **GitHub Actions**.