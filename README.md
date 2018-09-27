## Запуск проекта

```
$ docker-compose -f local.yml build

$ docker-compose -f local.yml up
```

## Фикстуры

```
$ docker-compose -f local.yml run --rm django python manage.py loaddata auth_user loans_company loans_borrower loans_offer loans_creditrequest
```

## Пользователи
Если вы загрузили фикстуры, то в системе будут доступны 5 пользователей:

Логин | Пароль | Роль
----- | ------ | ----
admin | admin | superuser
partner | partner | Сотрудник Партнера
partner2 | partne2 | Сотрудник Партнера2
credit_company | credit_company | Сотрудник кредитной организации
credit_company2 | credit_company2 | Сотрудник кредитной организации 2

## API
доступно по [ссылке](http://0.0.0.0:8000/api/)

## Тесты
```
$ docker-compose -f local.yml run --rm django python manage.py test api
```

