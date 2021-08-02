# raw function with Postgres connection 

for more details on how to set up serverless connection to
Postgres go to [YandexCloud docs](https://cloud.yandex.ru/docs/functions/operations/database-connection)

before deployment, you should manually create:
- postgres cluster 
- postgres connection to serverless function 
- service account (and add its id to yappa.yaml)

then run:
```shell 
$ yappa setup 
$ yappa deploy 
```

after you code is updated run 
```shell 
$ yappa deploy 
```