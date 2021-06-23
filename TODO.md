- написать cli
- сделать тесты с выкладыванием функции
- сделать апи гейтвей

- добить тесты
    - а что с multi value params

- красивости
    - деплой переменных окружения
    - перед деплоем проверки
    - размер функции указывать
    - https://click.palletsprojects.com/en/8.0.x/setuptools/#setuptools-integration
  
- документация
  - пример простого деплоя
  - по шагам деплой с нуля
  - статья на хабре

РЕЛИЗ

- следующие шаги
    - примеры деплоя
      - простое апи
      - джанго сайт
      - ангуляр + джанго апи (с авторизацией)
    - документация 
       - ограничения (загловки)
    - поддержка asgi
    - проверка аутентификации https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
- следующие версии
    - хостинг хтмл сайтов, не только апи + загрузка на с3
    - поддержка постгрес в яндексе
    - поддержка ассинхронных задач
    - поддержка YDB в Django ORM
    - вызов manage.py
  


# тест кейсы

mock of s3 calls https://github.com/garnaat/placebo#usage-as-a-decorator

- different frameworks (flask, fastapi, django)
    - /, /route, /route/route2, /route/<param>
    - query args (get)
    - post
    - patch, put

