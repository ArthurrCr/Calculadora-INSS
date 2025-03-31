from utils.calculos import (
    calcular_vau, 
    calcular_percentual_equivalencia, 
    calcular_fator_social, 
    calcular_percentual_mao_de_obra, 
    calcular_percentual_por_categoria, 
    calcular_percentual_nf,
    calcular_inss_economizado
)
from data.dados_percentuais import dados_percentuais
import pandas as pd
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

def format_currency(value):
    """
    Formata um valor numérico no padrão de moeda brasileira.
    Exemplo: 1245.50 -> R$ 1.245,50
    """
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_areas_totais(dados):
    """
    Agrupa os dados por destinação, acumulando a área aferida e calculando o VAU para cada grupo.
    
    Args:
        dados (list): Lista de dicionários com os dados de cada área.
    
    Returns:
        dict: Dicionário com chave = destinação, e valor contendo a área total acumulada,
              o VAU (calculado a partir do CUB) e os itens correspondentes.
    """
    total_por_destinacao = {}
    for dado in dados:
        dest = dado['destinacao']
        if dest not in total_por_destinacao:
            # Considera o CUB do primeiro item do grupo para cálculo do VAU
            total_por_destinacao[dest] = {
                'total_area': 0,
                'VAU': calcular_vau(dado['CUB']),
                'items': []
            }
        total_por_destinacao[dest]['total_area'] += dado['Área Total Aferida para Cálculo']
        total_por_destinacao[dest]['items'].append(dado)
    
    return total_por_destinacao

def gerar_tabela_areas_principais(dados):
    """
    Gera uma tabela (DataFrame) contendo os principais dados e cálculos das áreas aferidas,
    utilizando as funções de conversão e os percentuais extraídos dos documentos e sites consultados.
    
    Args:
        dados (list): Lista de dicionários com os dados de cada área.
    
    Returns:
        DataFrame: Tabela com os resultados dos cálculos.
    """
    resultados = []
    total_por_destinacao = calcular_areas_totais(dados)
    
    for dest, info in total_por_destinacao.items():
        area_total_em_afericao = info['total_area']
        # Calcula o percentual de equivalência de acordo com a área e destinação
        percentual_equivalencia = calcular_percentual_equivalencia(area_total_em_afericao, dest)
        # Fator social aplicado conforme a área total
        fator_social = calcular_fator_social(area_total_em_afericao)
        # Usa o VAU calculado para o grupo
        vau = info['VAU']

        for dado in info['items']:
            tipo_area = dado.get('Tipo area', 'Principal')
            redutor = 1  # Sem redução para área principal por padrão

            # Se a área for complementar, aplica o redutor conforme a cobertura
            if tipo_area == 'Complementar':
                redutor = 0.50 if dado.get('Cobertura', 'Coberta') == 'Coberta' else 0.25
                area_total_para_calculo = dado['Área Total Aferida para Cálculo'] * redutor
            else:
                # Para área principal, aplica o percentual de equivalência
                area_total_para_calculo = dado['Área Total Aferida para Cálculo'] * (percentual_equivalencia / 100)

            # Calcula o custo da obra para a destinação, utilizando o VAU
            custo_da_obra = area_total_para_calculo * vau

            # Percentual de mão de obra de acordo com o tipo de obra (destinação) e material
            percentual_mao_obra = calcular_percentual_mao_de_obra(dado['destinacao'], dado['Material'])
            
            # Para a categoria, define um percentual reduzido para Reforma ou outro tipo, conforme os dados
            categoria = dado['Categoria']
            percentual_categoria_remu = 100 if categoria in ['Obra Nova', 'Acréscimo'] else 35 if categoria == 'Reforma' else 0
            
            # Percentual relacionado ao uso de pré-moldados ou pré-fabricados
            percentual_nf = calcular_percentual_nf(dado)
            # Percentual de cálculo conforme a categoria (pode ser diferente do utilizado para crédito)
            percentual_categoria = calcular_percentual_por_categoria(categoria)
            
            # Cálculo da Remuneração da Mão de Obra Total (RMT)
            rmt_valor = custo_da_obra * (percentual_categoria / 100) * (fator_social / 100) \
                        * (percentual_mao_obra / 100) * (percentual_nf / 100)
            
            # Percentual de uso por UF conforme tabela de dados
            percentual_uso_uf = dados_percentuais.get(dado['UF'], {}).get(dado['destinacao'], 0)
            # Percentual de ajuste para Concreto Usinado (se aplicável)
            percentual_ajuste = 5 if dado.get('Concreto usinado', 'Não') == 'Sim' else 0

            # Crédito de remuneração adicional
            credito_remuneracao = custo_da_obra * (percentual_uso_uf / 100) \
                                  * (percentual_categoria_remu / 100) * (percentual_ajuste / 100)
            rmt_valor += credito_remuneracao

            resultados.append({
                'Identificação da Área': dado['Identificação'],
                'Categoria': categoria,
                'Material': dado['Material'],
                'Tipo de Área': tipo_area,
                'Redução de Área (%)': f"{redutor * 100}%" if tipo_area == 'Complementar' else "N/A",
                'Área Total': f"{dado.get('Área Total', 'N/A')} m²",
                'Área Total Aferida': f"{dado.get('Área Total Aferida', 'N/A')} m²",
                'Área Total Aferida para Cálculo': f"{dado['Área Total Aferida para Cálculo']} m²",
                'Área em Aferição': f"{dado.get('Área em Aferição', 'N/A')} m²",
                'Área Total em Aferição': f"{area_total_em_afericao} m²",
                'Percentual de Equivalência': f"{percentual_equivalencia}%" if tipo_area == 'Principal' else "N/A",
                'Área Total para Cálculo': f"{area_total_para_calculo:.2f} m²",
                'VAU': vau,
                'Custo da Obra por Destinação': format_currency(custo_da_obra),
                'Percentual de Mão de Obra': f"{percentual_mao_obra}%",
                'Percentual de Calculo por Categoria de obra': f"{percentual_categoria}%",
                'Percentual de NF': f"{percentual_nf}%",
                'Fator Social (%)': f"{fator_social}%",
                'Percentual de uso por UF': f"{percentual_uso_uf:.2f}%",
                'Percentual de aplicação do abatimento por categoria': f"{percentual_categoria_remu}%",
                'Percentual de ajuste': f"{percentual_ajuste}%",
                'Crédito de remuneração': format_currency(credito_remuneracao),
                'RMT': rmt_valor
            })

    return pd.DataFrame(resultados)

