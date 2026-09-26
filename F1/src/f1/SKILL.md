---
name: python-project-standards
description: Guia operacional obrigatório para desenvolver, testar, formatar e documentar este projeto Python. Use sempre que for implementar ou alterar código em src/projeto, criar/atualizar testes, rodar lint/formatação, medir cobertura, gerenciar dependências (Poetry/pyenv) ou atualizar a documentação (MkDocs Material). Consulte este arquivo antes de considerar qualquer tarefa de código concluída.
---

# SKILL.md — Padrão de Desenvolvimento do Projeto

Este documento é o guia de execução obrigatório para qualquer pessoa ou agente de IA que
desenvolva neste projeto Python. Ele define **ferramentas obrigatórias**, **comandos exatos**,
**estrutura esperada** e **critérios de qualidade verificáveis**. Nenhuma tarefa deve ser
considerada concluída sem passar pelas validações descritas aqui.

## Ferramentas obrigatórias (resumo)

| Categoria | Ferramenta | Proibido usar em vez dela |
|---|---|---|
| Versão do Python | pyenv | instalação manual do Python no sistema |
| Dependências/empacotamento | Poetry | `pip install` direto no projeto |
| Lint e formatação | Ruff | black, flake8, isort, autopep8 |
| Testes | pytest + pytest-cov | unittest puro, nose |
| Documentação | MkDocs Material | Sphinx, README solto como única doc |

---

## 1. Ambiente e dependências (pyenv + Poetry)

### 1.1 Configuração do zero

```bash
# 1. Instalar a versão do Python definida pelo projeto (ver .python-version)
pyenv install 3.12.4        # ajuste para a versão real definida no projeto
pyenv local 3.12.4          # grava/atualiza o arquivo .python-version na raiz

# 2. Garantir que o Poetry use a versão do pyenv ativa
poetry env use $(pyenv which python)

# 3. Instalar as dependências do projeto (cria a venv automaticamente)
poetry install

# 4. Executar qualquer comando dentro do ambiente do Poetry
poetry run <comando>
# ou, alternativamente, ativar o shell do ambiente:
poetry shell
```

### 1.2 Regras

- A versão do Python **deve** estar declarada em `.python-version` (pyenv) **e** em
  `pyproject.toml` na seção `[tool.poetry.dependencies]` (`python = "^3.12"`, por exemplo).
- Toda dependência nova é adicionada com `poetry add <pacote>` (ou `poetry add --group dev <pacote>`
  para dependências de desenvolvimento, como Ruff, pytest, mkdocs-material).
- **Nunca** rodar `pip install` para dependências do projeto. `pip` só pode aparecer indiretamente,
  gerenciado pelo próprio Poetry.
- Qualquer script, teste, lint, build de documentação etc. deve ser executado via
  `poetry run ...`, nunca chamando o interpretador global do sistema.

```bash
poetry add requests                 # dependência de produção
poetry add --group dev pytest ruff mkdocs-material pytest-cov   # dependências de dev
poetry lock                         # regenera o poetry.lock quando necessário
poetry install --sync               # sincroniza o ambiente exatamente com o lock
```

---

## 2. Lint e formatação (Ruff)

### 2.1 Instalação

```bash
poetry add --group dev ruff
```

### 2.2 Configuração centralizada no `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 2.3 Comandos obrigatórios

```bash
# Checar problemas de lint (falha se houver violações)
poetry run ruff check src tests

# Corrigir automaticamente o que for possível
poetry run ruff check src tests --fix

# Formatar o código (altera os arquivos)
poetry run ruff format src tests

# Verificar formatação SEM alterar arquivos (usado em CI/antes de commit)
poetry run ruff format src tests --check
```

**Regra:** nenhum código é considerado pronto se `ruff check` reportar erros ou se
`ruff format --check` indicar arquivos não formatados.

---

## 3. Testes unitários (pytest + pytest-cov)

### 3.1 Instalação

```bash
poetry add --group dev pytest pytest-cov
```

### 3.2 Estrutura esperada

```
tests/
├── __init__.py
└── test_<modulo>.py   # um arquivo de teste por módulo relevante de src/projeto
```

