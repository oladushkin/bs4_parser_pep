# BS4_PARSER_PEP

BS4_PARSER_PEP - парсер для сбора информации, ссылок на документацию, версиях и авторов версий языка Python,
сбор данных о статусах PEP и вывод общего количества.
Так же у паресера есть два режима вывода исобранной информации, вывод в консоль или запись в фаль с расширением .csv.

---

## Установка

1. Скачиваем репозиторий:
    `git clone git@github.com:yandex-praktikum/bs4_parser_pep.git`
2. Создаем окружающее окружение:
    `python -m venv venv`
3. Устанавливаем зависимости:
    `pip install -r requirements.txt`

---

## Команды парсера

1. Вывод общих комманд
     `python main.py -h`
2. Whats-new
    + `python main.py whats-new -o file` - Запишет результат в файл,
                                         ссылка на описания обновления, версию и автора.
    + `python main.py whats-new -o pretty` - выведет таблицу в консоль.
3. Latest-versions
    + `python main.py latest-versions -o file` - Запишет результат в файл,
                                               статусе разработки и ссылке на документацию.
    + `python main.py latest-versions -o pretty` - вывведет таблицу в консоль.
4. PEP
    + `python main.py pep -o file` - Запишет результат в файл, 
                                   статус PEP их количество и общее количество.
    + `python main.py pep -o pretty` - вывведет таблицу в консоль.

---

## Сылки на документацию

1. [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/)
2. [prettytable 2.1.0](https://pypi.org/project/prettytable/2.1.0/)
3. [requests-cache](https://requests-cache.readthedocs.io/en/stable/index.html)
4. [tqdm](https://pypi.org/project/tqdm/4.61.0/)

---

## Автор

Шелепин дмитрий|[GitHub](https://github.com/oladushkin)