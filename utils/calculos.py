"""
Módulo de cálculos para a aplicação de redução do INSS sobre obras de construção civil.

Referências:
- Instrução Normativa RFB nº 971, de 2009, disponível em:
  http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=15937#:~:text=IN%20RFB%20n%C2%BA%20971%2F2009&text=Disp%C3%B5e%20sobre%20normas%20gerais%20de,Federal%20do%20Brasil%20(RFB).
Data de extração dos números: 28/03/2023.

Observação:
Os percentuais, faixas e metodologias foram extraídos com base neste documento. Caso ocorram alterações na
legislação ou novas orientações técnicas sejam publicadas, as funções devem ser adaptadas para refletir os novos
parâmetros e variáveis, garantindo que os cálculos permaneçam corretos conforme a fonte oficial.
"""

from data.dados_percentuais import dados_percentuais

def calcular_vau(cub):
    """
    Calcula o Valor Atualizado Unitário (VAU) aplicando um ajuste de 1% ao CUB.
    
    Args:
        cub (float): Custo Unitário Básico do mês anterior à aferição.
    
    Returns:
        float: Valor Atualizado Unitário (VAU).
    """
    ajuste_percentual = 1.01  # Acréscimo de 1%
    vau = cub * ajuste_percentual
    return vau

def calcular_percentual_equivalencia(area_total, tipo_destinacao):
    """
    Retorna o percentual de equivalência com base na área total e na destinação da obra,
    conforme os dados disponíveis nos PDFs e sites consultados.
    
    Para alguns tipos de destinação (Galpão Industrial, Casa Popular, Conjunto Habitacional Popular)
    o percentual é fixo, enquanto para outros há faixas de área.

    Args:
        area_total (float): Área total da obra (m²).
        tipo_destinacao (str): Tipo de destinação da obra.
    
    Returns:
        int: Percentual de equivalência.
    """
    # Destinações com percentual fixo
    fixed_values = {
        "Galpão Industrial": 95,
        "Casa Popular": 98,
        "Conjunto Habitacional Popular": 98
    }
    if tipo_destinacao in fixed_values:
        return fixed_values[tipo_destinacao]

    # Para as demais destinações, utiliza-se a segmentação por área
    equivalencias = {
        "Residencial Unifamiliar": [(1000, 89), (float('inf'), 85)],
        "Residencial Multifamiliar": [(1000, 90), (float('inf'), 86)],
        "Comercial Salas e Lojas": [(3000, 86), (float('inf'), 83)],
        "Edifício de Garagens": [(3000, 86), (float('inf'), 83)]
    }
    percentuais = equivalencias.get(tipo_destinacao, [])
    for limite, percentual in percentuais:
        if area_total <= limite:
            return percentual
    return 0

def calcular_percentual_mao_de_obra(tipo_obra, material):
    """
    Retorna o percentual de mão de obra aplicável com base no tipo de obra e material.
    Esses percentuais são definidos conforme os dados das tabelas consultadas.

    Args:
        tipo_obra (str): Tipo de obra (ex.: "Residencial Unifamiliar").
        material (str): Material predominante da obra (ex.: "Alvenaria", "Madeira", "Mista").
    
    Returns:
        int: Percentual de mão de obra.
    """
    percentuais = {
        "Residencial Unifamiliar": {"Alvenaria": 20, "Madeira": 15, "Mista": 15},
        "Residencial Multifamiliar": {"Alvenaria": 20, "Madeira": 15, "Mista": 15},
        "Comercial Salas e Lojas": {"Alvenaria": 20, "Madeira": 15, "Mista": 15},
        "Edifício de Garagens": {"Alvenaria": 20, "Madeira": 15, "Mista": 15},
        "Galpão Industrial": {"Alvenaria": 20, "Madeira": 15, "Mista": 15},
        "Casa Popular": {"Alvenaria": 12, "Madeira": 7, "Mista": 7},
        "Conjunto Habitacional Popular": {"Alvenaria": 12, "Madeira": 7, "Mista": 7}
    }
    return percentuais.get(tipo_obra, {}).get(material, 0)

def calcular_percentual_por_categoria(categoria):
    """
    Retorna o percentual aplicável com base na categoria da obra.
    
    Args:
        categoria (str): Categoria da obra (ex.: "Obra Nova", "Reforma").
    
    Returns:
        int: Percentual para a categoria.
    """
    percentuais = {
        "Obra Nova": 100,  # 100% (sem redução)
        "Acréscimo": 100,  # 100% (sem redução)
        "Reforma": 35,     # 35% (redução de 65%)
        "Demolição": 10,   # 10% (redução de 90%)
        "Edifício de Garagens": 80  # 80% (redução de 20%)
    }
    return percentuais.get(categoria, 100)