### 3.3 Configuração centralizada no `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/projeto --cov-report=term-missing --cov-fail-under=50"

[tool.coverage.run]
source = ["src/projeto"]

[tool.coverage.report]
fail_under = 50
show_missing = true
```

Com essa configuração, `poetry run pytest` já aplica cobertura e o corte mínimo automaticamente.

### 3.4 Comandos obrigatórios

```bash
# Rodar toda a suíte de testes (com cobertura aplicada via pyproject.toml)
poetry run pytest

# Rodar um teste específico
poetry run pytest tests/test_modulo.py::test_funcao_especifica

# Rodar com relatório de cobertura explícito (equivalente reforçado)
poetry run pytest --cov=src/projeto --cov-report=term-missing --cov-fail-under=50

# Gerar relatório de cobertura em HTML para inspeção
poetry run pytest --cov=src/projeto --cov-report=html
```

**Regra:** a tarefa **não pode** ser considerada concluída se `poetry run pytest` falhar,
seja por teste quebrado, seja porque a cobertura de `src/projeto` ficou abaixo de **50%**.
Isso é reforçado por `--cov-fail-under=50` no `pyproject.toml`, então qualquer execução
abaixo do limite já retorna código de saída diferente de zero.

---

## 4. Documentação (MkDocs Material)

### 4.1 Instalação

```bash
poetry add --group dev mkdocs-material
```

### 4.2 Estrutura esperada

```
docs/
├── index.md
├── guia-de-uso.md
└── ...            # uma página por tema relevante (instalação, API, arquitetura etc.)
mkdocs.yml
```

### 4.3 Configuração mínima do `mkdocs.yml`

```yaml
site_name: Projeto
theme:
  name: material
  features:
    - navigation.tabs
    - content.code.copy
nav:
  - Início: index.md
  - Guia de uso: guia-de-uso.md
```

### 4.4 Comandos obrigatórios

```bash
# Servir a documentação localmente (hot-reload) para revisão
poetry run mkdocs serve

# Gerar o build estático da documentação (valida se está tudo correto)
poetry run mkdocs build --strict
```

### 4.5 Boas práticas

- Toda alteração de comportamento, API pública ou configuração do projeto **deve** vir
  acompanhada de atualização das páginas correspondentes em `docs/`.
- Usar `mkdocs build --strict` para garantir que links quebrados ou warnings de navegação
  interrompam o processo (falha explícita em vez de erro silencioso).
- Exemplos de código na documentação devem ser mantidos coerentes com a API real do projeto.

---

## 5. Estrutura do projeto

```
.
├── src/
│   └── projeto/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── docs/
│   └── index.md
├── mkdocs.yml
├── pyproject.toml
├── poetry.lock
├── .python-version
└── SKILL.md
```

Arquivos adicionais recomendados (adicionar apenas se necessário, mantendo o projeto simples):

- `.gitignore` — ignorar `.venv/`, `__pycache__/`, `site/` (build do MkDocs), `.pytest_cache/`, `htmlcov/`
- `.github/workflows/ci.yml` — pipeline de CI opcional replicando os passos deste SKILL.md
  (`ruff check`, `ruff format --check`, `pytest --cov-fail-under=50`, `mkdocs build --strict`)
- `README.md` — visão geral curta do projeto, apontando para `docs/` como fonte principal

---

## 6. Fluxo de desenvolvimento (obrigatório, nesta ordem)

Ao implementar ou alterar qualquer parte do projeto, seguir exatamente esta sequência:

1. **Verificar a versão do Python** do projeto em `.python-version` / `pyproject.toml`.
2. **Verificar o ambiente Poetry**: `poetry env info` (criar/ajustar se necessário com
   `poetry env use $(pyenv which python)`).
3. **Instalar/sincronizar dependências**: `poetry install` (ou `poetry install --sync`).
4. **Implementar ou modificar o código** em `src/projeto`.
5. **Criar ou atualizar os testes correspondentes** em `tests/`.
6. **Executar o lint**: `poetry run ruff check src tests` (corrigir todas as violações).
7. **Executar o formatter**: `poetry run ruff format src tests`.
8. **Executar os testes com cobertura**: `poetry run pytest`.
9. **Garantir cobertura mínima de 50%** em `src/projeto` (o próprio `pytest` falha se não atingir).
10. **Atualizar a documentação** em `docs/` quando houver mudança de comportamento, API ou configuração.
11. **Validar o build da documentação**: `poetry run mkdocs build --strict`.
12. **Somente considerar a tarefa concluída** quando os passos 6, 8/9 e 11 passarem sem erros.

Checklist rápido de "pronto para entregar":

```bash
poetry run ruff check src tests \
  && poetry run ruff format src tests --check \
  && poetry run pytest \
  && poetry run mkdocs build --strict
