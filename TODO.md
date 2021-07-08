- fix cli s3 part

- обработка ошибок если фунция уже есть
- проверить на скорость сетапа приложения


- документация
  - пример простого деплоя
  - по шагам деплой с нуля
  - статья на хабре
  - чатик в телеге

- необязательно?
  - тесты на cli целиком
  - добить тесты
    - а что с multi value params?
  
#TODO nikita
- yc
  - get_gateways
  - create_gateways
  - update_gateway
  - delete_gateway
- cli
  - undeploy
- cli_helpers
  - is_valid_bucket_name (only tests)
  - is empty (only tests)
  - get slug (only tests)
  - get_bucket_name (only tests)
  - is_valid_entrypoint
  - is_valid_django_settings_module
  - is_valid_requirements_file

# РЕЛИЗ


## следующие шаги
## документация \

### примеры деплоя
- простое апи
- джанго сайт
- ангуляр + джанго апи (с авторизацией)
### ограничения 
- загловки
- базы
### пример деплоя от А до Я
- регстрация в яндексе
- настсройка сервисных аккаунтов, aws, ci
- старт джанго приложения
- деплой серверлесс
- дальше что??
- сайт с доменным именем и хттпс
## фичи
- delete s3 key
- upload_to_bucket - добавить прогресс бар
- добавление домена к api-gw
- поддержка статики через cdn
- обработка ошибок 
  - когда функция уже есть
  - когда нет прав
  - когда сломанные конфиги
    - ентрипоинт не правильный
- cli комманда rollback
- cli команда логов
- поддержка задания масштабирования
- поддержка выкладвания без пакетов и без бакета
  - мб по умолчанию такой деплой
- проверка доступов перед выкладыванием. обработка ошибок
  - с3
  - функции
- поддержка asgi
- проверка аутентификации https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
- поддержка хтмл сайтов, не только апи + загрузка на с3
- поддержка постгрес в яндексе
- вызов manage.py
## тяжелые фичи
- поддержка ассинхронных задач
- поддержка YDB в Django ORM
  


mock of s3 calls https://github.com/garnaat/placebo#usage-as-a-decorator



