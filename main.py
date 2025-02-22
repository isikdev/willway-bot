import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import logging

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError(
        "Не найден токен бота. Убедитесь, что файл .env существует и содержит TELEGRAM_BOT_TOKEN"
    )

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определяем состояния диалога
(STATE_WELCOME, STATE_VIDEO, STATE_READY, STATE_Q1, STATE_Q2, STATE_Q3, STATE_Q4, 
 STATE_Q5, STATE_Q6, STATE_Q7, STATE_Q8, STATE_SUBSCRIPTION, STATE_PAYMENT) = range(13)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем команду /start и отправляем приветственное сообщение."""
    welcome_text = (
        "Привет! На связи команда пространства физического и ментального здоровья WILLWAY. "
        "Мы помогаем людям создать здоровое подтянутое тело и отличное ментальное состояние.\n\n"
        "Через наши программы уже прошло 1000+ пользователей, которые смогли добиться хороших результатов и полностью изменить свой образ жизни.\n\n"
        "Наша суперсила в том, что мы подбираем программу, исходя из особенностей и целей человека. Давай пройдем этот путь до результата вместе?"
    )
    keyboard = [[InlineKeyboardButton("Старт", callback_data='start_conversation')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return STATE_WELCOME

async def start_conversation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинаем опрос после нажатия кнопки Начать."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Открываем видео файл в бинарном режиме
        with open("IMG_5106.MOV", "rb") as video_file:
            # Отправляем видео с увеличенным таймаутом и оптимизированными параметрами
            message = await query.message.reply_video(
                video=video_file,
                caption="Посмотри короткое видео, чтобы узнать больше о методе 👆",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Готов пройти опрос", callback_data='ready_for_quiz')]
                ]),
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30,
                # Добавляем поддержку стриминга
                supports_streaming=True,
                # Уменьшаем размер превью
                width=480,
                height=640
            )
            
            if message and message.video:
                print(f"\nVideo file_id: {message.video.file_id}\n")
                # Сохраняем file_id в контекст для последующего использования
                context.bot_data['video_file_id'] = message.video.file_id
                
    except Exception as e:
        print(f"Детальная ошибка при отправке видео: {str(e)}")
        # Пробуем использовать сохраненный file_id если он есть
        if 'video_file_id' in context.bot_data:
            try:
                await query.message.reply_video(
                    video=context.bot_data['video_file_id'],
                    caption="Посмотри короткое видео, чтобы узнать больше о методе 👆",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Готов пройти опрос", callback_data='ready_for_quiz')]
                    ])
                )
                return STATE_VIDEO
            except Exception as e2:
                print(f"Ошибка при повторной отправке видео: {str(e2)}")
        
        # Если все попытки не удались, отправляем сообщение об ошибке
        await query.message.reply_text(
            "Извините, произошла ошибка при отправке видео. Попробуйте еще раз через несколько секунд.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Попробовать снова", callback_data='start_conversation')]
            ])
        )
    
    return STATE_VIDEO

async def ready_for_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинаем опрос."""
    query = update.callback_query
    await query.answer()
    
    # Удаляем клавиатуру у предыдущего сообщения
    await query.edit_message_reply_markup(reply_markup=None)
    
    # Отправляем новое сообщение с первым вопросом
    keyboard = [
        [InlineKeyboardButton("Не занимаюсь", callback_data='sport_none')],
        [InlineKeyboardButton("1-2 раза в неделю", callback_data='sport_1_2')],
        [InlineKeyboardButton("3-4 раза в неделю", callback_data='sport_3_4')],
        [InlineKeyboardButton("5+ раз в неделю", callback_data='sport_5_plus')]
    ]
    
    await query.message.reply_text(
        "1/8: Как часто занимаешься спортом?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return STATE_Q1

async def question1_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем ответ на вопрос 1 и переходим к вопросу 2."""
    query = update.callback_query
    await query.answer()
    # Сохраняем ответ в user_data
    context.user_data['sport_frequency'] = query.data  # например, 'sport_1_2'
    
    # Переходим ко второму вопросу: как часто медитируешь?
    keyboard = [
        [InlineKeyboardButton("1-2 раза в неделю", callback_data='meditate_1_2')],
        [InlineKeyboardButton("3-5 раз в неделю", callback_data='meditate_3_5')],
        [InlineKeyboardButton("Каждый день", callback_data='meditate_daily')],
        [InlineKeyboardButton("Пробовал(а) но не пошло", callback_data='meditate_failed')],
        [InlineKeyboardButton("Не медитирую", callback_data='meditate_none')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("2/8: Как часто медитируешь/практикуешь?")
    await query.message.reply_text("Выбери вариант:", reply_markup=reply_markup)
    return STATE_Q2

async def question2_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем ответ на вопрос 2 и переходим к следующим вопросам (например, вопрос 3 – пол)."""
    query = update.callback_query
    await query.answer()
    context.user_data['meditate_frequency'] = query.data
    
    # Вопрос 3: Пол
    keyboard = [
        [InlineKeyboardButton("М", callback_data='male')],
        [InlineKeyboardButton("Ж", callback_data='female')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("3/8: Укажи, пожалуйста, свой пол:")
    await query.message.reply_text("Выбери вариант:", reply_markup=reply_markup)
    return STATE_Q3

async def question3_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем выбор пола и переходим к вопросу 4 (возраст)."""
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = query.data
    
    # Вопрос 4: Сколько тебе лет?
    await query.edit_message_text("4/8: Сколько тебе лет?\n\nВведи число.")
    return STATE_Q4

async def question4_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем возраст и спрашиваем рост."""
    user_age = update.message.text
    context.user_data['age'] = user_age
    await update.message.reply_text("5/8: Какой у тебя рост? (в см)\n\nВведи число.")
    return STATE_Q5

async def question5_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем рост и спрашиваем вес."""
    user_height = update.message.text
    context.user_data['height'] = user_height
    await update.message.reply_text("6/8: Какой сейчас вес? (в кг)\n\nВведи число.")
    return STATE_Q6

async def question6_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем вес и спрашиваем о травмах."""
    user_weight = update.message.text
    context.user_data['weight'] = user_weight
    await update.message.reply_text(
        "7/8: Есть ли у тебя какие-то травмы или противопоказания к занятиям? "
        "Если да, опиши, если нет – напиши 'нет' и нажми 'Далее'."
    )
    return STATE_Q7

async def question7_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем информацию о травмах и спрашиваем запрос."""
    injuries = update.message.text
    context.user_data['injuries'] = injuries
    # Вопрос 8: Запрос (можно реализовать множественный выбор, здесь для примера один выбор)
    keyboard = [
        [InlineKeyboardButton("Снижение веса", callback_data='weight_loss')],
        [InlineKeyboardButton("Коррекция осанки", callback_data='posture')],
        [InlineKeyboardButton("Убрать боли в спине/шее", callback_data='back_neck')],
        [InlineKeyboardButton("Общий тонус/рельеф мышц", callback_data='muscle_tone')],
        [InlineKeyboardButton("Восстановиться после родов", callback_data='postpartum')],
        [InlineKeyboardButton("Снизить уровень стресса", callback_data='stress_reduction')],
        [InlineKeyboardButton("Почувствовать контакт с собой", callback_data='self_contact')],
        [InlineKeyboardButton("Найти внутреннюю опору", callback_data='inner_support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("8/8: Какой у тебя запрос? Выбери один или несколько вариантов.", reply_markup=reply_markup)
    return STATE_Q8

async def question8_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем выбор запросов пользователя."""
    query = update.callback_query
    await query.answer()
    
    # Инициализируем список выбранных целей, если его еще нет
    if 'selected_goals' not in context.user_data:
        context.user_data['selected_goals'] = set()
    
    # Если нажата кнопка "Далее"
    if query.data == 'next':
        if not context.user_data['selected_goals']:
            await query.answer("Пожалуйста, выберите хотя бы один вариант", show_alert=True)
            return STATE_Q8
            
        subscription_text = (
            "Круто, твоя программа уже готова! 🎉\n\n"
            "Мы подготовили для тебя:\n\n"
            "- Доступ к удобному приложению с видеопрограммой 📱\n"
            "- Медитации и практики эмоциональной гигиены 🧘‍♀️\n"
            "- Персонального ассистента-нутрициолога 👨‍⚕️\n\n"
            "Выбери вариант подписки:"
        )
        keyboard = [
            [InlineKeyboardButton("Месяц — 2222₽", callback_data='sub_month')],
            [InlineKeyboardButton("Год — 17777₽ (-35%)", callback_data='sub_year')]
        ]
        # Сначала отправляем новое сообщение
        await query.message.reply_text(
            subscription_text, 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        # Затем удаляем клавиатуру у предыдущего сообщения
        await query.edit_message_reply_markup(reply_markup=None)
        return STATE_SUBSCRIPTION
    
    # Обрабатываем выбор цели
    goal_data = query.data
    if goal_data in context.user_data['selected_goals']:
        context.user_data['selected_goals'].remove(goal_data)
    else:
        context.user_data['selected_goals'].add(goal_data)
    
    # Создаем клавиатуру с отметками выбранных пунктов
    goals_buttons = [
        [InlineKeyboardButton(
            f"{'✅' if 'weight_loss' in context.user_data['selected_goals'] else '⭕'} Снижение веса",
            callback_data='weight_loss')],
        [InlineKeyboardButton(
            f"{'✅' if 'posture' in context.user_data['selected_goals'] else '⭕'} Коррекция осанки",
            callback_data='posture')],
        [InlineKeyboardButton(
            f"{'✅' if 'back_neck' in context.user_data['selected_goals'] else '⭕'} Убрать боли в спине/шее",
            callback_data='back_neck')],
        [InlineKeyboardButton(
            f"{'✅' if 'muscle_tone' in context.user_data['selected_goals'] else '⭕'} Общий тонус/рельеф мышц",
            callback_data='muscle_tone')],
        [InlineKeyboardButton(
            f"{'✅' if 'postpartum' in context.user_data['selected_goals'] else '⭕'} Восстановиться после родов",
            callback_data='postpartum')],
        [InlineKeyboardButton(
            f"{'✅' if 'stress_reduction' in context.user_data['selected_goals'] else '⭕'} Снизить уровень стресса",
            callback_data='stress_reduction')],
        [InlineKeyboardButton(
            f"{'✅' if 'self_contact' in context.user_data['selected_goals'] else '⭕'} Почувствовать контакт с собой",
            callback_data='self_contact')],
        [InlineKeyboardButton(
            f"{'✅' if 'inner_support' in context.user_data['selected_goals'] else '⭕'} Найти внутреннюю опору",
            callback_data='inner_support')]
    ]
    
    # Добавляем кнопку "Далее"
    goals_buttons.append([InlineKeyboardButton("➡️ Далее", callback_data='next')])
    
    try:
        await query.edit_message_text(
            "8/8: Какой у тебя запрос? Выбери один или несколько вариантов.",
            reply_markup=InlineKeyboardMarkup(goals_buttons)
        )
    except Exception as e:
        print(f"Ошибка при обновлении сообщения: {e}")
        # Если не удалось отредактировать, отправляем новое
        await query.message.reply_text(
            "8/8: Какой у тебя запрос? Выбери один или несколько вариантов.",
            reply_markup=InlineKeyboardMarkup(goals_buttons)
        )
    
    return STATE_Q8

async def subscription_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем выбор подписки."""
    query = update.callback_query
    await query.answer()
    
    subscription_choice = query.data
    context.user_data['subscription'] = subscription_choice
    
    # Отправляем финальное сообщение
    final_text = (
        "Спасибо за доверие и добро пожаловать в пространство WILLWAY! 🎉\n\n"
        "Доступ к личному кабинету уже отправлен на твою почту, "
        "а программа доступна в этом боте."
    )
    
    # Удаляем клавиатуру и обновляем текст
    await query.edit_message_text(final_text)
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена диалога."""
    await update.message.reply_text("Диалог прерван.")
    return ConversationHandler.END

def run_bot():
    """Запускает бота в отдельной функции"""
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE_WELCOME: [
                CallbackQueryHandler(start_conversation_callback, pattern='^start_conversation$')
            ],
            STATE_VIDEO: [
                CallbackQueryHandler(ready_for_quiz_callback, pattern='^ready_for_quiz$')
            ],
            STATE_Q1: [
                CallbackQueryHandler(question1_handler, pattern='^sport_')
            ],
            STATE_Q2: [
                CallbackQueryHandler(question2_handler, pattern='^meditate_')
            ],
            STATE_Q3: [
                CallbackQueryHandler(question3_handler, pattern='^(male|female)$')
            ],
            STATE_Q4: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, question4_handler)
            ],
            STATE_Q5: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, question5_handler)
            ],
            STATE_Q6: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, question6_handler)
            ],
            STATE_Q7: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, question7_handler)
            ],
            STATE_Q8: [
                CallbackQueryHandler(question8_handler, pattern='^(weight_loss|posture|back_neck|muscle_tone|postpartum|stress_reduction|self_contact|inner_support|next)$')
            ],
            STATE_SUBSCRIPTION: [
                CallbackQueryHandler(subscription_handler, pattern='^sub_')
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    print('Бот запущен...')
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    run_bot()
