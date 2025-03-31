```markdown
# Calculadora de Redução de INSS em Obras

Este projeto é uma aplicação web desenvolvida em Python/Flask para auxiliar na aferição e cálculo dos encargos do INSS em obras de construção civil, com base na Instrução Normativa RFB nº 971/2009. A aplicação permite ao usuário inserir dados da obra (área, CUB, notas fiscais, etc.), gerar diversas tabelas de cálculo (áreas, aferição indireta, tabela financeira e INSS detalhado) e visualizar os resultados, incluindo a economia gerada pela redução aplicada.

## Funcionalidades

- **Cadastro de Obra:** Formulário para inserção dos dados da obra, com campos para identificação, categoria, material, tipo de área, área total, CUB, UF, concreto usinado, destinação, valor das notas fiscais e área aferida.
- **Tooltips:** Ícones de “?” em cada campo do formulário para auxiliar o usuário com explicações sobre o que cada campo representa.
- **Cálculo de Índices:** Cálculo do Valor Atualizado Unitário (VAU) a partir do CUB e dos demais índices, como Remuneração da Mão de Obra Total (RMT).
- **Tabelas de Cálculo:** Geração de quatro tabelas:
  - **Tabela de Áreas:** Exibe os dados inseridos e os cálculos iniciais (RMT, custo da obra, etc.).
  - **Aferição Indireta:** Exibe os ajustes realizados com base no fator de ajuste e nos meses de execução.
  - **Tabela Financeira:** Detalha os encargos mensais (valor atualizado, CPP, multa, juros de mora, MAED mínima, total, etc.) com base na SELIC.
  - **INSS Detalhado:** Mostra o INSS Devido, o INSS a Pagar, a Economia Gerada, os Honorários e a Economia Real.
- **Integração com API do Banco Central:** Para a obtenção das taxas SELIC, utilizadas na atualização dos valores financeiros.

## Estrutura do Projeto

```
Calculadora/
├── app.py
├── data/
│   └── dados_percentuais.py
├── static/
│   ├── script.js
│   └── styles.css
├── templates/
│   ├── index.html
│   └── resultado.html
└── utils/
    ├── calculos.py
    └── tabelas.py
```

- **app.py:** Arquivo principal da aplicação Flask.
- **data/dados_percentuais.py:** Contém os dados de percentuais por UF e tipo de obra.
- **static/**: Arquivos estáticos (CSS, JavaScript).
- **templates/**: Templates HTML da aplicação.
- **utils/**: Módulos Python com funções de cálculo e geração de tabelas.

## Instalação

### Pré-requisitos

- Python 3.6 ou superior
- Pip (gerenciador de pacotes Python)

### Passos para Instalação

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/calculadora-inss-obras.git
   cd calculadora-inss-obras
   ```

2. **Crie e ative um ambiente virtual (opcional, mas recomendado):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências:**

   As dependências principais são o Flask e o Pandas. Você pode instalá-las usando:

   ```bash
   pip install flask pandas python-dateutil requests
   ```

   *Obs.:* O Bootstrap e jQuery são carregados via CDN no template HTML.

## Uso

1. **Execute a aplicação:**

   ```bash
   python app.py
   ```

2. **Acesse a aplicação:**

   Abra o navegador e acesse [http://127.0.0.1:5000](http://127.0.0.1:5000).

3. **Preencha o formulário:**

   Insira os dados da obra. Para cada campo, clique no ícone de "?" para ver uma breve explicação.

4. **Envie o formulário:**

   Ao clicar em “Enviar”, a aplicação irá processar os dados e gerar as tabelas com os cálculos, exibindo:
   - Tabela de Áreas
   - Aferição Indireta
   - Tabela Financeira
   - INSS Detalhado

## Referências

- **Instrução Normativa RFB nº 971/2009**  
  Disponível em: [Instrução Normativa RFB nº 971/2009](http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=15937#:~:text=IN%20RFB%20n%C2%BA%20971%2F2009&text=Disp%C3%B5e%20sobre%20normas%20gerais%20de,Federal%20do%20Brasil%20(RFB).)

- **SINAPI - Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil**  
  Fonte dos dados do CUB e índices de construção.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

---

Sinta-se à vontade para contribuir, abrir issues ou sugerir melhorias!
```