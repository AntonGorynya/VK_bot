# Бот для публикации комиксов во Вконтакте

Данный репозитарий представляет собой скрипт для публикации комиксов с сайта https://xkcd.com/

### Как установить

Перед установкой отредактируйте файл `./.env` в соответсвии с описанием ниже:
```
VK_TOKEN=<ваш токен>
GROUP_ID=<ID  группы>
```

Для получения токена для работы с VK  воспользуйтесь документацией которая находится по ссылке
https://dev.vk.com/api/access-token/implicit-flow-user 

Для того что бы узнать ID  группы, в которой вы собираетесь постить фото вы можете воспользоваться сервисом 
https://regvk.com/id/

После чего перейдите к установке зависимостей.

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Пример запуска

Ниже представлен пример запуска скрипта.

```
VK_bot\main.py 

Process finished with exit code 0
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).