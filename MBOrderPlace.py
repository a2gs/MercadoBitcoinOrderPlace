#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota
# andre.scota@gmail.com
# MIT license

# https://www.mercadobitcoin.com.br/trade-api/
# https://www.mercadobitcoin.com.br/api-doc/

from sys import argv, exit
import time

import hashlib
import hmac
import json

from http import client
from urllib.parse import urlencode


def runOrder(conn, argOrderType : str, argCoin : str, argValue : str) -> bool:
	MB_TAPI_ID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
	MB_TAPI_SECRET = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
	REQUEST_PATH = '/tapi/v3/'

	if argOrderType == 'BUY':
		param = {
			'tapi_method': 'place_market_buy_order',
			'tapi_nonce': str(int(time.time())),
			'coin_pair': argCoin,
			'cost': argValue,
		}

	elif argOrderType == 'SELL':
		param = {
			'tapi_method': 'place_market_sell_order',
			'tapi_nonce': str(int(time.time())),
			'coin_pair': argCoin,
			'quantity': argValue,
		}

	else:
		return False

	param = urlencode(param)
	params_string = REQUEST_PATH + '?' + param
	H = hmac.new(bytes(MB_TAPI_SECRET, encoding = 'utf8'), digestmod = hashlib.sha512)
	H.update(params_string.encode('utf-8'))
	tapi_mac = H.hexdigest()

	headersOrder = {
		'Content-Type' : 'application/x-www-form-urlencoded',
		'TAPI-ID'      : MB_TAPI_ID,
		'TAPI-MAC'     : tapi_mac
	}

	try:
		conn.request("POST", REQUEST_PATH, params, headersOrder)

		response = conn.getresponse()
		response = response.read()

		response_json = json.loads(response)
		print("Ordem executada! Resultado:")

		print(f"Order Id: [{response_json['response_data']['order']['order_id']}]")
		print(f"Coin Pair: [{response_json['response_data']['order']['coin_pair']}]")
		print(f"Order Type: [{response_json['response_data']['order']['order_type']}] (1 - buy; 2 - sell)")
		print(f"Status: [{response_json['response_data']['order']['status']}] (2 - open; 3 - canceled; 4 - filled)")
		print(f"Execucoes: [{response_json['response_data']['order']['has_fills']}] (false - Sem execucoes; true - Com uma ou mais execucoes)")
		print(f"Quantidade: [{response_json['response_data']['order']['quantity']}]")
		print(f"Preco Limite: [{response_json['response_data']['order']['limit_price']}]")
		print(f"Qtd Executada: [{response_json['response_data']['order']['executed_quantity']}]")
		print(f"Preco Medio Executada: [{response_json['response_data']['order']['executed_price_avg']}]")
		print(f"Taxa: [{response_json['response_data']['order']['fee']}]")
		print(f"Timestamp: [{response_json['response_data']['order']['created_timestamp']}]")
		print(f"Updated Timestamp: [{response_json['response_data']['order']['updated_timestamp']}]")
		print(f"Operacao:")
		print(f"\tId: [{response_json['response_data']['order']['operations']['operation_id']}]")
		print(f"\tQtd: [{response_json['response_data']['order']['operations']['quantity']}]")
		print(f"\tPreco: [{response_json['response_data']['order']['operations']['price']}]")
		print(f"\tFee: [{response_json['response_data']['order']['operations']['fee_rate']}]")
		print(f"\tTimestamp: [{response_json['response_data']['order']['operations']['executed_timestamp']}]")

		print(f"Status: [{response_json['status_code']}]")
		print(f"Server Timestamp: [{response_json['server_unix_timestamp']}]")

		#print(json.dumps(response_json, indent=4))

		return True

	except Exception as e:
		print(f"Erro colocando ordem {param}: {e}")
		return False


def getPrice(conn, coin : str) -> [bool, float]:
	REQUEST_PATH = '/api/BTC/ticker/'

	try:
		conn.request("GET", REQUEST_PATH, '', {})

		response = conn.getresponse()
		response = response.read()
		response_json = json.loads(response)

		return (True, float(response_json.get('ticker').get('last')))

	except Exception as e:
		return (False, f"{e}")


if __name__ == '__main__':
	if len(argv) != 5:
		print(f"Uso:\n\t{argv[0]} [BUY / SELL] [MOEDA] [VALOR_REAIS / QTD_MOEDA] [MAIOR / MENOR / IGUAL] [VALOR_DE_REFERENCIA]")
		exit(1)

	if argCompare not in ['MAIOR', 'MENOR', 'IGUAL']:
		print(f"Erro. Comparacoes permitidas: 'MAIOR', 'MENOR' ou 'IGUAL'. Comparacao '{argCompare}' nao reconhecida")
		exit(1)

	if argOrderType not in ['BUY', 'SELL']:
		print(f"Erro. Comparacoes permitidas: 'BUY' ou 'SELL'. Comparacao '{argOrderType}' nao reconhecida")
		exit(1)

	argOrderType = argv[1]
	argCoin      = argv[2]
	argValue     = argv[3]
	argCompare   = argv[4]
	argReference = argv[5]

	try:
		conn = client.HTTPSConnection('www.mercadobitcoin.net')

	except Exception as e:
		if conn:
			conn.close()

		print("Erro de conexao: {e}")
		exit(1)

	while True:
		ret, price = getPrice(conn, argCoin)

		if ret == False:
			print("Erro no request do ticker.")
			exit(1)

		if argCompare == 'MAIOR' and price < argPrice:
			ret = runOrder(conn, argOrderType, argCoin, argValue)
			break

		elif argCompare == 'MENOR' and price > argPrice:
			ret = runOrder(conn, argOrderType, argCoin, argValue)
			break

		elif argCompare == 'IGUAL' and price == argPrice:
			ret = runOrder(conn, argOrderType, argCoin, argValue)
			break

		else:
			pass

		time.sleep(2)

	exit(0)
