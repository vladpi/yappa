# raw function with Postgres connection

for more details on how to set up serverless connection to Postgres go
to [YandexCloud docs](https://cloud.yandex.ru/docs/functions/operations/database-connection) 

## Postgres Setup 
before deployment, you should manually create:

- postgres cluster
- postgres connection to serverless function
- service account (and add its id to yappa.yaml)

### 1. Create Postgres cluster
First you should create managed Postgres cluster. Go to your
folder at YandexCloud console and set it up :)

Don't forget to check "access from serverless" option in cluster settings
### 2. Create serverless connection
Python app will not have access to db directly. It will use
[Odyssey connection manager](https://github.com/yandex/odyssey).
So you should create connection from YandexCloud console
(Folder -> Cloud Functions -> DB Connection).

### 3. Create service account
Create service account which will be associated with serverless
function.
- go to YandexCloud console, Folder -> Service Accounts
- create service account
- add permission 'serverless.mdbProxies.user'

### 4. Configure yappa.yaml
(if you don't have yappa.yaml file yet, run $ yappa setup && yappa deploy)

add id of service account to the yappa.yaml file
```yaml
...
service_account_id: ajek47377f918mdmmqha
```

## Deploy 

then run:

```shell 
$ yappa setup 
$ yappa deploy 
```

## Update
after you code is updated run

```shell 
$ yappa deploy 
```