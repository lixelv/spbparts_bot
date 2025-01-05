import time
import logging
from config import avito, prepared_texts, SLEEP_SEC

logging.basicConfig(level=logging.INFO)
logs_path = "/avito-bot.txt"
file_handler = logging.FileHandler(logs_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)

if __name__ == "__main__":
    while True:
        try:
            last_chat = avito.get_chats()[0]
            last_chat_messages = avito.get_messages(last_chat["id"])["messages"]

            if len(last_chat_messages) == 1:
                for text in prepared_texts:
                    avito.send_message(last_chat["id"], text)

        except Exception as e:
            print("Ошибка:", e)

        time.sleep(SLEEP_SEC)
