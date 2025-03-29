# Soneium Badges Farmer

Софт для фарма Badges на Soneium

## Главные особенности

Софт фармит бейджи с таких проектов:

- Owlto Swaps (3+ swaps)
- Owlto Multiple Swapper (0.005 ETH+ swaps)
- Owlto Bridge (1 bridge to Soneuim Network)
- Owlto Bridge Platinum (3 bridges to Soneium Network)
- Owlto Bridge Diamond (5 bridges to Soneium Network)
- Sonus (10 swaps, 5 locks)
- QuickSwap (10 swaps)
- Sonex (10 swaps)
- Untitled Bank (10 trans: Earn/Deposit/Borrow/Repay)

## Установка 

### Windows  
```
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
### Linux/MacOS
```
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install greenlet (FOR MACOS USERS)
python main.py
```
## Как использовать
### Первый запуск
Запустите в первый раз main.py для создания директории files/ и файлов в ней

### Настройка перед запуском
- Заполните приватные ключи в files/private.txt
- Заполните прокси в files/proxy.txt в формате:  http://log:pass@ip:port или log:pass@ip:port или ip:port:log:pass
- Заполните настройки в files/settings.json своими настройками
### Settings.json
Почти все настройки имеют рандомные значения, которые надо указывать от (from) до (to). Будет выбираться рандомное число в этом диапозоне при работе софта. Чтобы поставить не рандомное значение указывайте одинаковое значение в from и to ("from": 3, "to": 3) 
- eth_depost - Отвечает за минимальное и максимальное рандомное значение для депозита в сеть Soneuim
- use_arbitrum_for_bridge (и другие) - ставьте true или false. Настройка отвечает из каких сетей можно совершать депозит в сеть Soneuim
- delay_between_start_account - Задержка перед запуском аккаунта, выставляется для того, чтобы аккаунты не запускались одновременно
- delay_between_swaps - Задержка между транзакциями на одной площадке
- delay_between_actions - Задержка между площадками
- quick_swaps (и другие) - Количество свапов. По дефолту в from стоят минимальные значения критериев
- owlto_multiple_swapper - true/false отвечает за свап 0.005 в ETH + на owlto для получения бейджа
- owlto_bridger - true/false отвечает за несколько bridges через owlto
- owlto_bridger_times - работает если owlto_bridger = true. Сделает столько бриджей сколько указано в настройке
- sonus_amount_lock - Количество Sonus блокируемых одной транзакцией
- min_max_eth_swap - % от баланса эфира для свапа (при значениях from: 10 to: 30. Будет при транзакциях свапа свапать от 10 до 30% баланса в токен)
### Доступные опции
1. Import Wallets in DB
Создает Базу Данных. Используется для дальнейшей работы. Обязательно к запуску после заполнения файлов

2. Start Farm
Запускает фарм аккаунтов

### Работа софта
1. Запускает аккаунт и спит рандомное время
2. Проверяет баланс в сети Soneium, при 0 балансе совершает bridge через Owlto из доступных сетей
3. Проверяет количество совершенных транзакций на площадках
4. Выстраивает рандомный маршрут
5. Работает по маршруту выполняя транзакции



### Мои ссылки
TG канал https://t.me/buldozercode

### Support
#### Donate EVM:
0x7AE96311BEd9Fc1a32Eb99f1d62E9C2aA088bb38

#### Donate TRX:
TD6JnRN94C4sm313t7xDS9JKQkCypLhcJo

#### Donate SOL:
HgoYUmW6T6JFPCJjUvA21F5UmJ64dmWozVvcYGaxhENu

