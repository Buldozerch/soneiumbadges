import random
import asyncio
import os
from weakref import proxy
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


from libs.eth_async.client import Client
from libs.eth_async.utils.utils import parse_proxy
from functions.soneuim_activity import SoneuimActivity
from tasks.owlto_bridge import OwltoBridge
from libs.eth_async.data.models import Networks
from utils.db_api_async.db_api import Session
from utils.db_api_async.db_activity import DB
from data import config
from data.models import Settings
settings = Settings()


private_file = config.PRIVATE_FILE
if os.path.exists(private_file):
    with open(private_file, 'r') as private_file:
        private = [line.strip() for line in private_file if line.strip()]

proxy_file = config.PROXY_FILE
if os.path.exists(proxy_file):
    with open(proxy_file, 'r') as proxy_file:
        proxys = [line.strip() for line in proxy_file if line.strip()]


async def add_wallets_db():
    logger.info(f'Start import wallets')
    for i in range(len(private)):
        private_key = private[i]
        proxy = proxys[i]
        proxy = parse_proxy(proxy)
        client = Client(private_key=private_key,
                        network=Networks.Ethereum)
        async with Session() as session:
            db = DB(session=session)
            await db.add_wallet(private_key=private_key, public_key=client.account.address, proxy=proxy)

    logger.success('Success import wallets')
    return

async def update_proxy(user):
    logger.info(f'{user} start updating proxy')
    async with Session() as session:
        db = DB(session=session)
        await db.update_proxy(user_id=user.id, available_proxies=proxys)
        logger.success(f'{user} success update proxy')


async def check_balance_in_network(client: Client):
    balance = await client.wallet.balance()
    if balance.Ether <= settings.eth_deposit.from_:
        return False
    else:
        return True

async def choose_network_for_bridge(client_arbitrum: Client,
                                    client_base: Client,
                                    client_optimism: Client):
    network_with_balance = []
    arbitrum_balance = await check_balance_in_network(client=client_arbitrum)
    if arbitrum_balance and settings.use_arbitrum_for_bridge: network_with_balance.append(client_arbitrum)
    base_balance = await check_balance_in_network(client=client_base)
    if base_balance and settings.use_base_for_bridge: network_with_balance.append(client_base)
    optimism_balance = await check_balance_in_network(client=client_optimism)
    if optimism_balance and settings.use_optimism_for_bridge: network_with_balance.append(client_optimism)
    return random.choice(network_with_balance)


@retry(
    stop=stop_after_attempt(5),  
    wait=wait_fixed(5),         
    retry=retry_if_exception_type(Exception),  
    after=lambda retry_state: logger.error(f"Wrong with Owlto Bridge: {retry_state.outcome.exception()} (try {retry_state.attempt_number})") 
)
async def handle_bridge(user):
    client_aribtrum = Client(private_key=user.private_key, 
                             network=Networks.Arbitrum,
                             proxy=user.proxy,
                             check_proxy=False)

    client_base = Client(private_key=user.private_key, 
                             network=Networks.Base,
                             proxy=user.proxy,
                             check_proxy=False)

    client_optimism = Client(private_key=user.private_key, 
                             network=Networks.Optimism,
                             proxy=user.proxy,
                             check_proxy=False)
    random_network_for_bridge = await choose_network_for_bridge(client_aribtrum, client_base, client_optimism)

    if random_network_for_bridge:
        owlto_bridge = OwltoBridge(client=random_network_for_bridge)
        bridge = await owlto_bridge.owlto_bridge(network=random_network_for_bridge.network.name)
        if bridge:
            return True

    else:
        logger.warning(f"{user} no one Network don't have enough balance")
        return False

async def check_balance(user, client):
    while True:
        balance = await client.wallet.balance()
        if balance.Ether >= settings.eth_deposit.from_ - 0.0005:
            logger.success(f'{user} Bridge to Soneuim success found')
            return True
        else:
            logger.warning(f'{user} still waiting deposit')
            await asyncio.sleep(20)
            continue


async def handle_start_random_actions(user):
    random_sleep_before_start = random.randint(settings.delay_between_start_account.from_, settings.delay_between_start_account.to_)
    logger.info(f'{user} sleep {random_sleep_before_start} seconds before start working')
    await asyncio.sleep(random_sleep_before_start)
    logger.info(f'Start working with {user}')
    while True:
        try:
            client = Client(private_key=user.private_key, network=Networks.Soneium, proxy=user.proxy, check_proxy=True)
            break
        except Exception:
            logger.error(f'{user} proxy dont work. Try change')
            try:
                await update_proxy(user=user)
            except Exception:
                return
            continue
    try:
        client = Client(private_key=user.private_key,
                        network=Networks.Soneium, proxy=user.proxy, check_proxy=False)

        if settings.owlto_bridger and user.owlto_bridge < settings.owlto_bridger_times.from_:
            for _ in range(random.randint(settings.owlto_bridger_times.from_, settings.owlto_bridger_times.to_)):
                bridge = await handle_bridge(user=user)
                if bridge:
                    async with Session() as session:
                        db = DB(session=session)
                        await db.add_owlto_bridge(id=user.id)
                    await asyncio.sleep(20)
                else:
                    return False
        soneuim_balance = await client.wallet.balance()
        if not soneuim_balance.Ether:
            bridge = await handle_bridge(user=user)
            if bridge:
                async with Session() as session:
                    db = DB(session=session)
                    await db.add_owlto_bridge(id=user.id)
                await check_balance(user=user, client=client)
            else:
                return False
    except Exception:
        logger.error(f'Bad bridge for {user}')
        return
    swap = SoneuimActivity(client=client, user=user)
    await swap.handle_account()
    logger.success(f'{user} end all actions')
    return

async def start_swap():
    async with Session() as session:
        db = DB(session=session)
        wallets = await db.get_all_wallets()
    tasks = [handle_start_random_actions(user=user) for user in wallets]
    task_gathering = asyncio.gather(*tasks)

    # Ждем завершения всех задач
    await task_gathering
