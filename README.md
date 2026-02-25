# ValutaTrade Hub

Консольное приложение для ведения простого крипто/фиат портфеля и работы с курсами валют.
Проект состоит из двух частей:
1. **Core Service** — регистрация/логин, портфель, покупка/продажа, расчёт стоимости.
2. **Parser Service** — загрузка актуальных курсов из внешних API, сохранение в локальный кеш `data/rates.json` и ведение истории `data/exchange_rates.json`.

## Возможности

### Core Service
- `register` — регистрация пользователя
- `login` — вход
- `show-portfolio` — показать портфель и итоговую стоимость в базовой валюте
- `buy` / `sell` — покупка/продажа валюты (кошелёк создаётся автоматически при первой покупке)
- `get-rate` — получить курс пары (читает из локального кеша `data/rates.json`, учитывает TTL)

### Parser Service
- `update-rates` — обновить курсы из CoinGecko и/или ExchangeRate-API, записать кеш и историю
- `show-rates` — показать кеш курсов с фильтрацией (`--currency`, `--top`, `--base`)
- `scheduler` — периодически обновлять курсы по таймеру

## Требования
- Python 3.11+ (рекомендуется 3.12)
- Poetry

## Начало работы

1. Установка.
```bash
make install
```
2. Проверка линтера.
```bash
make lint
```
3. Сборка пакета.
```bash
make build
```
4. Установка собранного пакета локально (для запуска команды project без poetry run).
```bash
make package-install
```

## Запуск CLI

Через Poetry:
```bash
poetry run project --help
```

После make package-install можно так:
```bash
project --help
```

## Базовый сценарий (Core)

1. Регистрация и логин.
```bash
poetry run project register --username alice --password 1234
poetry run project login --username alice --password 1234
```
2. Покупка валюты.
```bash
poetry run project buy --currency BTC --amount 0.01
```
3. Просмотр портфеля.
```bash
poetry run project show-portfolio --base USD
```
4. Продажа.
```bash
poetry run project sell --currency BTC --amount 0.005
```
5. Получение курса.
```bash
poetry run project get-rate --from BTC --to USD
```

## Parser Service: ключи и конфигурация

Проект использует 2 внешних API:
1. CoinGecko — для криптовалют (публичный доступ без ключа).
2. ExchangeRate-API — для фиатных валют (нужен API-ключ).

### Хранение ключа

**Ключ нельзя коммитить в GitHub.**
Ключ берётся из переменной окружения EXCHANGERATE_API_KEY.

Рекомендуемый способ — .env в корне проекта:
1. Создайте файл .env (он должен быть в .gitignore).
```bash
EXCHANGERATE_API_KEY=ваш_ключ_сюда
```
2. Убедитесь, что в репозитории есть файл-шаблон .env.example.
```bash
EXCHANGERATE_API_KEY=your_key_here
```

### Сценарий при отсутствии ключа

Если .env нет и переменная окружения не задана:
- `update-rates --source all` может завершиться ошибкой для ExchangeRate-API,
- `update-rates --source coingecko` будет работать без ключа,
- Core-команды будут работать, но курс для фиатных пар может быть недоступен без обновления из ExchangeRate-API.

### Команды Parser Service

#### Обновить курсы (update-rates)

1. Обновить всё.
```bash
poetry run project update-rates --source all
```
2. Обновить только крипту (CoinGecko).
```bash
poetry run project update-rates --source coingecko
```
3. Обновить только фиат (ExchangeRate-API).
```bash
poetry run project update-rates --source exchangerate
```

После выполнения обновляется:
- data/rates.json — кеш последних курсов,
- data/exchange_rates.json — история обновлений (журнал).

#### Показать курсы (show-rates)

1. Показать всё из кеша.
```bash
poetry run project show-rates
```
2. Показать только одну валюту.
```bash
poetry run project show-rates --currency BTC
```
3. Показать топ-N (по стоимости) криптовалют.
```bash
poetry run project show-rates --top 2
```
4. Показать курсы относительно другой базы.
```bash
poetry run project show-rates --base EUR
```
5. Комбинация фильтров.
```bash
poetry run project show-rates --currency BTC --base EUR
poetry run project show-rates --top 2 --base GBP
```

#### Планировщик (scheduler)

Запуск обновления по таймеру (Ctrl+C чтобы остановить).
```bash
poetry run project scheduler --interval 10 --source coingecko
```

## Логи

Логи пишутся в `logs/app.log`.

В логах фиксируются:
- действия пользователя (buy/sell/get-rate и т.д.),
- шаги парсера (обновление, ошибки API, успешные запросы).

## Файлы данных

Папка data/ используется как хранилище (локальная БД):
1. data/users.json — пользователи.
2. data/portfolios.json — портфели.
3. data/session.json — текущая сессия.
4. data/rates.json — кеш курсов для Core Service (последние значения и метаданные).
5. data/exchange_rates.json — история обновлений Parser Service

**Файлы data/*.json не должны коммититься, поэтому они включены в .gitignore.**

## Структура проекта (кратко)

1. src/finalproject_1_perfilova/core/ — бизнес-логика (модели, usecases, исключения).
2. src/finalproject_1_perfilova/infra/ — настройки и работа с файловым хранилищем.
3. src/finalproject_1_perfilova/parser_service/ — клиенты API, обновление курсов, storage, планировщик.
4. src/finalproject_1_perfilova/cli/ — CLI (argparse).
5. logs/ — логи.
6. data/ — данные (локальные json-файлы).

## Демо (asciinema)

Запись демонстрации работы программы: https://asciinema.org/a/b7zJqm8COes0p6qE

В записи показано:
1. Core: register, login, buy, sell, show-portfolio, get-rate.
2. Parser: `update-rates --source all`, `show-rates` (с фильтрами), scheduler (10 сек) и остановка (Ctrl+C).
3. Ошибки: неизвестная валюта, недостаточно средств.