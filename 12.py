import csv
import hashlib

# ============ ЧАСТЬ 1 ============
# Шаг 1.1 – подготовка исходной матрицы данных
raw_deliveries = [
    ["code", "title", "category", "qty", "price"],
    [" sw-01 ", "Коммутатор: 24 порта", "Сеть", "4", "12500"],
    ["srv-02", "Сервер стоечный", "Серверы", "2", "95000"],
    ["cab-03", "Патч-корд 5м", "Сеть", "20", "ошибка_цены"],
    ["ups-04", "ИБП модульный; 3000VA", "Питание", "3", "32000"],
    [" srv-05 ", "Дисковая полка", "Серверы", "1", "64000"]
]

# Шаг 1.2 – экспорт матрицы в CSV-файл
with open("incoming_stock.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerows(raw_deliveries)

# Шаг 1.3 – потоковое чтение и извлечение заголовка
with open("incoming_stock.csv", "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f, delimiter=";")
    header = next(reader)
    loaded_rows = list(reader)

print(f"Шапка таблицы: {header} | Строк данных: {len(loaded_rows)}")

# ============ ЧАСТЬ 2 ============
# Шаг 2.1 – валидация строк в цикле и нормализация данных
clean_items = []
quarantine_log = []

for row in loaded_rows:
    try:
        qty = int(row[3])
        price = int(row[4])
        code = row[0].strip().upper()
        title = row[1].strip()
        category = row[2].strip()
        total = qty * price
        clean_items.append({
            "code": code,
            "title": title,
            "category": category,
            "qty": qty,
            "price": price,
            "total": total
        })
    except ValueError:
        quarantine_log.append(row[0].strip())

print(f"Принято позиций: {len(clean_items)} | В карантине (ошибка данных): {quarantine_log}")

# Шаг 2.2 – сортировка списка словарей по ключу
clean_items.sort(key=lambda x: x["total"], reverse=True)
leader = clean_items[0]
print(f"Лидер по стоимости: {leader['code']} ({leader['title']}) -> {leader['total']} руб.")

# Шаг 2.3 – фильтрация крупных поставок
priority_codes = []
for item in clean_items:
    if item["total"] > 60000:
        priority_codes.append(item["code"])
print(f"Крупные поставки (>60000 руб.): {priority_codes}")

# Шаг 2.4 – агрегация расходов по категориям
category_totals = {}
for item in clean_items:
    cat = item["category"]
    category_totals[cat] = category_totals.get(cat, 0) + item["total"]
print(f"Сводка по категориям: {category_totals}")

# ============ ЧАСТЬ 3 ============
# Шаг 3.1 – проверка перехвата ошибки отсутствующего файла
try:
    with open("backup_archive.csv", "r", encoding="utf-8") as f:
        pass
except FileNotFoundError:
    print("Проверка защиты: файл backup_archive.csv не найден, работа продолжена")

# Шаг 3.2 – выгрузка чистой базы через DictWriter
fields = ["code", "title", "category", "qty", "price", "total"]
with open("verified_stock.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
    writer.writeheader()
    writer.writerows(clean_items)

# Шаг 3.3 – сквозной тест Round-Trip и проверка через assert
restored_items = []
with open("verified_stock.csv", "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        row["qty"] = int(row["qty"])
        row["price"] = int(row["price"])
        row["total"] = int(row["total"])
        restored_items.append(row)

assert clean_items == restored_items
print(f"Тест целостности Round-Trip: УСПЕШНО ({len(clean_items)} из {len(clean_items)} записей идентичны)")

# Шаг 3.4 – вычисление цифрового отпечатка SHA-256
with open("verified_stock.csv", "rb") as bf:
    file_hash = hashlib.sha256(bf.read()).hexdigest()
print(f"Контрольная сумма SHA-256 (первые 16 симв.): {file_hash[:16]}")

