import os
import json

# Укажите путь к вашей директории с JSON файлами
directory_path = "projects/ruelderscrolls/characters_full"


def deal_with_categories():
    # Перебираем файлы в директории
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)

            # Читаем JSON файл
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

                # Преобразовываем поле "categories" в строку, разделенную запятой
                if "categories" in json_data and isinstance(json_data["categories"], list):
                    json_data["categories"] = ", ".join(json_data["categories"])

                # Записываем обновленные данные обратно в файл
                with open(file_path, 'w', encoding='utf-8') as updated_file:
                    json.dump(json_data, updated_file, ensure_ascii=False, indent=2)

    print("Обработка завершена.")

def deal_with_titles():
    # Перебираем все файлы в директории
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)

        # Проверяем, является ли файл JSON-файлом
        if os.path.isfile(filepath) and filename.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as file:
                # Загружаем JSON из файла
                data = json.load(file)

                # Проверяем наличие поля 'title' и выражения в скобках
                if 'title' in data and '(' in data['title'] and ')' in data['title']:
                    # Используем регулярное выражение для удаления выражения в скобках
                    import re
                    data['title'] = re.sub(r'\([^)]*\)', '', data['title']).strip()

            # Сохраняем изменения обратно в файл
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)


def main():
    deal_with_categories()
    deal_with_titles()
