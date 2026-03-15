import asyncio  # Для работы с асинхронностью (таймеры, задержки)
from aiogram import F, Router  # F - для фильтров, Router - для маршрутизации хендлеров
from aiogram.types import Message, CallbackQuery  # Типы сообщений и callback-запросов
from aiogram.fsm.state import State, StatesGroup  # Для машины состояний (FSM)
from aiogram.fsm.context import FSMContext  # Контекст для работы с состояниями
from aiogram.filters.command import Command  # Фильтр для команд (/start)


from datetime import datetime, timedelta  # Для работы с датой и временем
import random  # Для случайных чисел и выбора сообщений
import json  # Для работы с JSON файлами
from Json_read import UserSettings  # Твой класс для работы с JSON
import os  # Для проверки существования файлов

import App.button as bt  # Твои клавиатуры
import App.clear as cl  # Твоя функция очистки сообщений


# Создаем роутер - все хендлеры будут привязаны к нему
router = Router()

# Создаем объекты для работы с файлами настроек
settings = UserSettings('App/settings.json')  # Настройки пользователей
message_ole = UserSettings('App/message.json')  # Сообщения для отправки


# Класс для машины состояний (FSM) - управление шагами настройки
class Settings(StatesGroup):
    waiting_for_type = State()      # Состояние: ждем тип сообщения
    waiting_for_message = State()   # Состояние: ждем количество сообщений
    waiting_for_time = State()       # Состояние: ждем время периода
    confirm = State()                # Состояние: подтверждение данных

# Обработчик команды /start
@router.message(Command("start"))
async def menu(message: Message):
    # Проверка: только определенные пользователи могут использовать бота
    
    # Получаем username пользователя
    first_name = message.from_user.username
    # Получаем список всех пользователей из файла
    data_user = settings.get_all_users()
    
    # Если пользователь есть в списке - пускаем
    if first_name in data_user:
        print(first_name)  # Логируем в консоль
    else:
        # Если нет - добавляем нового пользователя
        settings.add_user(username=first_name)

    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(
        "Меню",
        reply_markup=bt.start_menu
    )


