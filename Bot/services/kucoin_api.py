# Код для KuCoin API 

import logging
import requests
import time

class KuCoinAPI:
    @staticmethod
    def get_p2p_offers(side='BUY', fiat='UAH', asset='USDT', rows=10, verified_only=False, limit_amount=0, transaction_amount=0):
        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'uk-UA',
                'Content-Type': 'application/json',
                'Origin': 'https://www.kucoin.com',
                'Referer': 'https://www.kucoin.com/p2p',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            payload = {
                "currency": asset,
                "fiatCurrency": fiat,
                "tradeType": side.lower(),
                "page": 1,
                "pageSize": rows,
                "merchantLevel": ["certified"] if verified_only else [],
                "amount": str(transaction_amount) if transaction_amount > 0 else ""
            }
            
            response = requests.post(
                'https://www.kucoin.com/_api/otc/ad/list',
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data or 'items' not in data:
                return []
            
            offers = []
            for item in data['items']:
                try:
                    amount = float(item['remainAmount'])
                    if limit_amount > 0 and amount < limit_amount:
                        continue
                    
                    offer = {
                        'price': float(item['price']),
                        'amount': amount,
                        'merchant': item['nickName'],
                        'completion': f"{float(item.get('completionRate', 0)) * 100:.2f}%",
                        'payment_methods': [pm['name'] for pm in item['payments']],
                        'exchange': 'KuCoin'
                    }
                    offers.append(offer)
                except Exception as e:
                    logging.error(f"Помилка обробки пропозиції KuCoin: {e}")
                    continue
            
            offers.sort(key=lambda x: x['price'], reverse=(side == 'SELL'))
            return offers[:3]

        except Exception as e:
            logging.error(f"Помилка отримання P2P пропозицій KuCoin: {e}")
            return []

    @staticmethod
    def get_buy_offers(context=None):
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return KuCoinAPI.get_p2p_offers(
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
        
        return KuCoinAPI.get_p2p_offers(
            side='SELL',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        ) 