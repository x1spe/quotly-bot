import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# Токен берём из переменных среды Render
TOKEN = os.environ.get("8437665636:AAFMObavl2iNYRSLMIRsSbuF7Ge6ZeakE9g")
if not TOKEN:
    raise ValueError("Не указан токен бота. Добавьте переменную среды TOKEN в Render.com")

def create_quote_image(text: str, width=600, height=400) -> io.BytesIO:
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    margin = 20
    max_width = width - 2 * margin

    # Разбиваем текст на строки по ширине картинки
    lines = []
    for line in text.splitlines():
        wrapped = textwrap.wrap(line, width=40)
        lines.extend(wrapped)

    # Подгоняем размер шрифта, если текст не помещается по высоте
    while True:
        line_heights = sum([draw.textsize(line, font=font)[1] for line in lines])
        if line_heights + margin * 2 <= height:
            break
        font_size = font.size - 1
        if font_size < 10:
            break
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    y = (height - line_heights) // 2
    for line in lines:
        line_width, line_height = draw.textsize(line, font=font)
        x = (width - line_width) // 2
        draw.text((x, y), line, fill=(0, 0, 0), font=font)
        y += line_height

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def quotly_command(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        text = update.message.reply_to_message.text
        if not text:
            update.message.reply_text("Невозможно создать цитату из медиа.")
            return
        image_buffer = create_quote_image(text)
        update.message.reply_photo(photo=image_buffer)
    else:
        update.message.reply_text("Ответьте на сообщение, чтобы создать цитату.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("q", quotly_command))

    print("Бот запущен...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