def gerar_tabela_aferecao_indireta(rmt_total, fator_de_ajuste, meses_execucao):
    """
    Gera uma tabela (DataFrame) com a aferição indireta, calculando o RMT ajustado e a remuneração mensal mínima.
    
    Args:
        rmt_total (float): Remuneração da Mão de Obra Total.
        fator_de_ajuste (float): Fator de ajuste a ser aplicado.
        meses_execucao (int): Número de meses de execução da obra.
    
    Returns:
        DataFrame: Tabela com os valores calculados.
    """
    rmt_ajustado = rmt_total * fator_de_ajuste
    remuneracao_mensal = rmt_ajustado / meses_execucao if meses_execucao > 0 else 0

    data = {
        'Aferição indireta': [
            'RMT TOTAL', 
            'Fator de Ajuste', 
            'RMT PARA O Fator de ajuste', 
            'REMUNERAÇÃO MENSAL (mínima)'
        ],
        'Valor': [
            format_currency(rmt_total), 
            f"{fator_de_ajuste * 100:.0f}%", 
            format_currency(rmt_ajustado), 
            format_currency(remuneracao_mensal)
        ]
    }

    return pd.DataFrame(data)

def fetch_selic_annualized(start_date, end_date):
    """
    Busca os dados da taxa SELIC (anualizada) no período informado, utilizando a API do Banco Central.
    
    Args:
        start_date (str): Data inicial no formato DD/MM/YYYY.
        end_date (str): Data final no formato DD/MM/YYYY.
    
    Returns:
        dict: Dicionário com chave no formato "YYYY-mm" e valor da taxa SELIC.
    """
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.4189/dados?formato=json&dataInicial={start_date}&dataFinal={end_date}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch data")
        return {}
    
    data = response.json()
    selic_data = {}
    for item in data:
        date_key = datetime.strptime(item['data'], "%d/%m/%Y").strftime("%Y-%m")
        selic_data[date_key] = float(item['valor'])

    return selic_data

