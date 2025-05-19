# PlainProject
Проект: Система управления бизнесом (Упрощённая версия)
![GitHub top language](https://img.shields.io/github/languages/top/Mike0001-droid/FinallyProject)
<!--Установка-->
## Установка 
У вас должны быть установлены [зависимости проекта](https://github.com/Mike0001-droid/FinallyProject/blob/main/requirements.txt)

1. Клонирование репозитория 

```git clone https://github.com/Mike0001-droid/FinallyProject.git```

2. Переход в директорию finally_project

```cd finally_project```

3. Создание виртуального окружения

```python -m venv venv```

4. Активация виртуального окружения

```cd venv/scripts/activate```

5. Установка зависимостей

```pip install -r requirements.txt```

6. Запуск миграций

```python manage.py migrate```

7. Создание админа

```python manage.py createsuperuser```

8. Запуск сервера

```python manage.py runserver```

## Документация по API

1. API DRF 
    * Запускаем сервер Django
    * Переходим по адресу /api
        ![alt text](readme_images/image.png)
    * Здесь мы можем тестировать эндпоинты. Давайте разберем набор эндпоинтов, связанных с выставлением оценок (Evaluations)
        ![alt text](readme_images/evaluations.png)
    * Чтобы протестировать запрос на получение всех записей данной таблицы, необходимо нажать зеленую кнопку Interact
        ![alt text](readme_images/evaluation-list.png)
    * Теперь нажимаем синюю кнопку Send Request и получаем результат
        ![alt text](readme_images/evaluation-result.png)
    * Самое интересное происходит, когда мы пытаемся добавить оценку
        ![alt text](readme_images/evaluation-create.png)
    * Заполнив все поля, мы получаем ошибку, связанную с авторизацией. Всё верно, оценки может ставить только администратор
    * Таким образом мы подходим к процессу авторизации


2. Авторизация по JWT - токену
    * Запускаем сервер Django
      
    * Переходим по адресу /api
      
    * Открываем приложение token и нажимаем на запрос create_token 
        ![alt text](readme_images/create-token.png)
      
    * Вводим свои данные и нажимаем синюю кнопку Send Request и копируем access токен из результата
        ![alt text](readme_images/response-token.png)
      
    * В нижнем левом углу нажимаем на вкладку Authentication и нажимаем на token
        ![alt text](readme_images/token-button.png)
   
    * Записываем в поле Scheme - Bearer, а в поле Token вставляем скопированный токен, затем нажимаем синюю кнопку Use Token Authentication
      
        ![alt text](readme_images/token-insert.png)
      
    * Возвращаемся к созданию оценки
      
        ![alt text](readme_images/evaluation-create.png)
      
    * После авторизации получаем вот такой результат
      
        ![alt text](readme_images/evaluation-success.png)


3. Календарь встреч
    * Переходим по адресу /calendar
        ![alt text](readme_images/calendar.png)
    * Здесь мы наблюдаем месячный вид наших встреч. Попробуем перейти на дневной вариант
        ![alt text](readme_images/day_calendar.png)
    * Здесь мы можем узнать подробную информацию о встрече, нажав кнопку "Подробнее"
        ![alt text](readme_images/detailed_data.png)
    * Так же можем удалить встречу. После нажатия нас перекидывает в админку, в которой мы можем произвести удаление
        ![alt text](readme_images/delete_meeting.png)
