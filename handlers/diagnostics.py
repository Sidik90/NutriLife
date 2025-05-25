import json
import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_yes_no_keyboard, get_diagnostic_result_keyboard, get_diagnostics_modules
from utils.logger import logger, log_to_db

router = Router()

# Определение состояний для диагностики
class DiagnosticStates(StatesGroup):
    QUESTION = State()

# Загрузка вопросов из JSON
def load_diagnostic_questions():
    with open("data/json/diagnostics.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Обработчик выбора темы диагностики (только для тем, начинающихся с "diag_" и не содержащих "answer")
@router.callback_query(F.data.startswith("diag_") & ~F.data.contains("answer"))
async def process_diagnostic_theme(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    theme = callback_query.data.split("_")[1]
    logger.info(f"Пользователь {user_id} выбрал тему диагностики: {theme}")

    # Отправляем видео перед началом диагностики
    video_path = f"data/videos/{theme}_start.mp4"
    try:
        if os.path.exists(video_path):
            await callback_query.message.answer_video(video=FSInputFile(video_path), caption=f"Видео для темы {theme.capitalize()}")
            logger.info(f"Видео для темы {theme} успешно отправлено пользователю {user_id}")
        else:
            await callback_query.message.answer(f"Видео для темы {theme.capitalize()} не найдено. Начинаем диагностику.")
            logger.warning(f"Видео для темы {theme} не найдено для пользователя {user_id}")
    except Exception as e:
        await callback_query.message.answer("Произошла ошибка при отправке видео. Начинаем диагностику.")
        logger.error(f"Ошибка при отправке видео для темы {theme} пользователю {user_id}: {str(e)}")
        await log_to_db("ERROR", f"Ошибка при отправке видео: {str(e)}", user_id)

    # Инициализируем данные для диагностики
    diagnostics_data = load_diagnostic_questions()
    if theme in diagnostics_data:
        questions = diagnostics_data[theme].get("questions", [])
        await state.update_data(theme=theme, question_index=0, questions=questions, answers=[])

        if questions:
            # Задаем первый вопрос
            first_question = questions[0]
            await callback_query.message.answer(f"Вопрос {first_question['id']}: {first_question['text']}", reply_markup=get_yes_no_keyboard(theme, first_question['id']))
            await state.set_state(DiagnosticStates.QUESTION)
        else:
            await callback_query.message.answer("Вопросы для данной темы отсутствуют. Диагностика завершена.", reply_markup=get_diagnostic_result_keyboard())
            await state.clear()
    else:
        await callback_query.message.answer("Выбранная тема диагностики не найдена.", reply_markup=get_diagnostic_result_keyboard())
        logger.warning(f"Тема {theme} не найдена для пользователя {user_id}")
        await state.clear()

    await callback_query.answer()

# Обработчик ответов на вопросы диагностики
@router.callback_query(DiagnosticStates.QUESTION, F.data.startswith("diag_answer_"))
async def process_diagnostic_answer(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    theme = data.get("theme")
    question_index = data.get("question_index", 0)
    questions = data.get("questions", [])
    answers = data.get("answers", [])

    # Обработка ответа
    answer_data = callback_query.data.split("_")
    question_id = int(answer_data[-2])  # ID вопроса
    answer = answer_data[-1]  # yes или no

    # Сохраняем ответ
    answers.append({"question_id": question_id, "answer": answer})
    logger.info(f"Пользователь {user_id} ответил на вопрос {question_id} темы {theme}: {answer}")

    # Отправляем обратную связь
    current_question = next((q for q in questions if q['id'] == question_id), None)
    if current_question:
        if answer == "yes" and "response" in current_question:
            await callback_query.message.answer(f"Ответ: {current_question['response']}")
        else:
            await callback_query.message.answer("Спасибо за ответ! ✅")

    question_index += 1
    await state.update_data(question_index=question_index, answers=answers)

    if question_index < len(questions):
        # Задаем следующий вопрос
        next_question = questions[question_index]
        await callback_query.message.bot.send_message(chat_id=user_id, text=f"Вопрос {next_question['id']}: {next_question['text']}", reply_markup=get_yes_no_keyboard(theme, next_question['id']))
    else:
        # Завершение диагностики
        end_video_path = f"data/videos/{theme}_end.mp4"
        try:
            if os.path.exists(end_video_path):
                await callback_query.message.bot.send_video(chat_id=user_id, video=FSInputFile(end_video_path), caption=f"Завершение диагностики по теме {theme.capitalize()}")
                logger.info(f"Завершающее видео для темы {theme} успешно отправлено пользователю {user_id}")
            else:
                await callback_query.message.bot.send_message(chat_id=user_id, text=f"Завершающее видео для темы {theme.capitalize()} не найдено.")
                logger.warning(f"Завершающее видео для темы {theme} не найдено для пользователя {user_id}")
        except Exception as e:
            await callback_query.message.bot.send_message(chat_id=user_id, text="Произошла ошибка при отправке завершающего видео.")
            logger.error(f"Ошибка при отправке завершающего видео для темы {theme} пользователю {user_id}: {str(e)}")
            await log_to_db("ERROR", f"Ошибка при отправке завершающего видео: {str(e)}", user_id)

        await callback_query.message.bot.send_message(chat_id=user_id, text="Диагностика завершена! Спасибо за ваши ответы. Вы можете записаться на консультацию или вернуться в главное меню.", reply_markup=get_diagnostic_result_keyboard())
        logger.info(f"Пользователь {user_id} завершил диагностику по теме {theme}")
        await state.clear()
    await callback_query.answer()