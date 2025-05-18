from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_quiz_options, get_main_menu
from utils.logger import logger

router = Router()

# Определение состояний для квиза
class QuizStates(StatesGroup):
    QUESTION = State()

# Вопросы и правильные ответы для квиза
QUIZ_QUESTIONS = [
    {"text": "Какой продукт полезнее для завтрака?", "correct": 1, "image_1": "data/images/quiz/question_1_option_1.jpg", "image_2": "data/images/quiz/question_1_option_2.jpg"},
    {"text": "Что лучше пить утром?", "correct": 2, "image_1": "data/images/quiz/question_2_option_1.jpg", "image_2": "data/images/quiz/question_2_option_2.jpg"},
    {"text": "Какой перекус полезнее?", "correct": 1, "image_1": "data/images/quiz/question_3_option_1.jpg", "image_2": "data/images/quiz/question_3_option_2.jpg"},
    {"text": "Что лучше для ужина?", "correct": 2, "image_1": "data/images/quiz/question_4_option_1.jpg", "image_2": "data/images/quiz/question_4_option_2.jpg"},
    {"text": "Какой продукт богат белком?", "correct": 1, "image_1": "data/images/quiz/question_5_option_1.jpg", "image_2": "data/images/quiz/question_5_option_2.jpg"},
]

# Обработчик выбора "Сыграть в квиз"
@router.callback_query(F.data == "quiz")
async def start_quiz(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} начал квиз")
    await state.update_data(question_index=0, score=0)
    question = QUIZ_QUESTIONS[0]
    try:
        await callback_query.message.bot.send_photo(chat_id=user_id, photo=FSInputFile(question["image_1"]), caption=question["text"], reply_markup=get_quiz_options(0))
        await callback_query.message.bot.send_photo(chat_id=user_id, photo=FSInputFile(question["image_2"]))
    except FileNotFoundError:
        await callback_query.message.bot.send_message(chat_id=user_id, text=f"{question['text']} (Изображения не найдены, используйте воображение!)", reply_markup=get_quiz_options(0))
    await state.set_state(QuizStates.QUESTION)
    await callback_query.answer()


# Обработчик ответов на вопросы квиза
@router.callback_query(QuizStates.QUESTION, F.data.startswith("quiz_"))
async def process_quiz_answer(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    question_index = data.get("question_index", 0)
    score = data.get("score", 0)
    answer = int(callback_query.data.split("_")[-1])
    correct_answer = QUIZ_QUESTIONS[question_index]["correct"]

    if answer == correct_answer:
        score += 1
        await callback_query.message.edit_caption(caption="Правильно! ✅")
        logger.info(f"Пользователь {user_id} ответил правильно на вопрос {question_index + 1}")
    else:
        await callback_query.message.edit_caption(caption="Неправильно. ❌")
        logger.info(f"Пользователь {user_id} ответил неправильно на вопрос {question_index + 1}")

    question_index += 1
    await state.update_data(question_index=question_index, score=score)

    if question_index < len(QUIZ_QUESTIONS):
        question = QUIZ_QUESTIONS[question_index]
        try:
            await callback_query.message.bot.send_photo(chat_id=user_id, photo=FSInputFile(question["image_1"]),
                                                        caption=question["text"],
                                                        reply_markup=get_quiz_options(question_index))
            await callback_query.message.bot.send_photo(chat_id=user_id, photo=FSInputFile(question["image_2"]))
        except FileNotFoundError:
            await callback_query.message.bot.send_message(chat_id=user_id,
                                                          text=f"{question['text']} (Изображения не найдены, используйте воображение!)",
                                                          reply_markup=get_quiz_options(question_index))
    else:
        await callback_query.message.bot.send_message(chat_id=user_id,
                                                      text=f"Квиз завершен! Ваш результат: {score}/{len(QUIZ_QUESTIONS)} 🎉",
                                                      reply_markup=get_main_menu())
        logger.info(f"Пользователь {user_id} завершил квиз с результатом {score}/{len(QUIZ_QUESTIONS)}")
        await state.clear()
    await callback_query.answer()