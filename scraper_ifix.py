import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

def atualizar_ifix():
    url = 'https://statusinvest.com.br/indices/ifix'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print("Buscando cotação do IFIX...")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pega o valor na tela
        valor_str = soup.select_one('.value').text
        valor_float = float(valor_str.replace('.', '').replace(',', '.'))
        
        # Pega a hora atual de Brasília para o log
        tz = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        
        # Monta a estrutura do JSON
        dados = {
            "ifix": valor_float,
            "ultima_atualizacao": agora
        }
        
        # Salva no arquivo
        with open('ifix_atual.json', 'w') as f:
            json.dump(dados, f)
            
        print(f"Sucesso! IFIX ({valor_float}) salvo em ifix_atual.json")
        
    except Exception as e:
        print(f"Erro ao buscar o IFIX: {e}")
        # Retorna erro para o GitHub Actions falhar e te avisar se o site mudar
        exit(1)

if __name__ == "__main__":
    atualizar_ifix()
