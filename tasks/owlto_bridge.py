import random
from .base import Base
from loguru import logger
from .base import Base
from data.models import Contracts
from libs.eth_async.data.models import TxArgs, TokenAmount
from data.models import Settings
settings = Settings()

class OwltoBridge(Base):
    async def owlto_bridge(self, network: str):
        logger.info(f"{self.client.account.address} start bridge on Owlto from {network} to Soneuim")
        if network.upper() == 'BASE':
            contract = await self.client.contracts.get(contract_address=Contracts.OWLTO_BRIDGE_BASE)
        elif network.upper() == 'ARBITRUM':
            contract = await self.client.contracts.get(contract_address=Contracts.OWLTO_BRIDGE_ARBITRUM)
        elif network.upper() == 'OPTIMISM':
            contract = await self.client.contracts.get(contract_address=Contracts.OWLTO_BRIDGE_OPTIMISM)
        else:
            logger.error(f'{self.client.account.address} unknown network for Owlto Bridge {network}')
            return False
        function = 'Deposit'
        amount = random.uniform(settings.eth_deposit.from_, settings.eth_deposit.to_)
        amount = TokenAmount(amount)
        balance = await self.client.wallet.balance()
        if balance.Ether <= settings.eth_deposit.from_:
            logger.error(f'{self.client.account.address} too many value ETH {balance.Ether} for deposit from this network {network}')
            return False
        if balance.Wei < amount.Wei:
            amount = balance.Wei - 100000000000
            amount = TokenAmount(amount)
        value = amount
        target = str(self.client.account.address)

        params = TxArgs(
            target=target,
            token='0x0000000000000000000000000000000000000000',
            maker=self.client.w3.to_checksum_address('0x1f49a3fa2b5B5b61df8dE486aBb6F3b9df066d86'),
            amount=amount.Wei,
            destination=91,
            channel=98675412,
                )

        data = contract.encodeABI(function, args=params.tuple())
        data = '0xfc180638' + data[10:]

        hash = await self.send_transaction(to=contract, data=data, value=value)
        if hash:
            logger.success(f'{self.client.account.address} success bridge on Owlto ETH({amount.Ether}) from {network} hash: {hash}')
            return True
        else:
            logger.error(f'{self.client.account.address} wrong with bridge on Owlto ETH({amount.Ether}) from {network} hash: {hash}')
            return False 
