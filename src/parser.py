# coding: utf8
import sys
import os
from coleta import coleta_pb2 as Coleta

CONTRACHEQUE_2018 = "contracheque"
CONTRACHEQUE_2019_DEPOIS = "contracheque1"
INDENIZACOES = "indenizações"

HEADERS = {
    CONTRACHEQUE_2018: {
        "Remuneração do Cargo Efetivo": 6,
        "Outras Verbas Remuneratórias, Legais ou Judiciais": 7,
        "Função de Confiança ou Cargo em Comissão": 8,
        "Gratificação Natalina": 9,
        "Férias (1/3 constitucional)": 10,
        "Abono de Permanência": 11,
        "Contribuição Previdenciária": 13,
        "Imposto de Renda": 14,
        "Retenção por Teto Constitucional": 15,
        "Verbas Indenizatórias": 18,
        "Outras Remunerações Retroativas / Temporárias": 19,
    },
    CONTRACHEQUE_2019_DEPOIS: {
        "Remuneração do Cargo Efetivo": 6,
        "Outras Verbas Remuneratórias, Legais ou Judiciais": 7,
        "Função de Confiança ou Cargo em Comissão": 8,
        "Gratificação Natalina": 9,
        "Férias (1/3 constitucional)": 10,
        "Abono de Permanência": 11,
        "Contribuição Previdenciária": 15,
        "Imposto de Renda": 16,
        "Retenção por Teto Constitucional": 17,
    },
    INDENIZACOES: {
        "Auxílio":6,
        "Auxílio Creche":7,
        "Auxílio Saúde":8,
        "Auxílio Transporte":9,
        "Verbas Rescisórias":10,
        "Licença-Prêmio":11,
        "Abono Pecuniário":12,
        "Outras Verbas Indenizatórias":13,
        "Adicional de Insalubridade/Periculosidade":14,
        "Gratificação Exercício Cumulativo":15,
        "Gratificação Exercício Natureza Especial":16,
        "Substituição":17,
        "Outras Remunerações Temporárias":18,
    },
}


def parse_employees(fn, chave_coleta, mes, ano):
    employees = {}
    counter = 1
    for row in fn:
        if int(ano) == 2018 or (int(ano) == 2019 and int(mes) < 7):
            funcao = row[5]
            local_trabalho = row[4]
        else:
            funcao = row[4]
            local_trabalho = row[5]
      
        matricula = str(row[2])
        name = row[3]
        if not is_nan(name) and name != "0":
            membro = Coleta.ContraCheque()
            membro.id_contra_cheque = chave_coleta + "/" + str(counter)
            membro.chave_coleta = chave_coleta
            membro.nome = name
            membro.matricula = matricula
            membro.funcao = funcao
            membro.local_trabalho = local_trabalho
            membro.tipo = Coleta.ContraCheque.Tipo.Value("MEMBRO")
            membro.ativo = True
            if int(ano) == 2018:
                membro.remuneracoes.CopyFrom(
                    cria_remuneracao(row, CONTRACHEQUE_2018)
                )
            else:
                membro.remuneracoes.CopyFrom(
                    cria_remuneracao(row, CONTRACHEQUE_2019_DEPOIS)
                )
            employees[name] = membro
            counter += 1
    return employees


def cria_remuneracao(row, categoria):
    remu_array = Coleta.Remuneracoes()
    items = list(HEADERS[categoria].items())
    for i in range(len(items)):
        key, value = items[i][0], items[i][1]
        remuneracao = Coleta.Remuneracao()
        remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
        if categoria == INDENIZACOES:
            remuneracao.categoria = categoria
        else:
            remuneracao.categoria = "contracheque"
        remuneracao.item = key
        remuneracao.valor = format_value(row[value])
        if categoria == CONTRACHEQUE_2018:
            if value == 6:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            elif value in [13, 14, 15]:
                remuneracao.valor = remuneracao.valor * (-1)
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
            elif value in [7, 8, 9, 10, 11, 18, 19]:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
        elif categoria == CONTRACHEQUE_2019_DEPOIS:
            if value == 6:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            elif value in [15, 16, 17]:
                remuneracao.valor = remuneracao.valor * (-1)
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
            elif value in [7, 8, 9, 10, 11]:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
        else:
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")

        remu_array.remuneracao.append(remuneracao)
    return remu_array


def update_employees(fn, employees, categoria):
    for row in fn:
        name = row[3]
        if name in employees.keys():
            emp = employees[name]
            remu = cria_remuneracao(row, categoria)
            emp.remuneracoes.MergeFrom(remu)
            employees[name] = emp
    return employees


def is_nan(string):
    return string != string


def parse(data, chave_coleta, mes, ano):
    employees = {}
    folha = Coleta.FolhaDePagamento()
    if int(ano) == 2018 or (int(ano) == 2019 and int(mes) < 7):
        try:
            employees.update(parse_employees(data.contracheque, chave_coleta, mes, ano))

        except KeyError as e:
            sys.stderr.write(
                "Registro inválido ao processar contracheque: {}".format(e)
            )
            os._exit(1)
    else:
        try:
            employees.update(parse_employees(data.contracheque, chave_coleta, mes, ano))
            update_employees(data.indenizatorias, employees, INDENIZACOES)

        except KeyError as e:
            sys.stderr.write(
                "Registro inválido ao processar contracheque ou indenizações: {}".format(e)
            )
            os._exit(1)
    for i in employees.values():
        folha.contra_cheque.append(i)
    return folha


def format_value(element):
    # A value was found with incorrect formatting. (3,045.99 instead of 3045.99)
    if is_nan(element):
        return 0.0
    if type(element) == str:
        if "." in element and "," in element:
            element = element.replace(".", "").replace(",", ".")
        elif "," in element:
            element = element.replace(",", ".")
        elif "-" in element:
            element = 0.0

    return float(element)
