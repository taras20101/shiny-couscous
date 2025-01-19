from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from services import (
    binance_api, mexc_api, bybit_api, 
    bingx_api, okx_api, kucoin_api, bitget_api
)

# Стани розмови
CHOOSE_EXCHANGE = range(1)

async def sell_usdt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Binance P2P", callback_data='sell_binance')],
        [InlineKeyboardButton("MEXC P2P", callback_data='sell_mexc')],
        [InlineKeyboardButton("Bybit P2P", callback_data='sell_bybit')],
        [InlineKeyboardButton("BingX P2P", callback_data='sell_bingx')],
        [InlineKeyboardButton("OKX P2P", callback_data='sell_okx')],
        [InlineKeyboardButton("KuCoin P2P", callback_data='sell_kucoin')],
        [InlineKeyboardButton("Bitget P2P", callback_data='sell_bitget')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏦 Оберіть біржу для продажу USDT:",
        reply_markup=reply_markup
    )
    return CHOOSE_EXCHANGE

async def exchange_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back':
        keyboard = [
            ["💰 Купити USDT", "💱 Продати USDT"],
            ["📊 Перегляд спредів", "📈 Арбітраж"],
            ["💧 Ліквідність", "⚙️ Налаштування"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text("Оберіть дію:", reply_markup=reply_markup)
        return ConversationHandler.END
    
    # Вибираємо API в залежності від біржі
    exchanges = {
        'sell_binance': (binance_api.BinanceAPI, "Binance"),
        'sell_mexc': (mexc_api.MexcAPI, "MEXC"),
        'sell_bybit': (bybit_api.BybitAPI, "Bybit"),
        'sell_bingx': (bingx_api.BingXAPI, "BingX"),
        'sell_okx': (okx_api.OkxAPI, "OKX"),
        'sell_kucoin': (kucoin_api.KuCoinAPI, "KuCoin"),
        'sell_bitget': (bitget_api.BitgetAPI, "Bitget")
    }
    
    api_class, exchange_name = exchanges.get(query.data, (None, None))
    if not api_class:
        await query.message.reply_text("Помилка вибору біржі")
        return ConversationHandler.END
    
    offers = api_class.get_sell_offers(context=context)
    
    if not offers:
        keyboard = [
            ["💰 Купити USDT", "💱 Продати USDT"],
            ["📊 Перегляд спредів", "📈 Арбітраж"],
            ["💧 Ліквідність", "⚙️ Налаштування"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text(
            "❌ Не знайдено пропозицій.\n"
            "Спробуйте пізніше або змініть налаштування.",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    
    message = f"💱 Найкращі пропозиції для продажу USDT на {exchange_name}:\n\n"
    
    for i, offer in enumerate(offers, 1):
        message += (
            f"{i}. Ціна: {offer['price']:.2f} UAH\n"
            f"👤 Покупець: {offer['merchant']} | ⭐ {offer['completion']}\n"
            f"💎 Доступно: {offer['amount']} USDT\n"
            f"🏦 Оплата: {', '.join(offer['payment_methods'])}\n\n"
        )
    
    keyboard = [
        ["💰 Купити USDT", "💱 Продати USDT"],
        ["📊 Перегляд спредів", "📈 Арбітраж"],
        ["💧 Ліквідність", "⚙️ Налаштування"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await query.message.reply_text(message, reply_markup=reply_markup)
    return ConversationHandler.END

async def amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        keyboard = [
            ["Купити USDT", "Продати USDT"],
            ["Перегляд спредів", "Налаштування"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Головне меню:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
        
    try:
        amount_usdt = float(update.message.text)
        price = binance_api.BinanceAPI.get_usdt_price()
        
        if price is None:
            await update.message.reply_text("Помилка отримання курсу. Спробуйте пізніше.")
            return ConversationHandler.END
        
        uah_amount = amount_usdt * price
        
        keyboard = [
            ["Купити USDT", "Продати USDT"],
            ["Перегляд спредів", "Налаштування"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"💱 Продаж USDT\n\n"
            f"Кількість USDT: {amount_usdt:.2f}\n"
            f"Курс: {price:.2f} UAH\n"
            f"Ви отримаєте: {uah_amount:.2f} UAH\n\n"
            f"Виплата доступна на:\n"
            f"- Monobank\n"
            f"- PrivatBank\n"
            f"- інші карти",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть коректну кількість USDT.")
        return CHOOSE_EXCHANGE 