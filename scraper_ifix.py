import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz
import os

def atualizar_ifix():
    # URL direta do Google Finance para o IFIX
    url = 'https://www.google.com/finance/quote/IFIX:INDEXBVMF'
    
    try:
        print("Buscando cotação do IFIX via Google Finance...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # A classe 'YMlKec fxKbKc' é o padrão fixo do Google Finance para o preço principal
        valor_str = soup.find(class_='YMlKec fxKbKc').text
        
        # O Google Finance em inglês retorna algo como "3,913.08"
        # Removemos a vírgula do milhar e convertemos para float
        valor_float = float(valor_str.replace(',', ''))
        
        # Pega a data de hoje no formato YYYY-MM-DD
        tz = pytz.timezone('America/Sao_Paulo')
        data_hoje = datetime.now(tz).strftime('%Y-%m-%d')
        
        # 1. Tenta carregar o histórico existente
        historico = {}
        if os.path.exists('ifix_historico.json'):
            with open('ifix_historico.json', 'r') as f:
                # Carrega o JSON antigo para a memória
                historico = json.load(f)
        
        # 2. Adiciona ou atualiza o valor de hoje no dicionário
        historico[data_hoje] = valor_float
        
        # 3. Salva tudo de volta no arquivo (agora com indentação para ficar legível)
        with open('ifix_historico.json', 'w') as f:
            json.dump(historico, f, indent=4)
            
        print(f"Sucesso! IFIX ({valor_float}) adicionado em ifix_historico.json na data {data_hoje}")
        
    except Exception as e:
        print(f"Erro ao buscar o IFIX: {e}")
        exit(1)

if __name__ == "__main__":
    atualizar_ifix()
