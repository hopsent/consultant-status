# consultant-status
Проект направлен на проверку статуса аккаунта работника консалтинговой компании
на целевом сайте.
Взаимодействие с пользователем обеспечивается через интерфейс телеграм-бота.
# технологии
python 3.8.10
selenium 4.7.2
geckodriver
python-telegram-bot 13.7 (поллинг; версия 2.0 будет на вебхуках)
# запуск
```
Запуск контейнера докер
```
sudo docker run --name consultant-status -it -p 8000:8000 -d --privileged hopsent/consultant-status:v1.07.2023
```
После запуска контейнера
```
sudo docker exec -ti consultant-status /bin/sh
dbus-run-session -- sh
echo 'somecredstorepass' | gnome-keyring-daemon --unlock
```
НЕ ВЫХОДЯ ИЗ DBUS
```
python3
import keyring as k
k.set_password()
```
Комментарий
```
наполняем хранилище данными: сервисное имя (prefix), логин и пароль
```
Запуск программы
```
ctrl-d (выход из шелла пайтона в терминал dbus)
python3 __main__.py
# хранение данных
Приложение использует чувствительные данные: логин и пароли для авторизации
на целевом сайте.
За хранение данных отвечает модуль keyring. Данные вносятся вручную.
# работа программы
```
Подготовительный этап
```
Переходим в директорию consultant-status/:
- cd consultant-status/
Запускаем вирутальное окружение:
- . venv/bin/activate
Запускаем файл __main__.py:
- venv/bin/python __main__.py
```
Комментарий
```
Включаются несколько geckodriver, которые будут работать постоянно,
пока работает файл __main__.py.
К этим драйверам программа будет обращаться каждый раз, когда
будет поступать запрос на выполнение команд из телеграма.
По умолчанию драйверы устанавливаются сразу на целевой адрес сайта.
Включается телеграм-бот, начинается polling
(периодическое обращение к серверу телеграм),
в отсутствие сообщений в адрес бота - команд - 
бот находится в режиме idle (простой).
```
Основное выполнение программы
```
Получая в телеграме команду, бот просыпается, выполняется обработка полученной команды,
а именно проверка доступности (занятости) аккаунтов на целевом сайте.
Проверка производится с использованием мультипоточности.
Доступных команд две: либо проверяем полный набор аккаунтов для проверки,
либо проверяем усеченный набор.
Каждый аккаунт инстанцируется через объект Account(). Объекты имеют свой пароль и логин.
Далее селениум эмулирует поведение человека на целевом сайте: авторизируется на сайт,
"нажимает" на элементы сайта, получает ответ сайта и выходит с сайта, занимая
снова целевой юрл.
Пайтон обрабатывает ответ, присваивает объекту Account() булевое значение атрибута
is_busy. Если при выполнении программы произошла ошибка - значение будет None (дефолтное).
Здесь пайтон выходит из мультипоточности, формируя словарь информации о статусе
аккаунтов с ключами, собирающими свободные аккаунты и ошибочные результаты.
Ответное сообщение телеграм-бота пользователю формируется с учетом содержания
значений словаря по ключу "свободные аккаунты".
Телеграм-бот отправляет сообщение в тот же чат.
Также проверяется значения по ключу словаря, отвечающему за неудачные проверки -
отправляется сообщение в телеграм-чат лица - техподдержки.
Телеграм-бот засыпает, продолжается поллинг - до следующего сообщения.
# содержание .env-файла
EXEC_PATH - локальный путь до гецкодрайвера
TOKEN - уникальный токен телеграм-бота
URL - веб-адрес целевого сайта
REGIONAL_AMOUNT - количество региональных аккаунтов
GENERAL_AMOUNT - количество общих аккаунтов
REGIONAL_PREFIX - обращение к региональным аккаунтам в хранилище keyring
GENERAL_PREFIX - обращение к общим аккаунтам в хранилище keyring
TROUBLE_CHAT_ID - ID чата техподдержки
VALID_CHAT_ID - ID целевого чата (все остальные чаты не поддерживают использование бота)
# лицензия
# автор
Алексей Кулаков