from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import os, re, sys, time
import tse, pandas as pd, numpy as np

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
    return dados

# definir função para abrir o navegador
def abrir_navegador():

    # define chrome options
    CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'

    # set options
    chrome_options = Options()
    chrome_options.binary_location = CHROME_PATH

    # open invisible browser
    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options = chrome_options)

    # set implicit wait for page load
    browser.implicitly_wait(10)

    return browser

def main():

    # executar funções
    candidaturas = juntar_tse()
    browser = abrir_navegador()

    # focar no paraná
    candidaturas_pr = candidaturas[candidaturas['SG_UF'] == 'PR']
    amostra_pr = candidaturas_pr.sample(10, random_state=67)

    # vamos achar as documentos processuais?
    candidatos_pr = pd.read_csv(
        '../dados/consulta_cand_2016_PR.csv', **juntar_tse.kwargs
    )


    # puxar os números do protocolo da candidatura
    amostra = amostra_pr.merge(candidatos_pr, on='SQ_CANDIDATO')

    # criar link para raspar documentos
    documentos_link = [
        f'http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?' \
        f'nprot={nprot}&comboTribunal=pr' \
        for nprot in amostra['NR_PROTOCOLO_CANDIDATURA'].to_list()
    ]

    # baixar os arquivos
    raspador = tse.scraper(browser)

    for i in range(15, 0, -1):
        sys.stdout.write(f'aguardando: {i:02d}s\r')
        sys.stdout.flush()
        time.sleep(1)

    # baixar todos
    for i, url in enumerate(documentos_link):
        sys.stdout.write(f'raspando RCAND #{i+1:02d}         \r')
        sys.stdout.flush()
        raspador.decision(url=url, filename=f'../dados/decisão_{i}')

    # avisar conclusão
    sys.stdout.write(f'raspagem concluída.              \r')
    sys.stdout.flush()

    # fechar
    browser.quit()

# executar bloco principal
if __name__ == '__main__':
    main()
