import yfinance as yf
import json
from datetime import datetime
import pytz

def atualizar_ifix():
    try:
        print("Buscando cotação do IFIX via Yahoo Finance...")
        # O ticker do IFIX no Yahoo Finance é ^IFIX
        ifix = yf.Ticker("^IFIX")
        
        # Pega o último preço de fechamento/atual
        dados_historicos = ifix.history(period="1d")
        
        if dados_historicos.empty:
            raise ValueError("Não foi possível obter os dados do Yahoo Finance. O retorno veio vazio.")
            
        valor_float = float(dados_historicos['Close'].iloc[-1])
        
        # Arredonda para 2 casas decimais (padrão de moeda)
        valor_float = round(valor_float, 2)
        
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
