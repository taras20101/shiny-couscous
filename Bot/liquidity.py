from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services import (
    binance_api, mexc_api, bybit_api, 
    bingx_api, okx_api, kucoin_api, bitget_api
)

async def show_liquidity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exchanges = {
        'Binance': binance_api.BinanceAPI,
        'MEXC': mexc_api.MexcAPI,
        'Bybit': bybit_api.BybitAPI,
        'BingX': bingx_api.BingXAPI,
        'OKX': okx_api.OkxAPI,
        'KuCoin': kucoin_api.KuCoinAPI,
        'Bitget': bitget_api.BitgetAPI
    }
    
    message = "💧 Ліквідність на біржах:\n\n"
    
    for name, api in exchanges.items():
        buy_offers = api.get_buy_offers(context)
        sell_offers = api.get_sell_offers(context)
        
        buy_volume = sum(offer['amount'] for offer in buy_offers)
        sell_volume = sum(offer['amount'] for offer in sell_offers)
        
        message += (
            f"🏦 {name}:\n"
            f"├ Купівля: {buy_volume:,.0f} USDT\n"
            f"├ Продаж: {sell_volume:,.0f} USDT\n"
            f"└ Всього: {buy_volume + sell_volume:,.0f} USDT\n\n"
        )
    
    await update.message.reply_text(message) 