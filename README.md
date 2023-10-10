# t4u backend
***
1. Клонировать
```
 git clone https://github.com/primapsa/ticket4u.git
```
Далее перейти в /ticket4uApp и все комнды запускать из этой папки

2. Установить зависимости
```
 pip install -r requirements.txt
```
3. В ticket4uApp/settings.py настроить базу данных
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
4. Выполнить миграции
```
 python manage.py makemigrations
 python manage.py migrate
```

5. Добавить инициализационные значения в базу данных
```
python manage.py loaddata init
```
6. Создать админа
```
python manage.py createsuperuser
```

7. Запустить сервер
```
python manage.py runserver
```