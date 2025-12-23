# 📊 COVID-19 Dashboard Brasil

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-7A76FF?style=for-the-badge&logo=plotly&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-7A76FF?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

Um dashboard interativo desenvolvido em Python para monitoramento e análise da evolução da COVID-19 no Brasil. O projeto utiliza dados públicos do [Brasil.IO](https://brasil.io/dataset/covid19/caso_full/), permitindo visualizações detalhadas por Estados e Municípios através de mapas, gráficos de evolução temporal e rankings.

## 🖼️ Visualização

<img width="1920" height="1080" alt="dashboard" src="https://github.com/user-attachments/assets/f7acf685-786c-4a25-90b5-4b1e5535c5ee" />

## 🚀 Funcionalidades

- **Filtros Dinâmicos:** Seleção por Estado (UF), Múltiplos Municípios e Tipo de Dado (Casos Confirmados ou Óbitos).
- **KPIs em Tempo Real:** Cartões informativos com Total Acumulado, Novos Casos (24h), Média por Município e Taxa de Letalidade.
- **Mapa Coroplético Interativo:** Visualização geoespacial colorida por densidade de casos/óbitos a cada 100k habitantes (Mapbox/Leaflet).
- **Análise Temporal:** Gráfico de linha otimizado mostrando a evolução mensal (Top 10 locais).
- **Ranking (Top 50):** Gráfico de barras horizontal com rolagem (scroll) para visualizar os municípios ou estados mais afetados.
- **Tabela de Dados:** Visualização tabular dos dados filtrados.
- **Modo Escuro (Dark Mode):** Interface moderna utilizando o tema *Slate* do Bootstrap.
- **Otimização de Performance:** Uso de arquivos **Parquet** para leitura rápida de grandes volumes de dados e pré-cálculo de colunas.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** [Python](https://www.python.org)
- **Framework Web:** [Dash](https://dash.plotly.com/)
- **Visualização de Dados:** [Plotly Express](https://plotly.com/python/)
- **Manipulação de Dados:** [Pandas](https://pandas.pydata.org/)
- **Estilização:**
  - [Dash Bootstrap Components](https://www.dash-bootstrap-components.com/docs/) (`dbc`)
  - [Dash Bootstrap Templates](https://pypi.org/project/dash-bootstrap-templates/) (Tema: Slate)
  - CSS Customizado (Scrollbars)
- **Formatos de Dados:** CSV (Raw), Parquet (Otimizado), GeoJSON (Mapas).

## 📂 Estrutura do Projeto

```text
CovidDashboard/
├── .python-version                             # Arquivo de versão do Python
├── pyproject.toml                              # Dependências (uv)
├── README.md                                   # Documentação do projeto
├── requirements.txt                            # Requisitos de pacotes do python
├── uv.lock                                     # Arquivo de sincronização do uv (Versionamento de pacotes)
└── src/
    ├── app.py                                  # Aplicação principal (Layout e Callbacks)
    ├── data_manager.py                         # Classe responsável pelo ETL e carregamento de dados
    └── data/
        ├── parquet/
        │   ├── covid_brasil_full.parquet       # Arquivo parquet otimizado com os dados de Covid-19 do Brasil
        │   └── covid_brasil_last.parquet       # Arquivo parquet otimizado com os últimos dados de Covid-19 do Brasil
        └── raw_data/
            ├── covid_brasil.csv                # Arquivo original retirado de Brasil.io
            ├── geojson_br.json                 # Arquivo de geojson para mapas
            └── states_localization.py          # Arquivo de latitude e longitude dos estados do Brasil
```

## ⚙️ Como Rodar o Projeto

### Pré-requisitos

Certifique-se de ter o Python 3.10 instalado.

**1. Clonar o repositório**

```bash
git clone https://github.com/gblelis/CovidDashboard.git
cd CovidDashboard
```

**2. Criar e ativar um ambiente virtual**

- Usando `uv` (Recomendado):

```bash
pip install uv  # Se não estiver instalado
uv init
uv venv
```

- Usando `pip` padrão:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

**3. Instalar as dependências**

- Usando `uv` (Recomendado):

```bash
uv sync
```

- Usando `pip` padrão:

```bash
pip install -r requirements.txt
```

**4. Executar a aplicação**

O script irá gerar automaticamente os arquivos `.parquet` na primeira execução (pode levar alguns segundos).

```bash
python src/app.py
```

Acesse no navegador: `http://127.0.0.1:8050/`

## 📊 Fonte de Dados
Os dados utilizados neste projeto foram obtidos através do [Brasil.IO](https://brasil.io/dataset/covid19/caso_full/), uma iniciativa que compila boletins epidemiológicos das Secretarias Estaduais de Saúde.

## 📝 Licença

MIT License © 2025 Gabriel Lelis