def calcular_fator_social(area_total):
    """
    Retorna o fator social aplicável com base na área total da obra.
    
    Conforme as tabelas encontradas:
        - Até 100 m²: 20
        - 101 a 200 m²: 40
        - 201 a 300 m²: 55
        - 301 a 400 m²: 70
        - Acima de 400 m²: 90
    
    Args:
        area_total (float): Área total da obra (m²).
    
    Returns:
        int: Fator social.
    """
    if area_total <= 100:
        return 20
    elif area_total <= 200:
        return 40
    elif area_total <= 300:
        return 55
    elif area_total <= 400:
        return 70
    else:
        return 90

def calcular_percentual_nf(dado):
    """
    Calcula o percentual aplicável com base no uso de pré-moldados ou pré-fabricados,
    considerando o valor das notas fiscais em relação ao custo da obra por destinação.

    Args:
        dado (dict): Dicionário com as chaves 'valor_notas_fiscais' e 'Custo da Obra por Destinação'.
    
    Returns:
        float: Percentual aplicável para o cálculo da RMT.
    """
    if 'valor_notas_fiscais' not in dado or 'Custo da Obra por Destinação' not in dado:
        # Se não houver informações suficientes, considera-se que não há redução
        return 100.0
    
    valor_notas_fiscais = dado['valor_notas_fiscais']
    custo_da_obra_destinacao = dado['Custo da Obra por Destinação']
    
    # Calcula a proporção do valor das notas fiscais em relação ao custo da obra
    proporcao_nf = (valor_notas_fiscais / custo_da_obra_destinacao) * 100
    
    # Se a proporção for igual ou superior a 40%, aplica redução (soma de 70% de desconto)
    if proporcao_nf >= 40:
        return 30.0  # Aplica 30% do valor original
    else:
        return 100.0  # Sem redução

def calcular_rmt(area_total, cub, material):
    """
    Calcula a Remuneração da Mão de Obra Total (RMT) utilizando a segmentação da área construída,
    conforme as tabelas dos documentos consultados.
    
    Para construções de Alvenaria:
        - 0 a 100 m²: 4%
        - 101 a 200 m²: 8%
        - 201 a 300 m²: 14%
        - Acima de 300 m²: 20%
    
    Para construções em Madeira ou Mistas:
        - 0 a 100 m²: 2%
        - 101 a 200 m²: 5%
        - 201 a 300 m²: 11%
        - Acima de 300 m²: 15%
    
    Args:
        area_total (float): Área total construída (m²).
        cub (float): Custo Unitário Básico.
        material (str): Material predominante ("Alvenaria", "Madeira" ou "Mista").
    
    Returns:
        float: Valor da Remuneração da Mão de Obra Total (RMT).
    """
    material_lower = material.lower()
    if material_lower == "alvenaria":
        p1, p2, p3, p4 = 0.04, 0.08, 0.14, 0.20
    else:  # para "madeira" ou "mista"
        p1, p2, p3, p4 = 0.02, 0.05, 0.11, 0.15

    # Cálculo por faixas de área
    area1 = min(area_total, 100)
    area2 = min(max(area_total - 100, 0), 100)
    area3 = min(max(area_total - 200, 0), 100)
    area4 = max(area_total - 300, 0)
    
    rmt = (area1 * cub * p1) + (area2 * cub * p2) + (area3 * cub * p3) + (area4 * cub * p4)
    return rmt

def calcular_inss(rmt):
    """
    Calcula o valor da contribuição do INSS sobre a Remuneração da Mão de Obra Total (RMT).
    
    Atualmente, a alíquota aplicada é de 36,8%.
    
    Args:
        rmt (float): Remuneração da Mão de Obra Total.
    
    Returns:
        float: Valor da contribuição do INSS.
    """
    aliquota = 0.368
    return rmt * aliquota

def calcular_inss_economizado(rmt, reducao_percentual):
    """
    Calcula o INSS devido, o INSS a pagar (após aplicação de redução) e a economia gerada.
    
    Args:
        rmt (float): Remuneração da Mão de Obra Total.
        reducao_percentual (float): Percentual de redução a ser aplicado (ex.: 65 para 65%).
    
    Returns:
        tuple: (inss_devido, inss_a_pagar, economia) onde:
            - inss_devido (float): Valor do INSS sem redução.
            - inss_a_pagar (float): Valor do INSS a ser pago após a redução.
            - economia (float): Economia gerada (diferença entre o INSS devido e o INSS a pagar).
    """
    aliquota = 0.368  # 36,8%
    inss_devido = rmt * aliquota
    base_reduzida = rmt * ((100 - reducao_percentual) / 100)
    inss_a_pagar = base_reduzida * aliquota
    economia = inss_devido - inss_a_pagar
    return inss_devido, inss_a_pagar, economia