def generate_financial_table(start_date, end_date, remuneration):
    """
    Gera uma tabela financeira com base na remuneração, aplicando os ajustes da SELIC e outros encargos.
    
    Para cada mês do período, são calculados:
        - Valor Atualizado (remuneração ajustada pela SELIC)
        - CPP (20% do valor atualizado)
        - Multa (20% sobre o CPP)
        - Juros de Mora (calculado com taxa diária para 30 dias de atraso)
        - MAED Mínima (acréscimo percentual, que aumenta 2 pontos percentuais por mês, limitado a 20%)
        - Total (soma dos encargos)
    
    Args:
        start_date (str): Data inicial no formato "YYYY-MM".
        end_date (str): Data final no formato "YYYY-MM".
        remuneration (float): Valor da remuneração base.
    
    Returns:
        DataFrame: Tabela financeira com os resultados.
    """
    # Ajusta a data de início para buscar um mês antes
    start = datetime.strptime(start_date, "%Y-%m") - relativedelta(months=1)
    end_dt = datetime.strptime(end_date, "%Y-%m")
    selic_rates = fetch_selic_annualized(start.strftime("%d/%m/%Y"), end_dt.strftime("%d/%m/%Y"))
    
    # Ajusta o mapeamento das taxas SELIC para o mês seguinte
    adjusted_selic_rates = {}
    previous_rate = 0
    for month in sorted(selic_rates.keys()):
        adjusted_selic_rates[month] = previous_rate
        previous_rate = selic_rates[month]
    
    results = []
    totals = {'Remuneração': 0, 'Atualizado': 0, 'Total': 0}
    current_date = datetime.strptime(start_date, "%Y-%m")  # Inicia na data original
    cont_maed = 0
    while current_date <= end_dt:
        if cont_maed < 20:
            cont_maed += 2
        month_key = current_date.strftime("%Y-%m")
        selic_rate = adjusted_selic_rates.get(month_key, 0)
        valor_atualizado = remuneration * (1 + selic_rate / 100)
        cpp = valor_atualizado * 0.20
        multa = cpp * 0.20

        # Juros de mora: taxa diária de 0,0333% para 30 dias de atraso
        juros_mora = (0.0333 / 100) * valor_atualizado * 30

        maed_minima = valor_atualizado * (cont_maed / 100)
        
        total = cpp + multa + juros_mora + maed_minima

        results.append({
            "Mês/Ano": month_key,
            "Remuneração": format_currency(remuneration),
            "ICM": f"{selic_rate:.2f}%",
            "Valor Atualizado": format_currency(valor_atualizado),
            "CPP - 20%": format_currency(cpp),
            "Multa - 20%": format_currency(multa),
            "Juros de MORA": format_currency(juros_mora),
            "MAED Mínima": format_currency(maed_minima),
            "Total": format_currency(total)
        })

        totals['Remuneração'] += remuneration
        totals['Atualizado'] += valor_atualizado
        current_date += relativedelta(months=1)

    # Linha de totais
    results.append({
        "Mês/Ano": "Total",
        "Remuneração": format_currency(totals['Remuneração']),
        "Valor Atualizado": format_currency(totals['Atualizado']),
        "Total": format_currency(sum([float(result['Total'].replace("R$ ", "").replace(".", "").replace(",", "."))
                                       for result in results if result["Mês/Ano"] != "Total"]))
    })

    return pd.DataFrame(results)

def gerar_tabela_inss_detalhado(rmt, reducao_percentual, honorarios_percentual=30):
    """
    Gera uma tabela detalhada (DataFrame) com valores de INSS Devido, INSS a Pagar,
    Economia Gerada, Honorários e Economia Real.
    
    Args:
        rmt (float): Remuneração da Mão de Obra Total.
        reducao_percentual (float): Percentual de redução a ser aplicado (ex.: 65 para 65%).
        honorarios_percentual (float): Percentual de honorários (ex.: 30 para 30%).
    
    Returns:
        DataFrame: Tabela com as colunas "Campo" e "Valor".
    """
    # Calcula INSS Devido, INSS a Pagar e Economia
    inss_devido, inss_a_pagar, economia_gerada = calcular_inss_economizado(rmt, reducao_percentual)
    
    # Calcula honorários (por exemplo, 30% da economia)
    honorarios = economia_gerada * (honorarios_percentual / 100.0)
    economia_real = economia_gerada - honorarios

    data = {
        "Campo": [
            "INSS Devido",
            "INSS a Pagar",
            "Economia Gerada",
            "Honorários",
            "A Receber",
            "ECONOMIA REAL"
        ],
        "Valor": [
            format_currency(inss_devido),
            format_currency(inss_a_pagar),
            format_currency(economia_gerada),
            f"{honorarios_percentual:.0f}%",
            format_currency(honorarios),
            format_currency(economia_real)
        ]
    }
    df = pd.DataFrame(data)
    return df
