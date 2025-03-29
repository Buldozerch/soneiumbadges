from .models import User
import random
from sqlalchemy import select, and_, desc, func, or_
from libs.eth_async.utils.utils import parse_proxy


class DB:
    def __init__(self, session):
        self.session = session


    async def add_wallet(self, private_key: str, public_key: str, proxy: str | None = None):
        wallet = User(
            private_key=private_key,
            public_key=public_key,
            proxy=proxy,
        )
        try:
            self.session.add(wallet)
        except Exception as e:
            print(e)
            return

    async def update_proxy(self, user_id: int, available_proxies: list):
        existing_proxies = await self.session.execute(select(User.proxy))
        existing_proxies = {proxy[0] for proxy in existing_proxies.all()}  # Преобразуем в множество

        # Фильтруем список, оставляя только уникальные прокси
        unique_proxies = list(set(available_proxies) - existing_proxies)
        if not unique_proxies:
            raise ValueError("Нет доступных уникальных прокси!")

        # Выбираем случайный уникальный прокси
        new_proxy = random.choice(unique_proxies)
        new_proxy = parse_proxy(new_proxy)

        # Обновляем прокси для пользователя
        user = await self.session.get(User, user_id)
        if user:
            user.proxy = new_proxy
            await self.session.commit()
            return new_proxy
        else:
            raise ValueError(f"Пользователь с id {user_id} не найден")

    async def get_all_wallets(self) -> list:
        result = await self.session.execute(select(User))  # выполняем запрос ко всем записям в таблице
        wallets = result.scalars().all()  # возвращаем все строки из таблицы как список
        return wallets

    async def add_quickswap(self, id):
        user = select(User).filter(User.id == id)
        user = (await self.session.scalars(user)).first()
        user.quickswap_swap += 1 

    async def add_sonex(self, id):
        user = select(User).filter(User.id == id)
        user = (await self.session.scalars(user)).first()
        user.sonex_swap += 1 

    async def add_owlto_swaps(self, id):
        user = select(User).filter(User.id == id)
        user = (await self.session.scalars(user)).first()
        user.owlto_swap += 1 

    async def add_owlto_bridge(self, id):
        user = select(User).filter(User.id == id)
        user = (await self.session.scalars(user)).first()
        user.owlto_bridge += 1 

    async def add_sonus_swaps(self, id):
        user = select(User).filter(User.id == id)
        user = (await self.session.scalars(user)).first()
        user.sonus_swap += 1 

    async def add_sonus_lock(self, id):
        user = select(User).filter(User.id == id)
        user = (await self.session.scalars(user)).first()
        user.sonus_lock += 1 

    async def add_untiled_bank(self, id, number):
        user = select(User).filter(User.id == id)
        user = (await self.session.scalars(user)).first()
        user.untintled_bank+= number 

