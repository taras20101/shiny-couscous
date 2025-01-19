from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services import (
    binance_api, mexc_api, bybit_api, 
    bingx_api, okx_api, kucoin_api, bitget_api
)

async def show_spreads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отримуємо пропозиції з усіх бірж
    exchanges = {
        'Binance': binance_api.BinanceAPI,
        'MEXC': mexc_api.MexcAPI,
        'Bybit': bybit_api.BybitAPI,
        'BingX': bingx_api.BingXAPI,
        'OKX': okx_api.OkxAPI,
        'KuCoin': kucoin_api.KuCoinAPI,
        'Bitget': bitget_api.BitgetAPI
    }
    
    message = "📊 Спреди на біржах:\n\n"
    
    for name, api in exchanges.items():
        try:
            buy_offers = api.get_buy_offers(context)
            sell_offers = api.get_sell_offers(context)
            
            if not buy_offers or not sell_offers:
                message += f"❌ {name}: Немає даних\n\n"
                continue
            
            best_buy = min(buy_offers, key=lambda x: x['price'])
            best_sell = max(sell_offers, key=lambda x: x['price'])
            
            spread = best_sell['price'] - best_buy['price']
            spread_percent = (spread / best_buy['price']) * 100
            
            message += (
                f"🏦 {name}:\n"
                f"├ Купівля: {best_buy['price']:.2f} UAH\n"
                f"├ Продаж: {best_sell['price']:.2f} UAH\n"
                f"├ Спред: {spread:.2f} UAH\n"
                f"└ Відсоток: {spread_percent:.2f}%\n\n"
            )
            
        except Exception as e:
            message += f"❌ {name}: Помилка отримання даних\n\n"
            continue
    
    keyboard = [
        ["💰 Купити USDT", "💱 Продати USDT"],
        ["📊 Перегляд спредів", "📈 Арбітраж"],
        ["💧 Ліквідність", "⚙️ Налаштування"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(message, reply_markup=reply_markup) 