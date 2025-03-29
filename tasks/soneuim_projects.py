import time
import random
from loguru import logger
import aiohttp
from .base import Base
from data.models import Contracts
from libs.eth_async.client import Client
from fake_useragent import UserAgent
from web3.constants import HexStr
from libs.eth_async.data.models import RawContract 
from libs.eth_async.data.models import TxArgs, TokenAmount



class SoneuimProjects(Base):
    async def get_token_prices(self, output_token, input_token):
        from_token_price_dollar = await self.get_token_price(token_symbol=output_token.title)
        to_token_price_dollar = await self.get_token_price(token_symbol=input_token.title)
        if not from_token_price_dollar or not to_token_price_dollar:
            raise ValueError (f'Cannot get token price for swap')
        return from_token_price_dollar, to_token_price_dollar

    async def output_token_is_eth(self, output_token):
        if output_token == 'ETH':
            return True
        else:
            return False

    async def amount_out_min(self, output_token, input_token, amount, slippage):
        from_token_price_dollar, to_token_price_dollar = await self.get_token_prices(output_token=output_token, input_token=input_token)
        if input_token.title == 'USDC' or input_token.title == 'USDT':
            decimals = 6
        else:
            decimals = 18
        amount_out_min = TokenAmount(
            amount=float(amount.Ether) * from_token_price_dollar / to_token_price_dollar * (100 - slippage) / 100,
            decimals=decimals
        )
        return amount_out_min

    async def quickswap_swap_token(self, swap_amount: float, output_token: RawContract, input_token: RawContract, slippage: float = 10.0):
        contract = await self.client.contracts.get(contract_address=Contracts.QUICK_SWAP)
        function = 'exactInputSingle'

        amount = TokenAmount(swap_amount, decimals=6) if output_token.title == 'USDC' or output_token.title == 'USDT' else TokenAmount(swap_amount)
        value = amount if await self.output_token_is_eth(output_token=output_token.title) else TokenAmount(0)
        amount_out_min = await self.amount_out_min(output_token=output_token, input_token=input_token, 
                                                   amount=amount, slippage=slippage)

        if output_token.title != 'ETH':
            await self.approve_interface(token_address=output_token, spender=contract, infinity=True)
        params = TxArgs(
            tokenIn=output_token.address,
            tokenOut=input_token.address,
            deployer='0x0000000000000000000000000000000000000000',
            recipient=self.client.account.address,
            deadline=int(time.time() + 1200),
            amountIn=amount.Wei,
            amountOutMinimum=amount_out_min.Wei,
            limitSqrtPrice=0,
                )

        data = contract.encodeABI(function, args=(params.tuple(),))

        hash = await self.send_transaction(to=contract, data=data, value=value)
        if hash:
            logger.success(f'{self.user} success swap on QuickSwap {output_token.title}({amount.Ether}) to {input_token.title} hash: {hash}')
            return True
        else:
            logger.error(f"{self.user} can't swap on QuickSwap {output_token.title}({amount.Ether}) to {input_token.title}")
            return False 

    async def sonus_swap_eth_to_token(self, swap_amount: float, input_token: RawContract, token_swap_amount: float = 0.0,  slippage: float = 0.5):
        contract = await self.client.contracts.get(contract_address=Contracts.SONUS_SWAP)
        function = 'swapExactETHForTokens'

        if token_swap_amount:
            amount = TokenAmount(token_swap_amount, decimals=6) if input_token.title == 'USDC' or input_token.title == 'USDT' else TokenAmount(token_swap_amount)
            path = [input_token.address, Contracts.ETH.address]
            decimals = 6 if input_token.title == 'USDC' or input_token.title == 'USDT' else 18 
            amount_out_min = await contract.functions.getAmountsOut(amountIn=amount.Wei, path=path).call()
            amount_out_min = TokenAmount(amount_out_min[1], decimals=decimals)
            amount_out_min = amount_out_min.Wei // 10 ** decimals 
            amount_out_min = int(amount_out_min)
            amount = TokenAmount(amount_out_min, wei=True)
            value = amount
            balance = await self.client.wallet.balance()
            if balance.Wei < value.Wei:
                return "Not enough balance"

        else:
            amount = TokenAmount(swap_amount)
            value = amount


        path = [Contracts.ETH.address, input_token.address]
        decimals = 6 if input_token.title == 'USDC' or input_token.title == 'USDT' else 18 
        amount_out_min = await contract.functions.getAmountsOut(amountIn=amount.Wei, path=path).call()
        amount_out_min = TokenAmount(amount_out_min[1], decimals=decimals)
        amount_out_min = amount_out_min.Wei // 10 ** decimals
        amount_out_min = int(amount_out_min * 0.985)
        params = TxArgs(
                amountOutMin = amount_out_min,
                path = path,
                to=self.client.account.address,
                deadline = int(time.time()) * 2 + 20 * 60
                )

        data = contract.encodeABI(function, args=params.tuple())

        hash = await self.send_transaction(to=contract, data=data, value=value)
        if hash:
            logger.success(f'{self.user} success swap on Sonus ETH({amount.Ether}) to {input_token.title} hash: {hash}')
            return True
        else:
            logger.error(f"{self.user} can't swap on Sonus ETH({amount.Ether}) to {input_token.title}")
            return False

    async def sonus_swap_token_to_eth(self, swap_amount: float, output_token: RawContract,  slippage: float = 5.0):
        contract = await self.client.contracts.get(contract_address=Contracts.SONUS_SWAP)
        function = 'swapExactTokensForETH'

        amount = TokenAmount(swap_amount, decimals=6) if output_token.title == 'USDC' or output_token.title == 'USDT' else TokenAmount(swap_amount)
        path = [output_token.address, Contracts.ETH.address]
        decimals = 6 if output_token.title == 'USDC' or output_token.title == 'USDT' else 18 
        amount_out_min = await contract.functions.getAmountsOut(amountIn=amount.Wei, path=path).call()
        amount_out_min = TokenAmount(amount_out_min[1], decimals=decimals)
        amount_out_min = amount_out_min.Wei // 10 ** decimals 
        amount_out_min = int(amount_out_min * 0.985)
        await self.approve_interface(token_address=output_token, spender=contract, infinity=True)

        params = TxArgs(
                amountIn = amount.Wei,
                amountOutMin = amount_out_min,
                path = path,
                to=self.client.account.address,
                deadline = int(time.time()) * 2 + 20 * 60
                )

        data = contract.encodeABI(function, args=params.tuple())
        hash = await self.send_transaction(to=contract, data=data, value = TokenAmount(0))
        if hash:
            logger.success(f'{self.user} success swap on Sonus {output_token.title}({amount.Ether}) to ETH hash: {hash}')
            return True
        else:
            logger.error(f"{self.user} can't swap on Sonus {output_token.title}({amount.Ether}) to ETH")
            return False

    async def sonus_lock(self, amount_lock: float):
        contract = await self.client.contracts.get(contract_address=Contracts.SONUS_LOCK)
        function = 'createLock'

        amount = TokenAmount(amount_lock)
        await self.approve_interface(token_address=Contracts.SONUS, spender=contract, infinity=True)

        params = TxArgs(
                _value = amount.Wei,
                _lockDuration = 604800,
                )

        data = contract.encodeABI(function, args=params.tuple())
        hash = await self.send_transaction(to=contract, data=data, value = TokenAmount(0))
        if hash:
            logger.success(f'{self.user} success lock SONUS {amount.Ether} hash: {hash}')
            return True
        else:
            logger.error(f"{self.user} can't lock SONUS {amount.Ether}") 
            return False

    async def untiled_bank_deposit(self, amount_deposit: float):
        contract = await self.client.contracts.get(contract_address=Contracts.UNTILED_BANK)
        function = 'supplyCollateral'
        amount = TokenAmount(amount_deposit, decimals=6)
        amount_for_approve = TokenAmount(amount.Wei * 10, decimals=6)
        await self.approve_interface(token_address=Contracts.USDC, spender=contract, amount=amount_for_approve)

        params = TxArgs(
                id=5,
                assets=amount.Wei,
                data='0x'
                )
        data = contract.encodeABI(function, args=params.tuple())
        hash = await self.send_transaction(to=contract, data=data, value = TokenAmount(0))
        if hash:
            logger.success(f'{self.user} success deposit USDC {amount.Ether} in Untiled Bank hash: {hash} ')
            return True
        else:
            logger.error(f"{self.user} can't deposit USDC in Untiled Bank")
            return False


    async def untiled_bank_borrow(self, amount_borrow: float):
        contract = await self.client.contracts.get(contract_address=Contracts.UNTILED_BANK)
        function = 'borrow'
        amount = TokenAmount(amount_borrow, decimals=18)

        params = TxArgs(
                id=5,
                assets=amount.Wei,
                receiver=self.client.account.address
                )
        data = contract.encodeABI(function, args=params.tuple())
        hash = await self.send_transaction(to=contract, data=data, value = TokenAmount(0))
        if hash:
            logger.success(f'{self.user} success Borrow WETH {amount.Ether} in Untiled Bank hash: {hash} ')
            return True
        else:
            logger.error(f"{self.user} can't borrow WETH in Untiled Bank")
            return False


    async def untiled_bank_repay(self, amount_repay: float):
        contract = await self.client.contracts.get(contract_address=Contracts.UNTILED_BANK)
        function = 'repay'
        amount = TokenAmount(amount_repay, decimals=18)
        amount_for_approve = TokenAmount(amount.Wei * 10, decimals=18)
        await self.approve_interface(token_address=Contracts.WETH, spender=contract, amount=amount_for_approve)

        params = TxArgs(
                id=5,
                assets=amount.Wei,
                data='0x'
                )
        data = contract.encodeABI(function, args=params.tuple())
        hash = await self.send_transaction(to=contract, data=data, value = TokenAmount(0))
        if hash:
            logger.success(f'{self.user} success repay WETH {amount.Ether} in Untiled Bank hash: {hash} ')
            return True
        else:
            logger.error(f"{self.user} can't repay WETH in Untiled Bank")
            return False


    async def untiled_bank_earn(self, output_token: RawContract, amount_earn: float):
        if output_token.title == "USDC":
            contract = await self.client.contracts.get(contract_address=Contracts.UNTILED_EARN_USDC)
            amount = TokenAmount(amount_earn, decimals=6)
            amount_for_approve = TokenAmount(amount.Wei * 10, decimals=6)
        else:
            contract = await self.client.contracts.get(contract_address=Contracts.UNTILED_EARN_WETH)
            amount = TokenAmount(amount_earn, decimals=18)
            amount_for_approve = TokenAmount(amount.Wei * 10, decimals=18)
        function = 'deposit'
        await self.approve_interface(token_address=output_token, spender=contract, amount=amount_for_approve)

        params = TxArgs(
                assets=amount.Wei,
                receiver=self.client.account.address
                )
        data = contract.encodeABI(function, args=params.tuple())
        hash = await self.send_transaction(to=contract, data=data, value = TokenAmount(0))
        if hash:
            logger.success(f'{self.user} success earn {output_token.title}({amount.Ether}) in Untiled Bank hash: {hash} ')
            return True
        else:
            logger.error(f"{self.user} can't earn {output_token.title} in Untiled Bank")
            return False


    async def sonex_swap(self, swap_amount: float, output_token: RawContract, input_token: RawContract,  slippage: float = 0.5):
        contract = await self.client.contracts.get(contract_address=Contracts.SONEX)
        function = 'exactInput'
        slippage = round(random.uniform(0.5, 5.0), 1)

        amount = TokenAmount(swap_amount, decimals=6) if output_token.title == 'USDC' or output_token.title == 'USDT' else TokenAmount(swap_amount)
        value = amount if await self.output_token_is_eth(output_token=output_token.title) else TokenAmount(0)

        if output_token.title != 'ETH':
            await self.approve_interface(token_address=output_token, spender=contract, infinity=True)

        if input_token.title == "USDC":
            path = [self.client.w3.to_bytes(hexstr=HexStr(output_token.address + "0001f4")),
                    self.client.w3.to_bytes(hexstr=HexStr(Contracts.USDT.address + "0001f4")),
                    self.client.w3.to_bytes(hexstr=HexStr(input_token.address + "0001f4"))]
        elif input_token.title == "USDT":
            path = [self.client.w3.to_bytes(hexstr=HexStr(output_token.address + "0001f4")),
                    self.client.w3.to_bytes(hexstr=HexStr(Contracts.USDC.address + "0001f4")),
                    self.client.w3.to_bytes(hexstr=HexStr(input_token.address + "0001f4"))]


        elif input_token.title == "ETH" and output_token.title == "USDC":
            path = [
                    self.client.w3.to_bytes(hexstr=HexStr(output_token.address + "000bb8")),
                    self.client.w3.to_bytes(hexstr=HexStr(Contracts.USDT.address + "000bb8")),
                    self.client.w3.to_bytes(hexstr=HexStr(input_token.address + "000bb8"))
                    ]

        else:
            path = [
                    self.client.w3.to_bytes(hexstr=HexStr(output_token.address + "000bb8")),
                    self.client.w3.to_bytes(hexstr=HexStr(Contracts.USDC.address + "000bb8")),
                    self.client.w3.to_bytes(hexstr=HexStr(input_token.address + "000bb8"))
                    ]

        amount_out_min = await self.amount_out_min(output_token=output_token, input_token=input_token, 
                                                   amount=amount, slippage=slippage)
        encoded_path = b''.join(path)

        if output_token.title == 'ETH':

            swap_amount_args = (
                    encoded_path,
                    self.client.account.address,
                    int(time.time()) + 20 * 60,
                    amount.Wei,
                    amount_out_min.Wei,
                )


            swap_amount_data = contract.encodeABI(function, args=[swap_amount_args])

            return_eth_data = contract.encodeABI('refundETH', args=[])

            swap_data = contract.encodeABI(
                'multicall',
                args=[
                    [swap_amount_data, return_eth_data]
                ]
            )
        else:
            swap_amount_args = (
                    encoded_path,
                    '0x0000000000000000000000000000000000000000', 
                    int(time.time()) + 20 * 60,
                    amount.Wei,
                    amount_out_min.Wei,
                )


            swap_amount_data = contract.encodeABI(function, args=[swap_amount_args])
            wrap_data = TxArgs(
                    amount=1,
                    receiver=self.client.account.address,
                )
            return_eth_data = contract.encodeABI('unwrapWETH9', args=wrap_data.tuple())

            swap_data = contract.encodeABI(
                'multicall',
                args=[
                    [swap_amount_data, return_eth_data]
                ]
            )

        hash = await self.send_transaction(to=contract, data=swap_data, value=value)
        if hash:
            logger.success(f'{self.user} success swap on Sonex {output_token.title}({amount.Ether}) to {input_token.title} hash: {hash}')
            return True
        else:
            logger.error(f"{self.user} can't swap on Sonex {output_token.title}({amount.Ether}) to {input_token.title}")
            return False

    async def owlto_deploy_contract(self):
        #не использовать!
        value = TokenAmount(0.0002)
        random_contract = Client()
        data = '0x60806040527389a512a24e9d63e98e41f681bf77f27a7ef89eb76000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163460405161009f90610185565b60006040518083038185875af1925050503d80600081146100dc576040519150601f19603f3d011682016040523d82523d6000602084013e6100e1565b606091505b5050905080610125576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161011c9061019a565b60405180910390fd5b506101d6565b60006101386007836101c5565b91507f4661696c757265000000000000000000000000000000000000000000000000006000830152602082019050919050565b60006101786000836101ba565b9150600082019050919050565b60006101908261016b565b9150819050919050565b600060208201905081810360008301526101b38161012b565b9050919050565b600081905092915050565b600082825260208201905092915050565b603f806101e46000396000f3fe6080604052600080fdfea264697066735822122095fed2c557b62b9f55f8b3822b0bdc6d15fd93abb95f37503d3f788da6cbb30064736f6c63430008000033'
        hash = await self.send_transaction(to=random_contract.account, data=data, value = value)
        if hash:
            logger.success(f'{self.user} succes deploy contract on Owlto')
            return True
        else:
            logger.error(f"{self.user} can't deplot contract on Owlto") 
            return False


    async def _owlto_get_data(self, output_token: RawContract, input_token: RawContract, amount: TokenAmount):
        if output_token.title == 'ETH': 
            output_token_address = '0x0000000000000000000000000000000000000000'
            output_icon = 'https://owlto.finance/icon/token/eth_logo.png'
            output_decimals = 18
            output_name = output_token.title

        else:
            output_token_address = output_token.address
            output_icon = f'https://owlto.finance/coins/images/6319/large/{output_token.title.lower()}.png?1696506694'
            output_decimals = 6
            if output_token.title == "USDC":
                output_name = "USDC.e"
            else:
                output_name = output_token.title

        if input_token.title == 'ETH': 
            input_token_address = '0x0000000000000000000000000000000000000000'
            input_icon = 'https://owlto.finance/icon/token/eth_logo.png'
            input_decimals = 18
            input_name = input_token.title

        else:
            input_token_address = input_token.address
            input_icon = f'https://owlto.finance/coins/images/6319/large/{input_token.title.lower()}.png?1696506694'
            input_decimals = 6
            if input_token.title == "USDC":
                input_name = "USDC.e"
            else:
                input_name = input_token.title

        user_agent = UserAgent()
        headers = {
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://owlto.finance/swap',
            'sec-ch-ua': '"Not:A-Brand";v="24", "Chromium";v="134"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': f'{user_agent.random}',
        }

        json_data = {
            'source_chain_id': '1868',
            'target_chain_id': '1868',
            'user': f'{self.client.account.address}',
            'recipient': f'{self.client.account.address}',
            'token_in': {
                'address': f'{output_token_address}',
                'decimals': output_decimals,
                'icon': f'{output_icon}',
                'name': f'{output_name}',
            },
            'token_out': {
                'address': f'{input_token_address}',
                'decimals': input_decimals,
                'icon': f'{input_icon}',
                'name': f'{input_name}',
            },
            'slippage': '0.05',
            'amount': f'{amount.Wei}',
            'channel': 98675412,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://owlto.finance/api/swap_api/v1/make_swap', headers=headers, json=json_data, proxy=self.client.proxy) as response:
                try:
                    result = await response.json()
                    return result['data']['contract_calls'][-1]['calldata']
                except Exception as e:
                    logger.error(f'{self.user} Error with response Owlto {e}')
                    return None

    async def owlto_swap_token(self, swap_amount: float, output_token: RawContract, input_token: RawContract):
        contract = await self.client.contracts.get(contract_address=Contracts.OWLTO_SWAP)

        amount = TokenAmount(swap_amount, decimals=6) if output_token.title == 'USDC' or output_token.title == 'USDT' else TokenAmount(swap_amount)
        value = amount if await self.output_token_is_eth(output_token=output_token.title) else TokenAmount(0)

        if output_token.title != 'ETH':
            await self.approve_interface(token_address=output_token, spender=contract, infinity=True)

        data = await self._owlto_get_data(output_token=output_token, input_token=input_token, amount=amount)
        if data:
            hash = await self.send_transaction(to=contract, data=data, value=value)
            if hash:
                logger.success(f'{self.user} success swap on Owlto {output_token.title}({amount.Ether}) to {input_token.title} hash: {hash}')
                return True
            else:
                logger.error(f"{self.user} can't swap on Owlto {output_token.title}({amount.Ether}) to {input_token.title}")
                return False
        else:
            logger.error(f'{self.user} wrong with Owlto response')
            return False

    async def unwrap_weth(self):
        contract = await self.client.contracts.get(contract_address=Contracts.WETH)
        amount = await self.client.wallet.balance(token=Contracts.WETH)
        if not amount:
            return True
        function = 'withdraw'

        params = TxArgs(
                wad=amount.Wei
                )
        data = contract.encodeABI(function, args=params.tuple())
        hash = await self.send_transaction(to=contract, data=data, value = TokenAmount(0))
        if hash:
            logger.success(f'{self.user} success unwrap ETH')
            return True
        else:
            logger.error(f"{self.user} can't unwrap ETH") 
            return False
