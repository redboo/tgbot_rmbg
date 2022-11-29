"""Bot for removing backgrounds in images."""
import gc
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from environs import Env
from rembg import remove

env = Env()
env.read_env()
bot = Bot(token=env.str("BOT_TOKEN"))
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message) -> None:
    """
    Send welcome message to the user.

    :param message: message from the user
    """
    await message.reply(
        """
    Привет! Я бот, который удаляет задний фон с изображений.
    Просто закинь мне изображение и я сам с ним разберусь."""
    )


@dp.message_handler(content_types=ContentType.PHOTO)
async def photo_handler(message: types.Message) -> None:
    """
    Download the photo, remove the background, and send the result back.

    :param message: message from the user
    """
    photo: types.PhotoSize | None = message.photo[-1]
    if photo:
        unique_id: str = photo.file_unique_id
        input_path = f"./images/{unique_id}.jpg"
        output_path = f"./images/{unique_id}.output.png"
        await photo.download(destination_file=input_path)

        with open(input_path, "rb") as i:
            with open(output_path, "wb") as o:
                input = i.read()
                output = remove(input)
                o.write(output)  # type: ignore

        await message.reply_document(types.InputFile(output_path))
        os.remove(input_path)
        os.remove(output_path)
        gc.collect()


@dp.message_handler(content_types=ContentType.ANY)
async def type_error(message: types.Message) -> None:
    """
    This function sends a message to the user if the file is not an image.

    :param message: message from the user
    """
    answer_message = "Загрузи изображение с включенной функцией компрессии."
    await message.answer(answer_message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
    gc.collect()
