from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd

from utils.tabelas import (
    gerar_tabela_areas_principais,
    gerar_tabela_aferecao_indireta,
    generate_financial_table,
    gerar_tabela_inss_detalhado
)
from utils.calculos import calcular_inss

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

@app.route('/')
def index():
    # Gera a lista de UFs dinamicamente a partir dos dados percentuais
    from data.dados_percentuais import dados_percentuais
    ufs = sorted(dados_percentuais.keys())
    return render_template('index.html', ufs=ufs)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # 1) Extrair dados do formulário principal
        identificacoes = request.form.getlist('identificacao[]')
        categorias = request.form.getlist('categoria[]')
        materiais = request.form.getlist('material[]')
        tipo_areas = request.form.getlist('tipoArea[]')
        areas_totais = request.form.getlist('areaTotal[]')
        cubs = request.form.getlist('CUB[]')
        ufs = request.form.getlist('uf[]')
        concretos = request.form.getlist('concretoUsinado[]')
        destinacoes = request.form.getlist('destinacao[]')
        valores_notas_fiscais = request.form.getlist('valorNotasFiscais[]')
        areas_aferidas = request.form.getlist('areaAferida[]')

        # 2) Ler os valores de mês de início e mês de fim (que vêm como listas)
        mes_inicios = request.form.getlist('mesInicio[]')  # lista de strings no formato YYYY-MM
        mes_fins = request.form.getlist('mesFim[]')        # idem

        # 3) Se desejar usar um único range [start_date, end_date] para toda a obra,
        #    podemos usar o mínimo de mes_inicios e o máximo de mes_fins:
        if mes_inicios:
            start_date = min(mes_inicios)  # earliest
        else:
            start_date = '2022-10'  # fallback

        if mes_fins:
            end_date = max(mes_fins)  # latest
        else:
            end_date = '2023-09'  # fallback

        # 4) Ler também outros campos (fatorAjuste, mesesExecucao), se existirem num <input> fora do loop
        fator_ajuste_str = request.form.get('fatorAjuste', '50')
        meses_execucao_str = request.form.get('mesesExecucao', '12')

        fator_de_ajuste = float(fator_ajuste_str) / 100.0
        meses_execucao = int(meses_execucao_str)

        # 5) Montar lista de dicionários para gerar_tabela_areas_principais
        dados = []
        for i in range(len(identificacoes)):
            try:
                dado = {
                    'Identificação': identificacoes[i],
                    'Categoria': categorias[i],
                    'Material': materiais[i],
                    'Tipo area': tipo_areas[i],
                    'Área Total': float(areas_totais[i]),
                    'CUB': float(cubs[i]),
                    'UF': ufs[i],
                    'Concreto usinado': concretos[i],
                    'destinacao': destinacoes[i],
                    'valor_notas_fiscais': float(valores_notas_fiscais[i]),
                    'Área Total Aferida para Cálculo': float(areas_aferidas[i])
                }
                dados.append(dado)
            except ValueError as e:
                flash(f'Erro na conversão dos dados: {str(e)}', 'danger')
                return redirect(url_for('index'))

        # 6) Gerar tabela de áreas
        tabela_areas = gerar_tabela_areas_principais(dados)
        tabela_areas_html = tabela_areas.to_html(classes='table table-striped', index=False)

        # 7) Calcular RMT total
        if 'RMT' in tabela_areas.columns:
            rmt_total = tabela_areas['RMT'].sum()
        else:
            rmt_total = 0.0

        # 8) Gera tabela de aferição indireta
        tabela_afericao = gerar_tabela_aferecao_indireta(rmt_total, fator_de_ajuste, meses_execucao)
        tabela_afericao_html = tabela_afericao.to_html(classes='table table-striped', index=False)

        # 9) Extrair RMT ajustado (caso queira usá-lo para a Tabela Financeira)
        try:
            rmt_ajustado_str = tabela_afericao.iloc[2, 1]  # busca "RMT PARA O Fator de ajuste" na tabela
            # Dependendo do formato, será necessário tratar a string adequadamente:
            rmt_ajustado = float(
                rmt_ajustado_str
                .replace('R$', '')
                .replace('.', '')
                .replace(',', '.')
            )
        except Exception as ex:
            print("Erro ao extrair RMT ajustado:", ex)
            rmt_ajustado = rmt_total * fator_de_ajuste

        # 10) Gera Tabela Financeira usando as datas do formulário
        tabela_financeira = generate_financial_table(start_date, end_date, rmt_ajustado)
        tabela_financeira_html = tabela_financeira.to_html(classes='table table-striped', index=False)

        # 11) Calcular INSS devido
        from utils.calculos import calcular_inss_economizado, calcular_inss
        inss_devido = calcular_inss(rmt_total)

        # 12) Determinar percentual de redução (exemplo simples)
        reducao_percentual = 0
        if categorias and categorias[0] == "Reforma":
            reducao_percentual = 65
        elif categorias and categorias[0] == "Demolição":
            reducao_percentual = 90

        # 13) Gera a tabela detalhada de INSS
        tabela_inss = gerar_tabela_inss_detalhado(rmt_total, reducao_percentual, honorarios_percentual=30)
        tabela_inss_html = tabela_inss.to_html(classes='table table-striped', index=False)

        return render_template('resultado.html',
                               tabela_areas_html=tabela_areas_html,
                               tabela_afericao_html=tabela_afericao_html,
                               tabela_financeira_html=tabela_financeira_html,
                               tabela_inss_html=tabela_inss_html,
                               rmt_total=rmt_total,
                               fator_de_ajuste=fator_de_ajuste,
                               meses_execucao=meses_execucao)
    except Exception as e:
        print("Exceção em submit:", e)
        flash(f'Ocorreu um erro inesperado: {str(e)}', 'danger')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
