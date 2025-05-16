from aiogram import Router, F
from aiogram import types
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu
from keyboards.reply import get_yes_no_back, get_consultation_back
from aiogram.types import FSInputFile

router = Router()

# Определение состояний для диагностики
class DiagnosticsStates(StatesGroup):
    QUESTION = State()

# Вопросы для каждого модуля (по 10 вопросов)
MODULE_QUESTIONS = {
    "module_1": [
        "Чувствуете ли вы усталость после еды?",
        "Едите ли вы регулярно 3-5 раз в день?",
        "Употребляете ли вы достаточно овощей и фруктов?",
        "Пьете ли вы достаточно воды в течение дня?",
        "Часто ли вы едите фастфуд?",
        "Есть ли у вас проблемы с пищеварением?",
        "Следите ли вы за калорийностью пищи?",
        "Употребляете ли вы сладкое каждый день?",
        "Есть ли у вас аллергия на какие-либо продукты?",
        "Чувствуете ли вы голод между приемами пищи?"
    ],
    "module_2": [
        "Спите ли вы 7-8 часов в сутки?",
        "Часто ли вы просыпаетесь ночью?",
        "Трудно ли вам засыпать?",
        "Чувствуете ли вы усталость утром?",
        "Используете ли вы гаджеты перед сном?",
        "Есть ли у вас регулярный график сна?",
        "Часто ли вы чувствуете сонливость днем?",
        "Есть ли у вас проблемы с дыханием во сне?",
        "Чувствуете ли вы стресс перед сном?",
        "Пьете ли вы кофе или чай перед сном?"
    ],
    "module_3": [
        "Часто ли вы чувствуете стресс?",
        "Есть ли у вас проблемы с концентрацией?",
        "Чувствуете ли вы тревогу без причины?",
        "Есть ли у вас перепады настроения?",
        "Часто ли вы раздражаетесь?",
        "Есть ли у вас физические симптомы стресса (головная боль, напряжение)?",
        "Удается ли вам расслабляться?",
        "Часто ли вы чувствуете давление на работе?",
        "Есть ли у вас поддержка со стороны близких?",
        "Практикуете ли вы медитацию или дыхательные упражнения?"
    ]
}

# Обработчик выбора модуля
@router.callback_query(lambda c: c.data in ["module_1", "module_2", "module_3"])
async def start_module(callback_query: types.callback_query, state: FSMContext):
    module = callback_query.data
    # Сохраняем текущий модуль и инициализируем счетчик вопросов и баллов
    await state.update_data(module=module, question_index=0, score=0)
    # Отправляем вводное видео для модуля
    video_path = f"data/videos/diagnostics/{module}_intro.mp4"
    await callback_query.message.answer_video_note(video_note=FSInputFile(video_path))
    # Задаем первый вопрос
    questions = MODULE_QUESTIONS[module]
    await callback_query.message.answer(questions[0], reply_markup=get_yes_no_back())
    await state.set_state(DiagnosticsStates.QUESTION)
    await callback_query.message.delete()
    await callback_query.answer()


# Обработчик ответов на вопросы
@router.message(DiagnosticsStates.QUESTION, F.text == ["Да", "Нет", "Назад в меню"])
async def process_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    module = user_data["module"]
    question_index = user_data["question_index"]
    score = user_data["score"]

    if message.text == "Назад в меню":
        await state.clear()
        await message.answer("Вы вернулись в главное меню:", reply_markup=get_main_menu())
        return

    # Обновляем баллы (1 балл за "Да")
    if message.text == "Да":
        score += 1
    await state.update_data(score=score)

    # Проверяем, есть ли еще вопросы
    questions = MODULE_QUESTIONS[module]
    if question_index + 1 < len(questions):
        await state.update_data(question_index=question_index + 1)
        await message.answer(questions[question_index + 1], reply_markup=get_yes_no_back())
    else:
        # Подводим итог
        result_text = f"Диагностика завершена! Ваш результат: {score} из 10.\n"
        if score >= 7:
            result_text += "У вас высокий уровень проблем в этой области. Рекомендуем консультацию."
        elif score >= 4:
            result_text += "Есть некоторые проблемы, обратите внимание на эту сферу."
        else:
            result_text += "У вас все в порядке, продолжайте в том же духе!"
        # Отправляем итоговое видео
        video_path = f"data/videos/diagnostics/{module}_result.mp4"
        await message.answer_video_note(video_note=FSInputFile(video_path))
        await message.answer(result_text, reply_markup=get_consultation_back())
        await state.clear()