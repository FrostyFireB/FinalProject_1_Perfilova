import logging
from datetime import datetime, timezone

from finalproject_1_perfilova.core.exceptions import ApiRequestError
from finalproject_1_perfilova.parser_service.storage import RatesStorage


class RatesUpdater:
    def __init__(self, clients: list, storage: RatesStorage):
        self.clients = clients
        self.storage = storage

    def run_update(self):
        """
        Возвращает количество курсов (пар), которые записали в snapshot.
        """
        logging.info("Старт обновления курсов...")

        all_rates: dict[str, tuple[float, str]] = {}
        errors = 0

        for client in self.clients:
            name = client.__class__.__name__

            if "CoinGecko" in name:
                src = "CoinGecko"
            elif "ExchangeRate" in name:
                src = "ExchangeRate-API"
            else:
                src = name

            try:
                rates = client.fetch_rates()

                count = 0
                for pair, rate in rates.items():
                    all_rates[pair] = (float(rate), src)
                    count += 1

                logging.info(f"Получение из {src}... OK ({count} курсов)")
            
            except ApiRequestError as e:
                errors += 1
                logging.error(f"Ошибка получения из {src}: {e}")

        now = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )


        history_records = []
        for pair, (rate, src) in all_rates.items():
            rec = {
                "id": self.storage.make_id(pair, now),
                "from_currency": pair.split("_")[0],
                "to_currency": pair.split("_")[1],
                "rate": rate,
                "timestamp": now,
                "source": src,
                "meta": {},
            }
            history_records.append(rec)


        pairs = {}
        for pair, (rate, src) in all_rates.items():
            pairs[pair] = {"rate": rate, "updated_at": now, "source": src}

        self.storage.append_history(history_records)
        self.storage.write_snapshot(pairs, last_refresh=now)

        if errors:
            logging.info("Обновление завершено с ошибками. Подробности в логах.")
        else:
            logging.info("Обновление завершено успешно.")

        return len(pairs)