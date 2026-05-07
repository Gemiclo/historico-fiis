import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

def atualizar_ifix():
    # URL direta do Google Finance para o IFIX
    url = 'https://www.google.com/finance/quote/IFIX:INDEXBVMF'
    
    try:
        print("Buscando cotação do IFIX via Google Finance...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # A classe 'YMlKec fxKbKc' é o padrão fixo do Google Finance para o preço principal
        valor_str = soup.find(class_='YMlKec fxKbKc').text
        
        # O Google Finance retorna algo como "3.913,32"
        valor_float = float(valor_str.replace('.', '').replace(',', '.'))
        
        tz = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        
        dados = {
            "ifix": valor_float,
            "ultima_atualizacao": agora
        }
        
        with open('ifix_atual.json', 'w') as f:
            json.dump(dados, f)
            
        print(f"Sucesso! IFIX ({valor_float}) salvo em ifix_atual.json")
        
    except Exception as e:
        print(f"Erro ao buscar o IFIX: {e}")
        exit(1)

if __name__ == "__main__":
    atualizar_ifix()
