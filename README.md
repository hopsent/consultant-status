# consultant-status
Проект направлен на проверку статуса аккаунта работника консалтинговой компании
на целевом сайте: занят аккаунт или свободен.
Взаимодействие с пользователем обеспечивается через интерфейс телеграм-бота.
# технологии
- python 3.8.10
- selenium 4.10
- geckodriver
- python-telegram-bot 13.7
- предварительно подготовленный сервер
# забираем докер-образ
- sudo docker image pull hopsent/consultant-status:v6.02.2025
# запуск
```
Запускаем контейнер докер (вместо example укажите ваш порт)
```
- sudo docker run --name consultant-status -p example:example --shm-size 10g -it -d --privileged hopsent/consultant-status:v6.02.2025
```
Копируем предварительно подготовленный файл .env в докер-контейнер вот этой командой (вместо example укажите путь к файлу)
```
- sudo docker cp example consultant-status:/app/
```
После запуска контейнера и копирования .env
```
- sudo docker exec -ti consultant-status /bin/sh
- dbus-run-session -- sh
- echo 'somecredstorepass' | gnome-keyring-daemon --unlock
```
НЕ ВЫХОДЯ ИЗ DBUS определяем данные аккаунтов (логин+пароль)
значение prefix принимается в соответствии с файлом .env.
Данные для списка credentials подгатавливаем заранее!
```
- python3
- import keyring as k
- credentials = [('prefixпорядковыйномер', 'логин', 'пароль'), ...]
- for cr in credentials:
-     k.set_password(cr[0], cr[1], cr[2])
```
Выполняем код выше нажатием Enter (дважды!!)
```
```
Запуск программы
```
- ctrl-d (выход из шелла пайтона в терминал dbus)
- python3 __main__.py
# хранение данных
Приложение использует чувствительные данные: логин и пароли для авторизации
на целевом сайте.
За хранение данных отвечает модуль keyring. Данные вносятся вручную.
# работа программы
```
После запуска __main__.py
```
Включаются несколько окон Firefox на geckodriver, которые будут работать постоянно,
пока работает __main__.py.
К этим окнам программа будет обращаться каждый раз, когда
будет поступать запрос на выполнение команд из телеграм-бота.
По умолчанию каждое окно устанавливается на адрес сайта.
Включается телеграм-бот, создается сервер WebHook и
в отсутствие сообщений в адрес бота - команд - 
бот находится в режиме idle (простой).
```
Основное выполнение программы
```
Получая в телеграме команду, бот просыпается, выполняется проверка доступности (занятости) аккаунтов на целевом сайте: логин, клики по элементам, сбор результата, логаут.
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
- EXEC_PATH - локальный путь до гецкодрайвера
- TOKEN - уникальный токен телеграм-бота
- URL - веб-адрес целевого сайта
- REGIONAL_AMOUNT - количество региональных аккаунтов
- GENERAL_AMOUNT - количество общих аккаунтов
- REGIONAL_PREFIX - обращение к региональным аккаунтам в хранилище keyring
- GENERAL_PREFIX - обращение к общим аккаунтам в хранилище keyring
- TROUBLE_CHAT_ID - ID чата техподдержки
- VALID_CHAT_ID - ID целевого чата (все остальные чаты не поддерживают использование бота)
- SERVER_ADDRESS - адрес хоста
- LISTEN - локальный адрес, который слушает бот-сервер
- SERVER_ADDRESS - доменное имя сервера
- PORT - один из внешних портов SSL, на которых работает телеграм
- SERVER_PORT - один из внутренних портов, на который сервер пробрасывает запрос телеграм
# лицензия
# автор
Алексей Кулаков