# Обработчик нажатия на кнопку с data="start" - запуск рассылки
@router.callback_query(F.data == "start")
async def message_for_ole1(callback: CallbackQuery):
    # Отвечаем на callback (убираем "часики" на кнопке)
    await callback.answer("Бот начал работать")
    # Меняем текст сообщения
    await callback.message.edit_text(text='🔄 Работает...')

    # Получаем данные пользователя
    first_name = callback.from_user.username  # Username пользователя
    file_name = 'App/message.json'  # Путь к файлу с сообщениями
    
    # Загружаем настройки пользователя с проверками
    # Получаем время периода из настроек
    h = settings.get_user_message(username=first_name, field='time')
    if h is None:
        h = 1  # Если нет настроек - ставим время по умолчанию - 1 час
    
    # Получаем тип сообщений
    data_user = settings.get_user_message(username=first_name, field='type')
    if data_user is None:
        data_user = 'love'  # Тип по умолчанию
    
    # Получаем количество сообщений
    count_message = settings.get_user_message(username=first_name, field='message')
    if count_message is None:
        count_message = 5  # Количество по умолчанию
    else:
        count_message = int(count_message)  # Преобразуем в число
    
    # Загружаем сообщения из файла
    try:
        # Проверяем, существует ли файл
        if os.path.exists(file_name):
            # Открываем и читаем JSON файл
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Если файл не найден - сообщаем об ошибке
            await callback.message.answer(f"❌ Файл {file_name} не найден")
            return
    except (IOError, json.JSONDecodeError) as e:
        # Если ошибка чтения - сообщаем
        await callback.message.answer(f"❌ Ошибка чтения файла: {e}")
        return
    
    # Проверяем наличие нужных ключей в данных
    # Если ключа 'love' нет - создаем с сообщением по умолчанию
    if 'love' not in data:
        data['love'] = ["Сообщение по умолчанию"]
    # Если ключа 'type_Другое' нет - создаем с сообщением по умолчанию
    if 'type_Другое' not in data:
        data['type_Другое'] = ["Другое сообщение по умолчанию"]
    
    # --- ЛОГИКА ОТПРАВКИ В СЛУЧАЙНЫЕ МОМЕНТЫ ---
    
    now = datetime.now()  # Текущее время
    end_time = now + timedelta(hours=h)  # Время окончания (текущее + h часов)
    time_range_seconds = h * 3600  # Общий диапазон времени в секундах
    
    # МАКСИМАЛЬНЫЙ ПЕРЕРЫВ 30 МИНУТ (1800 секунд)
    MAX_BREAK = 1800  # 30 минут в секундах
    
    # Отправляем информацию о параметрах отправки
    await callback.message.answer(
        f"📊 Параметры отправки:\n"
        f"• Период: {h} час(ов)\n"
        f"• Сообщений: {count_message}\n"
        f"• Тип: {data_user}\n"
        f"• Макс. перерыв: 30 минут\n"
        f"• Начало: {now.strftime('%H:%M:%S')}\n"
        f"• Окончание: {end_time.strftime('%H:%M:%S')}"
    )
    
    # Генерируем случайные моменты времени для отправки
    if count_message > 0:
        # УЧИТЫВАЕМ МАКСИМАЛЬНЫЙ ПЕРЕРЫВ ПРИ ГЕНЕРАЦИИ
        
        # Проверяем, можно ли разместить сообщения с макс. перерывом 30 мин
        max_possible_breaks = (count_message - 1) * MAX_BREAK
        if max_possible_breaks > time_range_seconds:
            # Если нельзя - предупреждаем
            await callback.message.answer(
                f"⚠️ Предупреждение: {count_message} сообщений не могут быть отправлены "
                f"с макс. перерывом 30 мин за {h} час(ов). "
                f"Перерыв будет автоматически уменьшен."
            )
        
        # Генерируем случайные интервалы с учетом максимального перерыва
        random_seconds = []  # Список интервалов между сообщениями
        remaining_seconds = time_range_seconds  # Оставшееся время
        
        # Для каждого сообщения генерируем случайный интервал
        for i in range(count_message):
            if i == 0:
                # Первое сообщение может быть в любое время от 0 до MAX_BREAK
                max_first = min(MAX_BREAK, remaining_seconds)
                if max_first <= 0:
                    break
                seconds = random.randint(1, max_first)
            else:
                # Следующие сообщения: перерыв от 1 до MAX_BREAK секунд
                max_break = min(MAX_BREAK, remaining_seconds)
                if max_break <= 0:
                    break
                seconds = random.randint(1, max_break)
            
            random_seconds.append(seconds)  # Добавляем интервал
            remaining_seconds -= seconds  # Уменьшаем оставшееся время
        
        # Преобразуем накопленные интервалы в абсолютные моменты времени
        absolute_times = []  # Абсолютное время отправки от начала
        current = 0
        for interval in random_seconds:
            current += interval  # Накопленная сумма интервалов
            absolute_times.append(current)  # Время отправки от старта
        
        sent_count = 0  # Счетчик отправленных сообщений
        
        # Цикл отправки сообщений
        for i, abs_seconds in enumerate(absolute_times):
            # Проверяем, не вышли ли за пределы времени
            current_time = datetime.now()
            if current_time >= end_time:
                await callback.message.answer(f"⏰ Время вышло. Отправлено {sent_count} из {count_message}")
                break
            
            # Вычисляем время ожидания до следующей отправки
            if i == 0:
                wait_time = abs_seconds  # Для первого - просто интервал
            else:
                wait_time = abs_seconds - absolute_times[i-1]  # Для остальных - разница
            
            # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА МАКСИМАЛЬНОГО ПЕРЕРЫВА
            if wait_time > MAX_BREAK:
                wait_time = MAX_BREAK
                await callback.message.answer("⚠️ Перерыв уменьшен до 30 минут")
            
            # Проверяем, что ожидание не больше оставшегося времени
            remaining = (end_time - datetime.now()).total_seconds()
            if wait_time > remaining:
                wait_time = max(1, remaining - 1)  # Ждем до конца периода
            
            # ЗАПУСКАЕМ ТАЙМЕР С ОБНОВЛЕНИЕМ КАЖДУЮ СЕКУНДУ
            if wait_time > 0:
                # Отправляем первое сообщение таймера
                minutes = wait_time // 60
                seconds = wait_time % 60
                timer_msg = await callback.message.answer(
                    f"⏳ Следующее сообщение через {int(minutes)} мин {int(seconds)} сек"
                )
                
                # Запускаем обратный отсчет с обновлением каждую секунду
                for remaining_wait in range(int(wait_time) - 1, 0, -1):
                    await asyncio.sleep(1)  # Ждем 1 секунду
                    
                    # Проверяем, не вышло ли время
                    if datetime.now() >= end_time:
                        await timer_msg.delete()  # Удаляем таймер
                        await callback.message.answer(f"⏰ Время вышло. Отправлено {sent_count} из {count_message}")
                        break
                    
                    # Обновляем сообщение таймера
                    minutes = remaining_wait // 60
                    seconds = remaining_wait % 60
                    try:
                        await timer_msg.edit_text(
                            f"⏳ Следующее сообщение через {int(minutes)} мин {int(seconds)} сек"
                        )
                    except:
                        pass  # Если не удалось обновить (сообщение слишком старое)
                
                # Удаляем сообщение таймера после окончания
                try:
                    await timer_msg.delete()
                except:
                    pass
            
            # Проверяем снова после ожидания
            if datetime.now() >= end_time:
                await callback.message.answer(f"⏰ Время вышло. Отправлено {sent_count} из {count_message}")
                break
            
            # Выбираем и отправляем сообщение
            try:
                # Выбираем текст в зависимости от типа
                if data_user == 'love':
                    message_text = random.choice(data['love'])  # Случайное из love
                else:
                    message_text = random.choice(data['type_Другое'])  # Случайное из другого
                
                # Отправляем сообщение в указанный чат
                await callback.bot.send_message(chat_id=958377023, text=message_text)
                # Отправляем подтверждение
                await callback.message.answer(text=f'✅ [{sent_count+1}/{count_message}] Отправлено: {message_text[:30]}...')
                
                sent_count += 1  # Увеличиваем счетчик
                
            except Exception as e:
                # Если ошибка - сообщаем
                await callback.message.answer(text=f'❌ Ошибка отправки: {e}')
        
        # Финальное сообщение о завершении
        await callback.message.answer(
            text=f'🏁 Работа завершена!\n'
                 f'Отправлено {sent_count} из {count_message} сообщений\n'
                 f'За период: {h} час(ов)'
        )
    else:
        # Если нет сообщений для отправки
        await callback.message.answer(text='❌ Нет сообщений для отправки')
        
