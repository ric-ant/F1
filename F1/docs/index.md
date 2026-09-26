# F1 Lap Comparison Dashboard - Projeto Supervisionado e aprovado por: Ricardo Antonello

Dashboard HTML interativo que consome a [API OpenF1](https://openf1.org) para gerar comparativos de tempos de volta entre pilotos de uma sessão de Fórmula 1.

## O que é

Este projeto gera um arquivo `dashboard.html` standalone com gráficos interativos (Plotly) mostrando:

- **Comparativo de tempos de volta** — uma linha por piloto, volta a volta, com detalhes de setor no hover
- **Resumo de pit stops** — tabela com duração e timing das paradas

Sem necessidade de servidor: o HTML gerado funciona direto no browser.

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/) para gerenciamento de dependências
- Conexão com a internet (para consultar a API OpenF1)

## Início rápido

```bash
# Instalar dependências
poetry install

# Gerar dashboard para o GP de Mônaco 2023
poetry run f1-dashboard --year 2023 --gp Monaco --session Race --output monaco_2023.html
```

Abra o arquivo `monaco_2023.html` no browser para visualizar o dashboard.

## Documentação

- [Guia de Uso](guia-de-uso.md) — instalação detalhada e exemplos
- [Arquitetura](arquitetura.md) — estrutura do código e fluxo de dados
- [Referência da API](api-reference.md) — endpoints OpenF1 utilizados
