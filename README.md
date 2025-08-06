# 🐙 GitLake

> Um mini data-lake versionado, leve e open-source, usando **GitHub + pandas + requests**

O **GitLake** é um framework simples e poderoso que permite salvar, versionar e gerenciar **coleções de dados** diretamente em repositórios do GitHub.

Ideal para projetos de dados, pipelines, protótipos de machine learning e experimentos que precisam de um **repositório remoto e versionado**, sem a complexidade e o custo de uma infraestrutura em nuvem.

---

## 🚀 Instalação

Via PyPI (em breve):
``pip install gitlake``

Ou instalando manualmente:

``git clone https://github.com/carloscorvaum/gitlake.git``
<br>
``cd gitlake``
<br>
``pip install``

## 🧠 Funcionalidades principais <br>

📁 Gerenciamento de coleções de DataFrames diretamente no GitHub <br>
💾 Suporte a formatos: csv, json, parquet <br>
✍️ Modos de escrita: overwrite, append <br>
🕒 Controle de metadados: created_at, updated_at <br>
🔐 Controle de versionamento Git <br>
🗑️ Exclusão lógica e física de coleções <br>
🔄 Totalmente baseado em GitHub como backend remoto <br>

---

## 📦 Requisitos

- Python 3.9+ <br>
- pandas <br>
- requests <br>
- pyarrow <br>

Instalados automaticamente via:
``pip install gitlake``

---

## 📁 Estrutura do gitlake recomendada

```
.
├── metadata/
│   └── collections_registry.json      # Registro de todas as coleções
└── data/
    ├── raw/
    │   └── raw_zone.parquet           # Dados da coleção
    ├── bronze/
    │   └── bronze.parquet
    └── silver/
        └── silver.parquet
```

---

##🔐 Autenticação

Você precisa de um GitHub Personal Access Token (PAT) com permissão para ler e escrever no repositório desejado.
Gere um token aqui:
https://github.com/settings/tokens

Use esse token com segurança. Para repositórios privados, ele é obrigatório.

---

## 🧪 Casos de uso

- Publicar datasets com versionamento
- Salvar resultados de ETLs diretamente no GitHub
- Criar um "data catalog" simples para seu time
- Compartilhar coleções de dados versionadas em repositórios abertos
