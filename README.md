# Simple and Easy serverless deploy of python web-apps Yandex Cloud

1. create account at Yandex Cloud
2. use Yappa:

```shell
$ yappa setup
$ yappa deploy
 ``` 

## that's it!

# Аутентификация в Yandex Cloud

Первоначальный шаг настройки доступа - команда:

```shell 
$ yappa setup
``` 

У вас спросят OAuth токен, после yappa создаст сервисный аккаунт и сохранит его ключ доступа в файл .yc. Также на этом
она сохранит айди облачного каталога в файл конфигурации

разъянить откуда берутся и зачем нужны token, folder_id, .yc

### limitations

- installing grpcio on Apple M1