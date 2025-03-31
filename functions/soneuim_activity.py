import random
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError
from loguru import logger

from libs.eth_async.data.models import TokenAmount
from utils.db_api_async.db_api import Session
from utils.db_api_async.db_activity import DB
from libs.eth_async.client import Client
from utils.db_api_async.models import User
from tasks.soneuim_projects import SoneuimProjects
from data.models import Contracts
from data.models import Settings

settings = Settings()
class SoneuimActivity(SoneuimProjects):
    def __init__(self, client: Client, user: User | None = None):
        super().__init__(client, user)
        self.usdc = Contracts.USDC
        self.eth = Contracts.ETH
        self.usdt = Contracts.USDT
        self.sonus = Contracts.SONUS
        self.tokens = [self.usdt, self.usdc]


    async def check_necessary_swap(self, project: str):
        if project == 'quickswap':
            swaps = self.user.quickswap_swap
            if swaps >= settings.quick_swaps.from_:
                return None
            random_swaps = int(random.randint(settings.quick_swaps.from_, settings.quick_swaps.to_))
            needed_swaps = random_swaps - swaps 
            if needed_swaps >= 1:
                return needed_swaps
            else:
                return None

        elif project == 'owlto':
            swaps = self.user.owlto_swap
            if swaps >= settings.owlto_swaps.from_:
                return None
            random_swaps = int(random.randint(settings.owlto_swaps.from_, settings.owlto_swaps.to_))
            needed_swaps = random_swaps - swaps 
            if needed_swaps >= 1:
                return needed_swaps
            else:
                return None

        elif project == 'sonus':
            swaps = self.user.sonus_swap
            if swaps >= settings.sonus_swaps.from_:
                return None
            random_swaps = int(random.randint(settings.sonus_swaps.from_, settings.sonus_swaps.to_))
            needed_swaps = random_swaps - swaps 
            if needed_swaps >= 1:
                return needed_swaps
            else:
                return None

        elif project == 'sonus_lock':
            swaps = self.user.sonus_lock
            if swaps >= settings.sonus_lock.from_:
                return None
            random_swaps = int(random.randint(settings.sonus_lock.from_, settings.sonus_lock.to_))
            needed_swaps = random_swaps - swaps 
            if needed_swaps >= 1:
                return needed_swaps
            else:
                return None

        elif project == 'sonex':
            swaps = self.user.sonex_swap
            if swaps >= settings.sonex_swaps.from_:
                return None
            random_swaps = int(random.randint(settings.sonex_swaps.from_, settings.sonex_swaps.to_))
            needed_swaps = random_swaps - swaps 
            if needed_swaps >= 1:
                return needed_swaps
            else:
                return None

        elif project == 'untiled_bank':
            swaps = self.user.untintled_bank
            if swaps >= settings.untiled_bank.from_:
                return None
            random_swaps = int(random.randint(settings.untiled_bank.from_, settings.untiled_bank.to_))
            needed_swaps = random_swaps - swaps 
            if needed_swaps >= 1:
                return needed_swaps
            else:
                return None

        
    async def random_path(self):
        projects = ['quickswap', 'owlto', 'sonus','sonus_lock', 'sonex', 'untiled_bank']
        random.shuffle(projects)
        path = {}
        for i in projects:
            needed_swaps = await self.check_necessary_swap(project=i)
            if needed_swaps:
                path[i] = needed_swaps
            else:
                path[i] = 0
        return path

    async def random_eth_swap(self, eth_balance: float):
        random_percent = random.randint(settings.min_max_eth_swap.from_, settings.min_max_eth_swap.to_)
        percent_as_fraction = random_percent / 100
        amount_swap = eth_balance * percent_as_fraction
        return amount_swap

    async def get_tokens_balances(self,):
        eth_amount = await self.client.wallet.balance()
        if eth_amount.Ether < 0.00005:
            await self.unwrap_weth()
        usdc_amount = await self.client.wallet.balance(token=self.usdc, decimals=6)
        usdt_amount = await self.client.wallet.balance(token=self.usdt, decimals=6)
        eth_amount = float(str(eth_amount.Ether))
        usdc_amount = float(str(usdc_amount.Ether))
        usdt_amount = float(str(usdt_amount.Ether))
        return eth_amount, usdc_amount, usdt_amount 

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with QuickSwap Swap: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def quickswap_random_swap(self):
        eth_amount, usdc_amount, usdt_amount = await self.get_tokens_balances()

        random_token = random.choice(self.tokens)

        if usdc_amount >= 0.05 and usdt_amount >= 0.05:
            if random_token.title == "USDC":
                swap = await self.quickswap_swap_token(output_token=random_token, input_token=self.eth, swap_amount=usdc_amount)
            else:
                swap = await self.quickswap_swap_token(output_token=random_token, input_token=self.eth, swap_amount=usdt_amount)
        if usdc_amount >= 0.05:
            swap = await self.quickswap_swap_token(output_token=self.usdc, input_token=self.eth, swap_amount=usdc_amount)
        elif usdt_amount >= 0.05:
            swap = await self.quickswap_swap_token(output_token=self.usdt, input_token=self.eth, swap_amount=usdt_amount)
        else:
            swap = await self.quickswap_swap_token(output_token=self.eth, input_token=random_token, swap_amount=await self.random_eth_swap(eth_balance=eth_amount))

        if swap:
            return True
        else:
            logger.error(f'{self.user} Error preparing transaction on QuickSwap')
            raise Exception 

    async def handle_quickswap(self, count_swaps):
        for _ in range(count_swaps):
            random_swap = await self.quickswap_random_swap()
            if random_swap:
                async with Session() as session:
                    db = DB(session=session)
                    await db.add_quickswap(id=self.user.id)
            random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
            logger.info(f'{self.user} sleep {random_sleep} before next swap')
            await asyncio.sleep(random_sleep)

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Sonex Swap: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def sonex_random_swaps(self):
        eth_amount, usdc_amount, usdt_amount = await self.get_tokens_balances()

        random_token = random.choice(self.tokens)

        if usdc_amount >= 0.05 and usdt_amount >= 0.05:
            if random_token.title == "USDC":
                swap = await self.sonex_swap(output_token=random_token, input_token=self.eth, swap_amount=usdc_amount)
            else:
                swap = await self.sonex_swap(output_token=random_token, input_token=self.eth, swap_amount=usdt_amount)
        if usdc_amount >= 0.05:
            swap = await self.sonex_swap(output_token=self.usdc, input_token=self.eth, swap_amount=usdc_amount)
        elif usdt_amount >= 0.05:
            swap = await self.sonex_swap(output_token=self.usdt, input_token=self.eth, swap_amount=usdt_amount)
        else:
            swap = await self.sonex_swap(output_token=self.eth, input_token=random_token, swap_amount=await self.random_eth_swap(eth_balance=eth_amount))

        if swap:
            return True
        else:
            logger.error(f'{self.user} Error preparing transaction on Sonex')
            raise Exception

    async def handle_sonex(self, count_swaps):
        for _ in range(count_swaps):
            random_swap = await self.sonex_random_swaps()
            if random_swap:
                async with Session() as session:
                    db = DB(session=session)
                    await db.add_sonex(id=self.user.id)
            random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
            logger.info(f'{self.user} sleep {random_sleep} before next swap')
            await asyncio.sleep(random_sleep)

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Owlto Swap: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def owlto_random_swaps(self):
        eth_amount, usdc_amount, usdt_amount = await self.get_tokens_balances()

        random_token = random.choice(self.tokens)
        if settings.owlto_multiple_swapper and eth_amount > 0.005:
            await self.owlto_swap_token(output_token=self.eth, input_token=random_token, swap_amount=round(random.uniform(0.005, 0.0055),4))

        if usdc_amount >= 0.05 and usdt_amount >= 0.05:
            if random_token.title == "USDC":
                swap = await self.owlto_swap_token(output_token=random_token, input_token=self.eth, swap_amount=usdc_amount)
            else:
                swap = await self.owlto_swap_token(output_token=random_token, input_token=self.eth, swap_amount=usdt_amount)
        if usdc_amount >= 0.05:
            swap = await self.owlto_swap_token(output_token=self.usdc, input_token=self.eth, swap_amount=usdc_amount)
        elif usdt_amount >= 0.05:
            swap = await self.owlto_swap_token(output_token=self.usdt, input_token=self.eth, swap_amount=usdt_amount)
        else:
            swap = await self.owlto_swap_token(output_token=self.eth, input_token=random_token, swap_amount=await self.random_eth_swap(eth_balance=eth_amount))

        if swap:
            return True
        else:
            logger.error(f'{self.user} Error preparing transaction on Owlto')
            raise Exception

    async def handle_owlto(self, count_swaps):
        for _ in range(count_swaps):
            random_swap = await self.owlto_random_swaps()
            if random_swap:
                async with Session() as session:
                    db = DB(session=session)
                    await db.add_owlto_swaps(id=self.user.id)
            random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
            logger.info(f'{self.user} sleep {random_sleep} before next swap')
            await asyncio.sleep(random_sleep)

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Sonus Swap: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def sonus_random_swaps(self):
        eth_amount, usdc_amount, usdt_amount = await self.get_tokens_balances()

        random_token = random.choice(self.tokens)

        if usdc_amount >= 0.05 and usdt_amount >= 0.05:
            if random_token.title == "USDC":
                swap = await self.sonus_swap_token_to_eth(output_token=random_token, swap_amount=usdc_amount)
            else:
                swap = await self.sonus_swap_token_to_eth(output_token=random_token, swap_amount=usdt_amount)
        if usdc_amount >= 0.05:
            swap = await self.sonus_swap_token_to_eth(output_token=self.usdc, swap_amount=usdc_amount)
        elif usdt_amount >= 0.05:
            swap = await self.sonus_swap_token_to_eth(output_token=self.usdt, swap_amount=usdt_amount)
        else:
            swap = await self.sonus_swap_eth_to_token(input_token=random_token, swap_amount=await self.random_eth_swap(eth_balance=eth_amount))

        if swap:
            return True
        else:
            logger.error(f'{self.user} Error preparing transaction on Sonus Swap')
            raise Exception

    async def handle_sonus_swaps(self, count_swaps):
        for _ in range(count_swaps):
            random_swap = await self.sonus_random_swaps()
            if random_swap:
                async with Session() as session:
                    db = DB(session=session)
                    await db.add_sonus_swaps(id=self.user.id)
            random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
            logger.info(f'{self.user} sleep {random_sleep} before next swap')
            await asyncio.sleep(random_sleep)

    async def _random_sonus_lock(self):
        return random.randint(settings.sonus_amount_lock.from_, settings.sonus_amount_lock.to_)

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Sonus Lock: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def sonus_random_lock(self, sonus_amount_lock):
        sonus_amount = await self.client.wallet.balance(token=self.sonus)
        sonus_amount = float(str(sonus_amount.Ether))
        if sonus_amount_lock > sonus_amount:
            swap = await self.sonus_swap_eth_to_token(swap_amount=sonus_amount_lock - sonus_amount + 5, input_token=self.sonus)
            if swap:
                lock = await self.sonus_lock(amount_lock=sonus_amount_lock)
                if lock:
                    return True
                else:
                    logger.error(f'{self.user} Error preparing transaction on Sonus Lock')
                    raise Exception
            else:
                logger.error(f'{self.user} Error preparing transaction on Sonus Swap')
                raise Exception
        else:
            lock = await self.sonus_lock(amount_lock=sonus_amount_lock)
            if lock:
                return True
            else:
                logger.error(f'{self.user} Error preparing transaction on Sonus Lock')
                raise Exception

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Sonus Swap: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def swap_to_sonus(self, amount_swap):
        swap = await self.sonus_swap_eth_to_token(token_swap_amount=amount_swap, input_token=self.sonus, swap_amount=0.0, slippage=0.5)
        if swap == "Not enough balance":
            return False
        elif swap:
            return True
        else:
            logger.error(f'{self.user} Error preparint trainsaction on Swap to Sonus')
            raise Exception


    async def handle_swap_to_sonus(self,count_swaps):
        random_locks = []
        for _ in range(count_swaps):
            amount = await self._random_sonus_lock()
            random_locks.append(amount)
        amount_swap = 0
        for i in random_locks:
            amount_swap += i 

        swap = await self.swap_to_sonus(amount_swap=amount_swap)
        if swap:
            async with Session() as session:
                db = DB(session=session)
                await db.add_sonus_swaps(id=self.user.id)
            random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
            logger.info(f'{self.user} sleep {random_sleep} before next swap')
            await asyncio.sleep(random_sleep)
            return random_locks
        else:
            return False

    async def handle_sonus_lock(self, count_swaps):
        swap_to_sonus = await self.handle_swap_to_sonus(count_swaps=count_swaps)
        if not swap_to_sonus:
            logger.error(f"{self.user} can't sonus lock. Not Enough Balance")
            return
        for _ in range(count_swaps):
            random_lock = await self.sonus_random_lock(sonus_amount_lock=swap_to_sonus[_])
            if random_lock:
                async with Session() as session:
                    db = DB(session=session)
                    await db.add_sonus_lock(id=self.user.id)
            random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
            logger.info(f'{self.user} sleep {random_sleep} before next lock')
            await asyncio.sleep(random_sleep)


    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Untiled Swap Zero: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def _untiled_bank_swap_zero(self):
        eth_amount, usdc_amount, usdt_amount = await self.get_tokens_balances()
        weth_amount = await self.client.wallet.balance(token=Contracts.WETH)
        weth_amount = float(str(weth_amount.Ether))
        if usdc_amount == 0.0 and weth_amount == 0.0:
            swap = await self.sonus_swap_eth_to_token(input_token=self.usdc, swap_amount=await self.random_eth_swap(eth_balance=eth_amount))
        else:
            return usdc_amount, weth_amount
        if swap:
            async with Session() as session:
                db = DB(session=session)
                await db.add_sonus_swaps(id=self.user.id)
            random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
            logger.info(f'{self.user} sleep {random_sleep} before next swap')
            await asyncio.sleep(random_sleep)
            return usdc_amount, weth_amount
        else:
            logger.error(f'{self.user} Error preparing transaction on Sonus Swap')
            raise Exception

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Untiled Earn: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def untiled_bank_earn_random(self):
        usdc_amount, weth_amount = await self._untiled_bank_swap_zero()
        random_pick = ['USDC', 'WETH']
        random_token = random.choice(random_pick)
        if usdc_amount > 0.1:
            usdc_amount = round(random.uniform(0.01, 0.1), 2)
        if weth_amount > 0.0001:
            weth_amount = round(random.uniform(0.00001,0.00005), 5)
        if usdc_amount >= 0.01 and weth_amount >= 0.00001:
            if random_token == "USDC":
                swap = await self.untiled_bank_earn(output_token=self.usdc, amount_earn=usdc_amount)
            else:
                swap = await self.untiled_bank_earn(output_token=self.eth, amount_earn=weth_amount)
        elif usdc_amount >= 0.01:
            swap = await self.untiled_bank_earn(output_token=self.usdc, amount_earn=usdc_amount)
        else:
            swap = await self.untiled_bank_earn(output_token=self.eth, amount_earn=weth_amount)

        if swap:
            return True
        else:
            logger.error(f'{self.user} Error preparing transaction on Untiled Earn')
            raise Exception

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Untiled Deposit: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def untiled_bank_deposit_random(self):
        usdc_amount, weth_amount = await self._untiled_bank_swap_zero()
        if usdc_amount > 0.1:
            usdc_amount = round(random.uniform(0.01, 0.1), 2)
        deposit = await self.untiled_bank_deposit(amount_deposit=usdc_amount)
        if deposit:
            return usdc_amount
        else:
            logger.error(f'{self.user} Error preparing transcation on Untiled Deposit')
            raise Exception

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Untiled Borrow: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def untiled_bank_borrow_random(self, amount_borrow):
        borrow = await self.untiled_bank_borrow(amount_borrow=amount_borrow)
        if borrow:
            return True
        else:
            logger.error(f'{self.user} Error preparing transcation on Untiled Deposit')
            raise Exception

    @retry(
        stop=stop_after_attempt(5),  
        wait=wait_fixed(5),         
        retry=retry_if_exception_type(Exception),  
        after=lambda retry_state: logger.error(f"Wrong with Untiled Repay: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
    )
    async def untiled_bank_repay_random(self, amount_repay):
        repay = await self.untiled_bank_repay(amount_repay=amount_repay)
        if repay:
            return True
        else:
            logger.error(f'{self.user} Error preparing transcation on Untiled Deposit')
            raise Exception

    async def handle_untiled_bank_deposit(self):
        usdc_deposit = await self.untiled_bank_deposit_random()
        slippage = random.randint(70, 90)
        if usdc_deposit:
            random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
            logger.info(f'{self.user} sleep {random_sleep} before next transaction')
            await asyncio.sleep(random_sleep)
            amount_borrow = await self.amount_out_min(output_token=self.usdc, input_token=self.eth, amount=TokenAmount(usdc_deposit, decimals=6), slippage=slippage)
            amount_borrow = float(str(amount_borrow.Ether))
            borrow = await self.untiled_bank_borrow_random(amount_borrow=amount_borrow)
            if borrow:
                random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
                logger.info(f'{self.user} sleep {random_sleep} before next transaction')
                await asyncio.sleep(random_sleep)
                repay = await self.untiled_bank_repay_random(amount_repay=amount_borrow / 2)
                if repay:
                    return True


    async def handle_untiled_bank(self, count_swaps):
        i = 0
        while i < count_swaps:
            random_action = ['Earn', 'Deposit']
            random_action = random.choice(random_action)
            if random_action == 'Earn':
                random_earn = await self.untiled_bank_earn_random()
                if random_earn:
                    i += 1
                    async with Session() as session:
                        db = DB(session=session)
                        await db.add_untiled_bank(id=self.user.id, number=1)
                random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
                logger.info(f'{self.user} sleep {random_sleep} before next transaction')
                await asyncio.sleep(random_sleep)
            else:
                random_deposit = await self.handle_untiled_bank_deposit()
                if random_deposit:
                    i += 3
                    async with Session() as session:
                        db = DB(session=session)
                        await db.add_untiled_bank(id=self.user.id, number=3)
                random_sleep = random.randint(settings.delay_between_swaps.from_, settings.delay_between_swaps.to_)
                logger.info(f'{self.user} sleep {random_sleep} before next transaction')
                await asyncio.sleep(random_sleep)

    async def handle_account(self):
        for _ in range(2):
            path = await self.random_path()
            logger.info(f'{self.user} path for account: {path}')
            for key, value in path.items():
                try:
                    if key == 'owlto' and value > 0:
                        await self.handle_owlto(count_swaps=value)
                        random_sleep = random.randint(settings.delay_between_actions.from_, settings.delay_between_actions.to_)
                        logger.info(f'{self.user} sleep {random_sleep} before next action')
                        await asyncio.sleep(random_sleep)
                    elif key == 'sonus' and value > 0:
                        await self.handle_sonus_swaps(count_swaps=value)
                        random_sleep = random.randint(settings.delay_between_actions.from_, settings.delay_between_actions.to_)
                        logger.info(f'{self.user} sleep {random_sleep} before next action')
                        await asyncio.sleep(random_sleep)
                    elif key == 'quickswap' and value > 0:
                        await self.handle_quickswap(count_swaps=value)
                        random_sleep = random.randint(settings.delay_between_actions.from_, settings.delay_between_actions.to_)
                        logger.info(f'{self.user} sleep {random_sleep} before next action')
                        await asyncio.sleep(random_sleep)
                    elif key == 'sonus_lock' and value > 0:
                        await self.handle_sonus_lock(count_swaps=value)
                        random_sleep = random.randint(settings.delay_between_actions.from_, settings.delay_between_actions.to_)
                        logger.info(f'{self.user} sleep {random_sleep} before next action')
                        await asyncio.sleep(random_sleep)
                    elif key == 'untiled_bank' and value > 0:
                        await self.handle_untiled_bank(count_swaps=value)
                        random_sleep = random.randint(settings.delay_between_actions.from_, settings.delay_between_actions.to_)
                        logger.info(f'{self.user} sleep {random_sleep} before next action')
                        await asyncio.sleep(random_sleep)
                    elif key == 'sonex' and value > 0:
                        await self.handle_sonex(count_swaps=value)
                        random_sleep = random.randint(settings.delay_between_actions.from_, settings.delay_between_actions.to_)
                        logger.info(f'{self.user} sleep {random_sleep} before next action')
                        await asyncio.sleep(random_sleep)

                except asyncio.CancelledError:
                    logger.warning(f'{self.user} task was cancelled')
                    raise  # Не игнорируем отмену задачи

                except RetryError as e:
                    logger.error(f"{self.user} retry error in {key}, last attempt failed")

                    if e.last_attempt and e.last_attempt.exception():
                        original_exception = e.last_attempt.exception()
                        logger.error(f"Original exception: {original_exception}")

                        error_message = str(original_exception)

                        if "gas required exceeds allowance" in error_message:
                            logger.warning(f'{self.user} balance too low for work')
                            return False
                        continue

                except Exception as e:
                    logger.error(f'{self.user} error in {key} please restart later for this action')
                    error_message = str(e)
                    if "gas required exceeds allowance" in error_message:
                        logger.warning(f'{self.user} balance too low for work')
                        return False
                    continue
            # Оборачиваем unwrap_weth() в try
            try:
                await self.unwrap_weth()
            except Exception as e:
                logger.error(f"{self.user} error in unwrap_weth: {e}")
                # logger.error(f"Exception details:\n{traceback.format_exc()}")
