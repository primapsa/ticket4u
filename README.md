# t4u backend
***

1. Клонировать
```
 git clone https://github.com/primapsa/ticket4u.git
```

2. Создать и активировать виртуальное окружение
```
 python –m venv t4uenv
 t4uenv\Scripts\activate
```

3. Установить зависимости
```
 pip install -r requirements.txt
```

4. В ticket4uApp/settings.py настроить базу данных
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
Далее перейти в /ticket4uApp и все комнды запускать из этой папки

5. Выполнить миграции
```
 python manage.py makemigrations
 python manage.py migrate
```

6. Добавить инициализационные значения в базу данных
```
python manage.py loaddata init
```

7. Создать админа
```
python manage.py createsuperuser
```
имя пользователя и адрес электронной почты должы совпадать

```
Имя пользователя: admin@t4u.com
Адрес электронной почты: admin@t4u.com
```

8. Запустить сервер
```
python manage.py runserver
```