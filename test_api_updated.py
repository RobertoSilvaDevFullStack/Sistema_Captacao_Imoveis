#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api():
    print("Testando API com scraper simplificado...")
    
    # Parâmetros como query string para GET
    params = {
        'city': 'rio-de-janeiro',
        'property_type': 'apartamento',
        'portal': 'zapimoveis'
    }

    url = 'http://127.0.0.1:5000/api/properties/search'
    print('Fazendo requisição GET para API...')
    
    try:
        response = requests.get(url, params=params, timeout=120)  # 2 minutos timeout
        print(f'Status: {response.status_code}')

        if response.status_code == 200:
            result = response.json()
            properties = result.get('properties', [])
            print(f'Sucesso! {len(properties)} propriedades encontradas')
            
            for i, prop in enumerate(properties[:5]):
                print(f'\n{i+1}. {prop.get("title", "N/A")}')
                print(f'   Preço: {prop.get("price", "N/A")}')
                print(f'   Local: {prop.get("location", "N/A")}')
                print(f'   Portal: {prop.get("portal", "N/A")}')
                print(f'   URL: {prop.get("url", "N/A")}')
        else:
            print(f'Erro HTTP {response.status_code}:')
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("Timeout na requisição - scraper pode estar demorando mais que o esperado")
    except requests.exceptions.ConnectionError:
        print("Erro de conexão - verifique se o backend está rodando")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    test_api()
