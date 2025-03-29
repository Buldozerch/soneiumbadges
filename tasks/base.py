import asyncio

import aiohttp

from libs.eth_async.client import Client
from libs.eth_async.data.models import TokenAmount
from web3.types import TxParams, Wei
from web3.constants import MAX_INT
from libs.eth_async.transactions import Tx
from libs.eth_async.utils.utils import randfloat
from utils.db_api_async.models import User



class Base:
    def __init__(self, client: Client, user: User | None = None):
        self.client = client
        self.user = user

    @staticmethod
    async def get_token_price(token_symbol='ETH', second_token: str = 'USDT') -> float | None:
        token_symbol, second_token = token_symbol.upper(), second_token.upper()

        if token_symbol.upper() in ('USDC', 'USDT', 'DAI', 'CEBUSD', 'BUSD'):
            return 1
        if token_symbol == 'WETH':
            token_symbol = 'ETH'

        for _ in range(5):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f'https://api.binance.com/api/v3/depth?limit=1&symbol={token_symbol}{second_token}') as r:
                        if r.status != 200:
                            return None
                        result_dict = await r.json()
                        if 'asks' not in result_dict:
                            return None
                        return float(result_dict['asks'][0][0])
            except Exception as e:
                await asyncio.sleep(5)
        raise ValueError(f'Can not get {token_symbol + second_token} price from Binance')

    async def approve_interface(self, token_address, spender, amount: TokenAmount | None = None, infinity: bool = False) -> bool:
        # Получаем баланс токена
        balance = await self.client.wallet.balance(token=token_address)
        
        # Если баланс 0, сразу возвращаем False
        if balance.Wei <= 0:
            return False

        # Если не указана сумма, или сумма больше чем баланс, устанавливаем на максимальную
        if not amount:
            amount = balance

        # Проверяем одобренную сумму для spender
        approved = await self.client.transactions.approved_amount(
            token=token_address,
            spender=spender,
            owner=self.client.account.address
        )

        # Если сумма уже одобрена, возвращаем True
        if amount.Wei <= approved.Wei:
            return True

        # Если сумма меньше, то делаем approve с "неограниченной" суммой (например, InfinityAmount)
        if infinity:
            amount = TokenAmount(amount=2*256-1)

        tx = await self.client.transactions.approve(
            token=token_address.address,
            spender=spender.address,
            amount=amount
        )

        # Ожидаем получения receipt
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)
        
        if receipt:
            return True

        return False
    async def send_transaction(self, to, data, value):

        tx_params = TxParams(
            to=to.address,
            data=data,
            value=value.Wei
        )

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

        if receipt['status'] == 1:
            return receipt['transactionHash'].hex()
        else:
            return None

    async def get_token_info(self, contract_address):
        contract = await self.client.contracts.default_token(contract_address=contract_address)
        print('name:', await contract.functions.name().call())
        print('symbol:', await contract.functions.symbol().call())
        print('decimals:', await contract.functions.decimals().call())

    @staticmethod
    def parse_params(params: str, has_function: bool = True):
        if has_function:
            function_signature = params[:10]
            print('function_signature', function_signature)
            params = params[10:]
        while params:
            print(params[:64])
            params = params[64:]