# Обработчик кнопки "Письма"
@router.callback_query(F.data == "message_for_ole")
async def callback_message_for_ole(callback: CallbackQuery):
    # Меняем текст и показываем клавиатуру с письмами
    await callback.message.edit_text(text='Письма', reply_markup=await bt.inline_pis())
    await callback.answer("Вы выбрали Письма")


# Обработчик кнопки "Настройки" - начало настройки
@router.callback_query(F.data == "settings")
async def time_callback(callback: CallbackQuery, state: FSMContext):
    # Очищаем предыдущие состояния
    await state.clear()
    # Устанавливаем состояние "ждем время"
    await state.set_state(Settings.waiting_for_time)
    
    await callback.answer("Вы выбрали Настройка")
    await callback.message.edit_text(text='Введите Время')

# Обработчик ввода времени (состояние waiting_for_time)
@router.message(Settings.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    """Этот обработчик сработает ТОЛЬКО в состоянии waiting_for_time"""
    
    try:
        # Пробуем преобразовать текст в число
        time = int(message.text)
    except ValueError:
        # Если не число - ошибка
        await message.answer("❌ Введите число!")
        return 
    
    # Сохраняем время в состояние
    await state.update_data(waiting_for_time=time)

    # Переходим к следующему состоянию - выбор типа
    await state.set_state(Settings.waiting_for_type)
    await message.answer("Выберите тип сообщения Оле:\n-Любовь\n-Другое\nНапиши тип:")

# Обработчик ввода типа сообщения (состояние waiting_for_type)
@router.message(Settings.waiting_for_type)
async def process_type(message: Message, state: FSMContext):
    
    type_text = message.text.lower()  # Приводим к нижнему регистру
    # Определяем тип
    if type_text == 'любовь':
        type_value = "love"
    else:
        type_value = "type_Другое"  # Все остальное - другое
    
    # Сохраняем тип
    await state.update_data(waiting_for_type=type_value)
    # Переходим к следующему состоянию - ввод количества
    await state.set_state(Settings.waiting_for_message)
    await message.answer("Введи Кол-во сообщений:")


# Обработчик ввода количества сообщений
@router.message(Settings.waiting_for_message)
async def process_message(message: Message, state: FSMContext):

    try:
        # Пробуем преобразовать в число
        message_ole = int(message.text)
    except ValueError:
        # Если не число - ошибка
        await message.answer("❌ Введите число!")
        return 

    # Сохраняем количество
    await state.update_data(waiting_for_message=message_ole)
    # Получаем все сохраненные данные
    data = await state.get_data()
    # Переходим к подтверждению
    await state.set_state(Settings.confirm)
    # Показываем введенные данные для подтверждения
    await message.answer(
        f"📊 Параметры отправки:\n"
        f"• Период: {data['waiting_for_time']} час(ов)\n"
        f"• Сообщений: {data['waiting_for_message']}\n"
        f"• Тип: {data['waiting_for_type']}\n"
    )

# Обработчик подтверждения
@router.message(Settings.confirm)
async def process_con(message: Message, state: FSMContext):

    # Проверяем, ответил ли пользователь "да"
    message_confirm = message.text.lower() == 'да' or 'lf'  # 'lf' - опечатка?

    if message_confirm:
        # Если да - сохраняем настройки
        message_confirm = True
        await state.update_data(confirm=message_confirm)
        # Получаем все данные
        data = await state.get_data()
        first_name = message.from_user.username
        
        # Формируем данные для сохранения
        Info = [{
            "type": data['waiting_for_type'],
            "message": data['waiting_for_message'],
            "time": data['waiting_for_time'],
            "con": data['confirm']}]
        
        # Сохраняем в файл
        settings.update_user(username=first_name, new_data=Info)
        # Очищаем состояние
        await state.clear()
        # Удаляем сообщения пользователя
        await cl.delete_all_user_messages(message)
        # Подтверждаем сохранение
        await message.answer("✅ Настройки сохранены!", reply_markup=bt.inline_pis())
    else:
        # Если не да - отменяем
        await state.update_data(confirm=message_confirm)
        # Удаляем сообщения
        await cl.delete_all_user_messages(message)
        # Очищаем состояние
        await state.clear()
        # Сообщаем об отмене
        await message.answer("❌ Отменено", reply_markup=bt.inline_pis())

