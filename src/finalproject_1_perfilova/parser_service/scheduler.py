import logging
import time

from finalproject_1_perfilova.core.exceptions import ApiRequestError
from finalproject_1_perfilova.parser_service.updater import RatesUpdater


class RatesScheduler:
    """
    Планировщик (scheduler) для Parser Service.

    1. Раз в N секунд вызывает обновление курсов через RatesUpdater.
    2. Останавливается по Ctrl+C.
    """

    def __init__(self, updater: RatesUpdater):
        self.updater = updater

    def run_forever(self, interval_seconds: int = 300):
        if not isinstance(interval_seconds, int) or interval_seconds <= 0:
            raise ValueError("interval_seconds должен быть целым числом > 0")

        logging.info(f"Планировщик запущен. Интервал: {interval_seconds} сек.")
        try:
            while True:
                started_at = time.time()
                try:
                    updated = self.updater.run_update()
                    logging.info(f"Обновление выполнено. Обновлено курсов: {updated}.")
                except ApiRequestError as e:
                    logging.error(f"Ошибка при обновлении курсов: {e}")
                except Exception as e:
                    logging.exception(f"Непредвиденная ошибка планировщика: {e}")

                elapsed = time.time() - started_at
                sleep_for = interval_seconds - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)
        except KeyboardInterrupt:
            logging.info("Планировщик остановлен пользователем (Ctrl+C).")
            print("Планировщик остановлен.")