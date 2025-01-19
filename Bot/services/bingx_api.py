# Код для BingX API 

import logging
import requests
import time

class BingXAPI:
    @staticmethod
    def get_p2p_offers(side='BUY', fiat='UAH', asset='USDT', rows=10, verified_only=False, limit_amount=0, transaction_amount=0):
        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'uk-UA',
                'Content-Type': 'application/json',
                'Origin': 'https://bingx.com',
                'Referer': 'https://bingx.com/en-us/p2p/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            payload = {
                "page": 1,
                "pageSize": rows,
                "fiatCurrency": fiat,
                "cryptoCurrency": asset,
                "side": 1 if side == 'BUY' else 2,
                "paymentMethods": [],
                "amount": str(transaction_amount) if transaction_amount > 0 else "",
                "merchantVerified": verified_only
            }
            
            response = requests.post(
                'https://api-p2p.bingx.com/api/v1/p2p/advertisement/list',
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data or 'items' not in data['data']:
                return []
            
            offers = []
            for item in data['data']['items']:
                try:
                    amount = float(item['availableAmount'])
                    if limit_amount > 0 and amount < limit_amount:
                        continue
                    
                    offer = {
                        'price': float(item['price']),
                        'amount': amount,
                        'merchant': item['merchant']['nickname'],
                        'completion': f"{float(item['merchant'].get('completionRate', 0)) * 100:.2f}%",
                        'payment_methods': [method['name'] for method in item['paymentMethods']],
                        'exchange': 'BingX'
                    }
                    offers.append(offer)
                except Exception as e:
                    logging.error(f"Помилка обробки пропозиції BingX: {e}")
                    continue
            
            offers.sort(key=lambda x: x['price'], reverse=(side == 'SELL'))
            return offers[:3]

        except Exception as e:
            logging.error(f"Помилка отримання P2P пропозицій BingX: {e}")
            return []

    @staticmethod
    def get_buy_offers(context=None):
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return BingXAPI.get_p2p_offers(
            side='BUY',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        )

    @staticmethod
    def get_sell_offers(context=None):
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return BingXAPI.get_p2p_offers(
            side='SELL',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        ) 