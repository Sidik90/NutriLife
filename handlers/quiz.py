from aiogram import Router
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu, get_quiz_options
from aiogram.types import FSInputFile

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
@router.callback_query(lambda c: c.data == "quiz")
async def start_quiz(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(question_index=0, score=0)
    question = QUIZ_QUESTIONS[0]
    await callback_query.message.answer_photo(photo=FSInputFile(question["image_1"]), caption=question["text"], reply_markup=get_quiz_options(0))
    await callback_query.message.answer_photo(photo=FSInputFile(question["image_2"]))
    await state.set_state(QuizStates.QUESTION)
    await callback_query.message.delete()
    await callback_query.answer()

# Обработчик ответов на вопросы квиза
@router.callback_query(QuizStates.QUESTION, lambda c: c.data.startswith("quiz_"))
async def process_quiz_answer(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    question_index = user_data["question_index"]
    score = user_data["score"]
    answer = int(callback_query.data.split("_")[-1])
    correct_answer = QUIZ_QUESTIONS[question_index]["correct"]


    if answer == correct_answer:
        score += 1
        await callback_query.message.answer("Правильно! ✅")
    else:
        await callback_query.message.answer("Неправильно. ❌")
    await state.update_data(score=score)

    if question_index + 1 < len(QUIZ_QUESTIONS):
        await state.update_data(question_index=question_index + 1)
        question = QUIZ_QUESTIONS[question_index + 1]
        await callback_query.message.answer_photo(photo=FSInputFile(question["image_1"]), caption=question["text"], reply_markup=get_quiz_options(question_index + 1))
        await callback_query.message.answer_photo(photo=FSInputFile(question["image_2"]))
    else:
        result_text = f"Квиз завершен! Ваш результат: {score} из {len(QUIZ_QUESTIONS)}."
        await callback_query.message.answer(result_text, reply_markup=get_main_menu())
        await state.clear()
    await callback_query.message.delete()
    await callback_query.answer()