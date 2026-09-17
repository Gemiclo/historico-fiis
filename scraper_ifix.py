import json
import os
import sys
from datetime import datetime

import pytz
import requests

# Fonte: BRAPI, endpoint legado de cotação. Substituiu o scraping do Google
# Finance em 17/09/2026: o Google migrou para /finance/beta, que manda cliente
# sem JavaScript para /finance/beta/unsupported e não tem mais a classe
# `YMlKec fxKbKc` onde o preço ficava. A BRAPI devolve só o valor do momento
# para o IFIX (sem histórico), então este script continua sendo quem acumula
# um ponto por dia em ifix_historico.json.
#
# O token NÃO fica no código: vem do secret BRAPI_TOKEN do GitHub Actions.
# Custo: 1 requisição por rodada, contra um teto mensal de centenas de milhares.
URL = 'https://brapi.dev/api/quote/IFIX'
ARQUIVO = 'ifix_historico.json'
FUSO = pytz.timezone('America/Sao_Paulo')


def buscar_ifix(token):
    resposta = requests.get(
        URL,
        headers={'Authorization': f'Bearer {token}'},
        timeout=30,
    )
    if resposta.status_code != 200:
        raise RuntimeError(
            f'BRAPI respondeu HTTP {resposta.status_code}: {resposta.text[:200]}')

    dados = resposta.json()
    resultados = dados.get('results') or []
    if not resultados:
        raise RuntimeError(f'BRAPI sem results para IFIX: {dados}')

    cotacao = resultados[0]
    valor = cotacao.get('regularMarketPrice')
    if not valor or valor <= 0:
        raise RuntimeError(f'BRAPI devolveu preço inválido para IFIX: {valor!r}')

    # Data DA COTAÇÃO, não do dia em que o job roda. Em feriado a BRAPI devolve
    # o último pregão com a data dele; regravar a mesma chave com o mesmo valor
    # não muda o arquivo e o workflow pula o commit. Sem isto, um feriado
    # criaria um ponto falso com o valor do dia anterior.
    momento = cotacao.get('regularMarketTime')
    if momento:
        utc = datetime.fromisoformat(momento.replace('Z', '+00:00'))
        data = utc.astimezone(FUSO).strftime('%Y-%m-%d')
    else:
        data = datetime.now(FUSO).strftime('%Y-%m-%d')

    return data, float(valor)


def atualizar_ifix():
    token = os.environ.get('BRAPI_TOKEN', '').strip()
    if not token:
        print('Erro: variável BRAPI_TOKEN não definida. '
              'Cadastre o secret no repositório e passe no workflow.')
        sys.exit(1)

    try:
        print('Buscando cotação do IFIX via BRAPI...')
        data, valor = buscar_ifix(token)

        historico = {}
        if os.path.exists(ARQUIVO):
            with open(ARQUIVO, 'r') as f:
                historico = json.load(f)

        anterior = historico.get(data)
        historico[data] = valor

        with open(ARQUIVO, 'w') as f:
            json.dump(historico, f, indent=4)

        if anterior is None:
            print(f'Sucesso! IFIX {valor} gravado em {data}.')
        else:
            print(f'IFIX {valor} em {data} (já havia {anterior}; arquivo regravado).')

    except Exception as e:
        print(f'Erro ao buscar o IFIX: {e}')
        sys.exit(1)


if __name__ == '__main__':
    atualizar_ifix()
