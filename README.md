# Амплифер

Программа собирает статистику в социальных сетях Instagram, ВКонтакте и Facebook.        
        
Выдает ID самых активных участников, которые часто лайкают, репостят и комментируют посты.        

По умолчанию:  
Статистика из Instagram считается за 3 месяца.  
Статистика из ВКонтакте считается за 2 недели.  
В статистике из ВКонтакте только комментаторы, которые лайкали посты.  
В статистике из Facebook есть все комментаторы и все реакции на посты за последний месяц.  


### Как запустить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
   
Запустите `smm_analyze.py` указав одну из социальных сетей: `facebook`, `vk` или `instagram`  
например: `python smm_analyze.py facebook`   
          
Чтобы получить статистику за определенное время, укажите количество дней после параметра `-d`  
например: `python smm_analyze.py facebook -d 90`



### Переменные окружения

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` рядом с `manage.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступны следующие переменные:



* Для Фейсбука: 
    * `FB_RESEARCH_GROUP_ID` - id исследуемой группы
    * `FB_TOKEN` - ваш токен приложения

* Для Вконтакте: 
    * `VK_RESEARCH_DOMAIN` - доменное имя исследуемой группы
    * `VK_APP_ID` - ваш id приложения
    * `VK_APP_TOKEN` - ваш токен приложения
    
* Для Инстаграм: 
    * `IG_RESEARCH_USERNAME` - username исследуемой группы
    * `IG_USERNAME` - ваш username
    * `IG_PASSWORD` - ваш пароль

    


### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org].

[dvmn.org]: https://dvmn.org/modules/python-for-smm/lesson/customer-searching/