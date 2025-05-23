import pandas as pd
import sys
import os

# Se for erro de não existir planilhas o retorno vai ser esse:
STATUS_DATA_UNAVAILABLE = 4
# Caso o erro for a planilha, que é invalida por algum motivo, o retorno vai ser esse:
STATUS_INVALID_FILE = 5


def _read(file, year, month):
    try:
        # Adicionamos essa condição devido ao cabeçalho adicionando a essa planilha específica
        if "indenizatorias" in file:
            data = pd.read_csv(file, skiprows=2).to_numpy()
        else:
            data = pd.read_csv(file).to_numpy()
        # Compara o tamanho da planilha para ver se não está vazia.
    except Exception as excep:
        print(f"Erro lendo as planilhas: {excep}", file=sys.stderr)
        sys.exit(STATUS_INVALID_FILE)
        
    if len(data) ==0:
            sys.stderr.write(f"Não existe planilhas para {month}/{year}.")
            sys.exit(STATUS_DATA_UNAVAILABLE)
    return data


def load(file_names, year, month):
    """Carrega os arquivos passados como parâmetros.
    
     :param file_names: slice contendo os arquivos baixados pelo coletor.
    Os nomes dos arquivos devem seguir uma convenção e começar com 
    Membros ativos-contracheque e Membros ativos-Verbas Indenizatorias
     :param year e month: usados para fazer a validação na planilha de controle de dados
     :return um objeto Data() pronto para operar com os arquivos
    """

    contracheque = _read([c for c in file_names if "contracheque" in c][0], year, month)
    if int(year) == 2018 or (int(year) == 2019 and int(month) < 7):
        # Não existe dados exclusivos de verbas indenizatórias nesse período de tempo.
        return Data_2018(contracheque, year, month)

    indenizatorias = _read([i for i in file_names if "indenizatorias" in i][0], year, month)

    return Data(contracheque, indenizatorias, year, month)


class Data:
    def __init__(self, contracheque, indenizatorias, year, month):
        self.year = year
        self.month = month
        self.contracheque = contracheque
        self.indenizatorias = indenizatorias

    def validate(self, output_path):
        """
         Validação inicial dos arquivos passados como parâmetros.
        Aborta a execução do script em caso de erro.
         Caso o validade fique pare o script na leitura da planilha 
        de controle de dados dara um erro retornando o codigo de erro 4,
        esse codigo significa que não existe dados para a data pedida.
        """

        if not (
            os.path.isfile(
                output_path + f"/membros-ativos-contracheque-{self.month}-{self.year}.csv"
            )
            or os.path.isfile(
                output_path + f"/membros-ativos-verbas-indenizatorias-{self.month}-{self.year}.csv"
            )
        ):
            sys.stderr.write(f"Não existe planilhas para {self.month}/{self.year}.")
            sys.exit(STATUS_DATA_UNAVAILABLE)


class Data_2018:
    def __init__(self, contracheque, year, month):
        self.year = year
        self.month = month
        self.contracheque = contracheque

    def validate(self, output_path):
        """
         Essa validação só leva em consideração o arquivo Membros Ativos-contracheque,
         pois até Julho de 2019 o MPSE não disponibiliza o arquivo Verbas Indenizatórias
        """

        if not (
            os.path.isfile(
                output_path + f"/membros-ativos-contracheque-{self.month}-{self.year}.csv"
            )
        ):
            sys.stderr.write(f"Não existe planilha para {self.month}/{self.year}.")
            sys.exit(STATUS_DATA_UNAVAILABLE)
