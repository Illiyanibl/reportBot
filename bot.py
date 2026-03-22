import json
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from MainReport import MainReport

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Доступные команды:\n"
        "/getReport [{\"login\":\"...\",\"password\":\"...\",\"start_year\":2023,"
        "\"end_year\":2024,\"start_month\":1,\"end_month\":12,"
        "\"url\":\"...\",\"action\":\"create_json\"}]\n\n"
        "Параметр action необязателен, по умолчанию create_json."
    )


async def get_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Всё после команды — это JSON
    raw = update.message.text.partition(" ")[2].strip()

    if not raw:
        await update.message.reply_text(
            "Передайте параметры в формате JSON после команды.\n"
            "Пример: /getReport {\"login\":\"user\",\"password\":\"pass\","
            "\"start_year\":2023,\"end_year\":2024,"
            "\"start_month\":1,\"end_month\":12,\"url\":\"https://example.com\"}"
        )
        return

    try:
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        await update.message.reply_text(f"Ошибка парсинга JSON: {e}")
        return

    required = ["login", "password", "start_year", "end_year",
                "start_month", "end_month", "url"]
    missing = [f for f in required if f not in params]
    if missing:
        await update.message.reply_text(
            f"Не хватает обязательных параметров: {', '.join(missing)}"
        )
        return

    await update.message.reply_text("⏳ Генерирую отчёт, подождите...")

    try:
        result = MainReport.start(
            login=params["login"],
            password=params["password"],
            start_year=params["start_year"],
            end_year=params["end_year"],
            start_month=params["start_month"],
            end_month=params["end_month"],
            url=params["url"],
            action=params.get("action", "create_json"),
        )
    except Exception as e:
        logger.exception("Ошибка при выполнении MainReport.start")
        await update.message.reply_text(f"Ошибка при выполнении отчёта: {e}")
        return

    if result is None:
        await update.message.reply_text("✅ Отчёт выполнен, файл не был создан.")
    else:
        # result — путь к файлу (str) или байты (bytes)
        try:
            if isinstance(result, (str, bytes)):
                if isinstance(result, str):
                    with open(result, "rb") as f:
                        file_data = f.read()
                    filename = result.split("/")[-1]
                else:
                    file_data = result
                    filename = "report.xlsx"

                await update.message.reply_document(
                    document=file_data,
                    filename=filename,
                    caption="✅ Отчёт готов!"
                )
            else:
                await update.message.reply_text(
                    f"✅ Отчёт выполнен. Результат: {result}"
                )
        except Exception as e:
            logger.exception("Ошибка при отправке файла")
            await update.message.reply_text(f"Ошибка при отправке файла: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Доступные команды:\n\n"
        "/start — приветствие\n"
        "/help — список команд\n"
        "/getReport {JSON} — запустить отчёт\n\n"
        "Параметры JSON для /getReport:\n"
        "  login       — логин (обязательно)\n"
        "  password    — пароль (обязательно)\n"
        "  start_year  — начальный год (обязательно)\n"
        "  end_year    — конечный год (обязательно)\n"
        "  start_month — начальный месяц (обязательно)\n"
        "  end_month   — конечный месяц (обязательно)\n"
        "  url         — URL (обязательно)\n"
        "  action      — действие (необязательно, по умолчанию create_json)"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("getReport", get_report))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
