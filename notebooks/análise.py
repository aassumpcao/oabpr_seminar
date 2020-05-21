# importar os pacotes necessários para fazer análise
import pandas as pd, numpy as np
import os, re
import requests
import zipfile

# importar meus pacotes personalizados
import tse
from tse import parser
import navegador_automatico

# definir função que baixa os dados
def baixar_tse():
    URL = 'http://agencia.tse.jus.br/estatistica/sead/odsele/motivo_cassacao/motivo_cassacao_2016.zip'
    r = requests.get(URL)
    with open('../dados/motivo_cassacao2016.zip', 'wb') as arquivo:
        arquivo.write(r.content)
    return 'Motivo(s) para Indeferimento 2016 baixado(s) com sucesso.'

# definir função de descomprime arquivo do tse
def unzip_tse():
    with zipfile.ZipFile('../dados/motivo_cassacao2016.zip', 'r') as zip:
        zip.extractall('../dados')
    return 'Arquivo(s) descomprimido(s) com sucesso.'

# definir função para juntar os dados do tse
def juntar_tse():

    regex = re.compile(r'motivo.*csv$')
    juntar_tse.kwargs = {
        'engine': 'python', 'encoding': 'latin1', 'sep':';', 'quoting': 1,
        'dtype': str
    }

    arquivos = os.listdir('../dados')
    arquivos = list(filter(regex.search, arquivos))
    arquivos = [
        os.path.join(os.path.realpath('../dados'), arquivo) \
        for arquivo in arquivos
    ]

    dados = pd.concat(
        [pd.read_csv(arquivo, **juntar_tse.kwargs) for arquivo in arquivos],
        ignore_index=True
    )

    dados = dados[dados['DS_MOTIVO_CASSACAO'].notna()]
    # dados.drop(dados.columns[-1], axis=1, inplace=True)

    print('Arquivo(s) juntado(s) com sucesso.')
    return dados

# executar funções
baixar_tse()
unzip_tse()
candidaturas = juntar_tse()

# mostrar os dados
candidaturas.sample(10)

# verificar os motivos para cassação
list(candidaturas['DS_MOTIVO_CASSACAO'].unique())

# focar no paraná
candidaturas_pr = candidaturas[candidaturas['SG_UF'] == 'PR']
amostra = candidaturas_pr.sample(10, random_state=67)
amostra.columns

# vamos achar as documentos processuais?
candidatos_pr = pd.read_csv(
    '../dados/consulta_cand_2016_PR.csv', **juntar_tse.kwargs
)

# puxar os números do protocolo da candidatura
amostra = amostra.merge(candidatos_pr, on='SQ_CANDIDATO')

# criar link para raspar documentos
documentos_link = [
    f'http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?' \
    f'nprot={nprot}&comboTribunal=pr' \
    for nprot in amostra['NR_PROTOCOLO_CANDIDATURA'].to_list()
]

# verifiquem o link vocês mesmos
print(documentos_link[1])

# # baixar os arquivos
# raspador = tse.scraper(navegador_automatico.browser)

# # baixar todos
# for i, url in enumerate(documentos_link):
#     raspador.decision(url=url, filename=f'decisão_{i+1}')

# # fechar
# navegador_automatico.browser.quit()

# construir path para os arquivos
decisões = [f'../dados/decisão_{i}.html' for i in range(0, 10)]

# transformar em tabela
sumário = parser(decisões[1])
sumário.parse_summary()
pd.DataFrame(sumário.parse_summary()).T

# criar banco de dados
sumários = pd.concat(
    [pd.DataFrame(parser(decisão).parse_summary()) for decisão in decisões],
    ignore_index=True
)

# onde estão estes processos? nas seguintes zonas eleitorais
sumários['district']
