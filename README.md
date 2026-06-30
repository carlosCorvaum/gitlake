# 🐙 GitLake

> Um mini data-lake versionado, leve e open-source, usando **GitHub + pandas + requests**

O **GitLake** é um framework simples e poderoso que permite salvar, versionar e gerenciar **coleções de dados** diretamente em repositórios do GitHub.

Ideal para projetos de dados, pipelines, protótipos de machine learning e experimentos que precisam de um **repositório remoto e versionado**, sem a complexidade e o custo de uma infraestrutura em nuvem.

---

## 🚀 Instalação

> Ainda não publicado no PyPI. Por enquanto, instale a partir do código-fonte:

```bash
git clone https://github.com/carloscorvaum/gitlake.git
cd gitlake
pip install .
```

Para desenvolvimento (inclui as dependências de teste):

```bash
pip install -e ".[dev]"
```

## 🧠 Funcionalidades principais

📁 Gerenciamento de coleções de DataFrames diretamente no GitHub <br>
💾 Suporte a formatos: csv, json, parquet <br>
✍️ Modos de escrita: overwrite, append <br>
🕒 Controle de metadados: created_at, updated_at <br>
🔐 Autenticação via GitHub Personal Access Token <br>
🗑️ Exclusão lógica e física de coleções <br>
🔄 Totalmente baseado em GitHub como backend remoto <br>

---

## 📦 Requisitos

- python 3.9+ <br>
- pandas <br>
- requests <br>
- pyarrow <br>

Instalados automaticamente ao instalar o gitlake.

---

## ⚡ Quickstart

```python
import os
import pandas as pd
from gitlake import GitConnection, CollectionManager, Collection

git = GitConnection(
    repo_url="https://github.com/seu-usuario/seu-repo.git",
    username="seu-usuario",
    token=os.environ["GIT_TOKEN"],  # GitHub Personal Access Token
)

cm = CollectionManager(git)

# Cria uma coleção
vendas = Collection(name="vendas", base_path="data", path="vendas", format="parquet")
cm.create_collection(vendas)

# Salva um DataFrame na coleção
df = pd.DataFrame({"produto": ["a", "b"], "preco": [10, 20]})
cm.save_dataframe(df, collection_name="vendas")

# Lê de volta
df = cm.read_dataframe("vendas")

# Remove a coleção (dados + registro)
cm.delete_collection("vendas")
```

Um notebook completo com exemplos está em [`test.ipynb`](./test.ipynb).

---

## ⚠️ Tratamento de erros

Falhas na comunicação com a API do GitHub são sinalizadas com exceções específicas (`gitlake.connection`):

| Exceção | Quando ocorre |
|---|---|
| `FileNotFoundError` | Arquivo/coleção não existe no repositório |
| `GitHubAuthError` | Token inválido ou expirado (HTTP 401) |
| `GitHubRateLimitError` | Rate limit ou acesso negado (HTTP 403/429) |
| `GitHubConflictError` | Escrita/remoção concorrente — sha desatualizado (HTTP 409) |
| `GitHubAPIError` | Erro genérico da API do GitHub (inclui arquivos grandes demais para leitura inline) |

---

## 📁 Estrutura do gitlake recomendada

```
.
├── metadata/
│   └── collections_registry.json      # Registro de todas as coleções
└── data/
    ├── raw/
    │   └── raw.parquet           # Dados da coleção
    ├── bronze/
    │   └── bronze.parquet
    └── silver/
        └── silver.parquet
```

---

## 🔐 Autenticação

Você precisa de um GitHub Personal Access Token (PAT) com permissão para ler e escrever no repositório desejado.
Gere um token aqui:
https://github.com/settings/tokens

Use esse token com segurança (nunca o exponha em código versionado — prefira variáveis de ambiente). Para repositórios privados, ele é obrigatório.

---

## 🧪 Casos de uso

- Publicar datasets com versionamento
- Salvar resultados de ETLs diretamente no GitHub
- Criar um "data catalog" simples para seu time
- Compartilhar coleções de dados versionadas em repositórios abertos

---

## 🧰 Desenvolvimento

```bash
pip install -e ".[dev]"
pytest
```

---

## 📄 Licença

MIT — veja [LICENSE](./LICENSE).
