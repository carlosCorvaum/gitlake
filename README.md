# 🐙 GitLake

> Um mini data-lake versionado, leve e open-source, usando apenas **GitHub + pandas + requests**

O **GitLake** é um framework simples e poderoso que permite salvar, versionar e gerenciar **coleções de dados** diretamente em repositórios do GitHub.

Ideal para projetos de dados, pipelines, protótipos de machine learning e experimentos que precisam de um **repositório remoto e versionado**, sem a complexidade de uma infraestrutura em nuvem.

---

## 🚀 Instalação

Via PyPI (em breve):

``bash
pip install gitlake
``

Ou instalando manualmente:

git clone https://github.com/carloscorvaum/gitlake.git
cd gitlake
pip install .

🧠 Funcionalidades principais
📁 Gerenciamento de coleções de DataFrames diretamente no GitHub
💾 Suporte a formatos: csv, json, parquet
✍️ Modos de escrita: overwrite, append
🕒 Controle de metadados: created_at, updated_at
🔐 Controle de versionamento Git
🗑️ Exclusão lógica e física de coleções
🔄 Totalmente baseado em GitHub como backend remoto



---

## 📦 Requisitos
Python 3.9+
pandas
requests
pyarrow
Instalados automaticamente via:

pip install gitlake


📁 Estrutura esperada
. <br>
├── metadata/  <br>
│   └── collections_registry.json     <br> # Registro de todas as coleções
└── data/     <br>
    └── minha_colecao/     <br>
        └── minha_colecao.csv            <br>  # Dados da coleção

🔐 Autenticação
Você precisa de um GitHub Personal Access Token (PAT) com permissão para ler e escrever no repositório desejado.

Gere um token aqui:
https://github.com/settings/tokens

Use esse token com segurança. Para repositórios privados, ele é obrigatório.


🧪 **Casos de uso

- Publicar datasets com versionamento
- Salvar resultados de ETLs diretamente no GitHub
- Criar um "data catalog" simples para seu time
- Compartilhar coleções de dados versionadas em repositórios abertos
