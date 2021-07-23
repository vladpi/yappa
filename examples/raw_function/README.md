# raw function deployment 
you can deploy raw function with Yappa. In this case Yappa handles 
preparing and uploading package to S3 and creation of new function version. Be aware 
at this point Yappa makes function available publicly.

- function.py - basic serverless function 
- yappa.yaml - generated Yappa config 

to deploy it to yandex cloud just run:
```shell 
$ yappa setup 
$ yappa deploy 
```

after you code is updated run 
```shell 
$ yappa deploy 
```