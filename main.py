from datetime import datetime as dt
import time
import requests

class CurrencyAPI:
    cache = {}

    def __init__(self, api_key, api_name):
        self.api_key = api_key
        self.api_name = api_name

    def set_to_cache(self, key, value_buy, value_sell):
        # Прив'язка ключа до дати, щоб кеш скидався 1 раз на добу.
        today = dt.now().strftime('%Y-%m-%d')
        full_key = f"{key}_{today}"

        # Видалення старих ключів із кешу.
        self.clear_old_cache()

        # Записуємо пару значень у кеш (курс купівлі та продажу).
        self.cache[full_key] = {"rateBuy": value_buy, "rateSell": value_sell}
        print(f"Додано до кешу: ключ = {full_key}, значення = rateBuy: {value_buy}, rateSell: {value_sell}\n")

    def get_from_cache(self, key):
        # Для перевірки ключа відносно поточного дня, в іншому випадку буде створюватись новий кеш для ключа
        today = dt.now().strftime('%Y-%m-%d')
        full_key = f"{key}_{today}"

        # Отримує пару значень з кешу за ключем.
        value = self.cache.get(full_key)
        if value is not None:
            return value["rateBuy"], value["rateSell"]
        else:
            print(f"Ключ '{full_key}' не знайдено в кеші.")
            return None

    def status_code(self, status_code):
        if status_code == 200:
            return True
        elif status_code == 404:
            return False
        elif status_code == 429:
            time.sleep(4)
            return False

    def clear_old_cache(self):
        today = dt.now().strftime('%Y-%m-%d')
        keys_to_delete = [k for k in self.cache if not k.endswith(f"_{today}")]
        for key in keys_to_delete:
            del self.cache[key]
            print(f"Старі ключі видалено з кешу: {key}")

    def __repr__(self):
        return f"Name api: {self.api_name}. Date: {dt.now().strftime('%Y-%m-%d')}"


class MonoAPI(CurrencyAPI):
    def __init__(self, api_key, api_name, url: str):
        super().__init__(api_key, api_name)
        self.url = url
        self.data = None

    def get_currency(self, currency: str):
        # Перевірка на наявність даних у кешу
        cached = self.get_from_cache(currency)
        if cached:
            rate_buy, rate_sell = cached
            print(f"Отримано з кешу:")
            print(f"{codes.get(currency).get('emj')} {codes.get(currency).get('name')} to 💰UAH:\nSell: {rate_sell}\nBuy: {rate_buy}\n")
            return rate_buy, rate_sell

        # Отримання даних із запиту
        if not self.data:
            try:
                response = requests.get(self.url)
            except requests.exceptions.RequestException as e:
                print(f"Помилка запиту: {e}")
                return None

            if self.status_code(response.status_code):
                self.data = response.json()                 # збереження даних у self.data
                result = self.parsing_data(currency)        # виклик методу парсингу parsing_data
                return result
            else:
                print(f"Помилка статус-коду: {response.status_code}")
                return None
        return self.parsing_data(currency)

    def parsing_data(self, currency: str):
        # Парсимо отримані дані та шукаємо курс для заданої валюти (currencyCodeA).
        for item in self.data:
            if str(item.get("currencyCodeA")) == currency:
                # Отримаємо rateBuy та rateSell
                rate_buy, rate_sell = item.get("rateBuy"), item.get("rateSell")
                # Основний варіант виводу даних на екран
                print(
                    f"{codes.get(currency).get('emj')} {codes.get(currency).get('name')} to 💰UAH:\nSell: {rate_sell}\nBuy: {rate_buy}")
                if rate_buy and rate_sell:
                    # Передаємо ключ та значення для запису у кеш
                    self.set_to_cache(currency, rate_buy, rate_sell)
                    return rate_buy, rate_sell
                else:
                    print(f"Курс не знайдено для валюти {currency}")
                    return None

        print(f"Валюта {currency} не знайдена у даних")
        return None


# Для перевірки декількох валют, та використанні у парсингу, щоб красиво виводити валюти
codes = {
    "840" : {'emj': '💵', 'name': 'USD'}
    , "978" : {'emj': '💶', 'name': 'EUR'}
    ,"8401" : {'emj': 'NoLabel', 'name': 'NoName'}
}

# Створення 2-х екземплярів класу mono та mono_b, один має створити кеш, другий повинен використати даний кеш
mono = MonoAPI(
    api_key="",
    api_name="MonoBank",
    url="https://api.monobank.ua/bank/currency"
)

mono_b = MonoAPI(
    api_key="",
    api_name="MonoBank",
    url="https://api.monobank.ua/bank/currency"
)

# Викликається метод get_currency для екземпляра, для попередньо заданих валют у codes
print("Курси Монобанку:")
for key, value in codes.items():
    rate = mono.get_currency(key)

    # Даний print закоментував, він може бути 2-м варіантом виводу даних. Основний у parsing_data
    # print(f"Курс {value.get('emj')} {value.get('name')}: {rate}")

print("*" * 50, end="\n\n")
# Викликається метод get_currency для екземпляра, для попередньо заданих валют у codes. Перевірка роботи кешу.
print("Курси Монобанку, 2-й запит:")
for key, value in codes.items():
    rate = mono_b.get_currency(key)