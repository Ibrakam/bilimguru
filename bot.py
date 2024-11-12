from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.models import User
from db import get_db

router = Router()


def register_user(uid, name, phone_number):
    with next(get_db()) as db:
        user = User(uid=uid, name=name, phone_number=phone_number)
        db.add(user)
        db.commit()


def check_user(uid):
    with next(get_db()) as db:
        user = db.query(User).filter(User.uid == uid).first()
        return user


def get_all_users():
    with next(get_db()) as db:
        users = db.query(User).all()
        all_uid = [user.uid for user in users]
        return all_uid


class RegisterState(StatesGroup):
    name = State()
    phone_number = State()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    uid = message.from_user.id
    if check_user(uid):
        await message.answer_photo(FSInputFile("images/bilim-guru-logo-new.png"),
                                   "Здравствуйте это бот <b>Bilimguru</b>",
                                   parse_mode="HTML")
    else:
        await state.set_state(RegisterState.name)
        await message.answer_photo(FSInputFile("images/bilim-guru-logo-new.png"),
                                   "Здравствуйте это бот <b>Bilimguru</b>.\nДавайте познакомимся, введите ваше имя",
                                   parse_mode="HTML")


@router.message(RegisterState.name)
async def get_name_(message: Message, state: FSMContext):
    name = message.text
    await state.set_data({"name": name})
    button = [[
        KeyboardButton(text="ОТПРАВИТЬ НОМЕР ТЕЛЕФОНА☎️", request_contact=True)
    ]]
    kb = ReplyKeyboardMarkup(resize_keyboard=True,
                             keyboard=button)
    await state.set_state(RegisterState.phone_number)
    await message.answer("Ваш номер телефона?", reply_markup=kb)


@router.message(RegisterState.phone_number)
async def get_phone_num(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    uid = message.from_user.id
    data = await state.get_data()
    register_user(uid, data["name"], phone_number)
    await message.answer("Отлично!")


ADMINS = [889121031]


class BotState(StatesGroup):
    mailing = State()


@router.message(Command('admin'))
async def admin_menu(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        buttons = [
            [KeyboardButton(text="❌Отменить")]
        ]
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

        await message.answer(
            "Введите сообщение для рассылки, либо отправьте фотографии/видео с описанием",
            reply_markup=kb)
        await state.set_state(BotState.mailing)


@router.message(BotState.mailing)
async def mailing_admin(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено")
        await state.clear()
    else:
        all_users = get_all_users()
        success = 0
        unsuccess = 0
        for i in all_users:
            try:
                await message.bot.copy_message(chat_id=i, from_chat_id=message.from_user.id,
                                               message_id=message.message_id, reply_markup=message.reply_markup)
                success += 1
            except:
                unsuccess += 1
        await message.bot.send_message(message.from_user.id, f"Рассылка завершена!\n"
                                                             f"Успешно отправлено: {success}\n"
                                                             f"Неуспешно: {unsuccess}",
                                       reply_markup=ReplyKeyboardRemove())
        await state.clear()