```

Se qualquer um desses comandos falhar, a tarefa **não está concluída**.

---

## 7. Regras para a IA/agente

Ao atuar neste projeto, a IA/agente **deve**:

- Respeitar a estrutura de diretórios existente (`src/projeto`, `tests/`, `docs/`).
- Usar **exclusivamente** as ferramentas definidas neste documento (Poetry, pyenv, Ruff,
  pytest/pytest-cov, MkDocs Material). Não introduzir ferramentas alternativas
  (ex.: black, pip puro, unittest, Sphinx) sem justificativa explícita e aprovação do usuário.
- **Nunca** instalar dependências globalmente no sistema; toda dependência entra via
  `poetry add` (ou `poetry add --group dev`).
- Executar ferramentas e scripts sempre via `poetry run ...`.
- Criar ou atualizar testes para **toda** alteração de comportamento de código.
- Manter ou aumentar a cobertura de testes existente; **nunca** reduzir a cobertura total
  de `src/projeto` para abaixo de **50%**.
- Executar `ruff check`, `ruff format` e `pytest` (com cobertura) **antes** de considerar
  qualquer implementação concluída.
- Atualizar a documentação (`docs/` + `mkdocs.yml` quando aplicável) sempre que a mudança
  afetar comportamento, API pública ou configuração do projeto.
- Evitar alterações fora do escopo da tarefa solicitada (sem refatorações não pedidas,
  sem trocar dependências sem necessidade).
- Preferir soluções simples, idiomáticas e alinhadas ao ecossistema Python padrão
  (tipagem quando fizer sentido, funções pequenas e testáveis, nomes claros).
- Centralizar configurações de ferramentas no `pyproject.toml`, evitando arquivos de
  configuração duplicados ou espalhados (ex.: não criar `.flake8`, `setup.cfg` etc.).

---

## 8. Configuração centralizada no `pyproject.toml`

Exemplo consolidado (ajustar nomes/versões conforme o projeto real):

```toml
[tool.poetry]
name = "projeto"
version = "0.1.0"
description = ""
authors = []
packages = [{ include = "projeto", from = "src" }]

[tool.poetry.dependencies]
python = "^3.12"

[tool.poetry.group.dev.dependencies]
ruff = "^0.6"
pytest = "^8.0"
pytest-cov = "^5.0"
mkdocs-material = "^9.5"

[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/projeto --cov-report=term-missing --cov-fail-under=50"

[tool.coverage.run]
source = ["src/projeto"]

[tool.coverage.report]
fail_under = 50
show_missing = true

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

Isso garante que Poetry, Ruff, pytest e pytest-cov leiam suas configurações de um único
lugar, sem duplicação entre arquivos.

---

## 9. Definição de "concluído" (Definition of Done)

Uma tarefa só é considerada finalizada quando **todos** os itens abaixo forem verdadeiros:

- [ ] Código implementado em `src/projeto`, seguindo a estrutura existente.
- [ ] Testes criados/atualizados em `tests/` cobrindo a mudança.
- [ ] `poetry run ruff check src tests` sem erros.
- [ ] `poetry run ruff format src tests --check` sem pendências.
- [ ] `poetry run pytest` passando, com cobertura de `src/projeto` ≥ 50%.
- [ ] Documentação em `docs/` atualizada, se houve mudança de comportamento/API/configuração.
- [ ] `poetry run mkdocs build --strict` concluído sem erros.
- [ ] Nenhuma alteração fora do escopo da tarefa solicitada.
