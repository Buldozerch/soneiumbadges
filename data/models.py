from dataclasses import dataclass

from libs.eth_async.utils.files import read_json
from libs.eth_async.classes import AutoRepr, Singleton
from libs.eth_async.data.models import RawContract, DefaultABIs

from data.config import SETTINGS_FILE, ABIS_DIR



@dataclass
class FromTo:
    from_: int | float
    to_: int | float

class Settings(Singleton, AutoRepr):
    def __init__(self):
        json_data = read_json(path=SETTINGS_FILE)

        self.eth_deposit: FromTo = FromTo(
            from_=json_data['eth_deposit']['from'], to_=json_data['eth_deposit']['to'])
        self.use_arbitrum_for_bridge: bool = json_data['use_arbitrum_for_bridge']
        self.use_base_for_bridge: bool = json_data['use_base_for_bridge']
        self.use_optimism_for_bridge: bool = json_data['use_optimism_for_bridge']
        self.delay_between_start_account: FromTo = FromTo(
            from_=json_data['delay_between_start_account']['from'], to_=json_data['delay_between_start_account']['to'])
        self.delay_between_swaps: FromTo = FromTo(
            from_=json_data['delay_between_swaps']['from'], to_=json_data['delay_between_swaps']['to'])
        self.delay_between_actions: FromTo = FromTo(
            from_=json_data['delay_between_actions']['from'], to_=json_data['delay_between_actions']['to'])
        self.quick_swaps: FromTo = FromTo(
            from_=json_data['quick_swaps']['from'], to_=json_data['quick_swaps']['to'])
        self.owlto_swaps: FromTo = FromTo(
            from_=json_data['owlto_swaps']['from'], to_=json_data['owlto_swaps']['to'])
        self.owlto_multiple_swapper: bool = json_data['owlto_multiple_swapper']
        self.owlto_bridger: bool = json_data['owlto_bridger']
        self.owlto_bridger_times: FromTo = FromTo(
            from_=json_data['owlto_bridger_times']['from'], to_=json_data['owlto_bridger_times']['to'])
        self.sonex_swaps: FromTo = FromTo(
            from_=json_data['sonex_swaps']['from'], to_=json_data['sonex_swaps']['to'])
        self.sonus_swaps: FromTo = FromTo(
            from_=json_data['sonus_swaps']['from'], to_=json_data['sonus_swaps']['to'])
        self.sonus_lock: FromTo = FromTo(
            from_=json_data['sonus_lock']['from'], to_=json_data['sonus_lock']['to'])
        self.sonus_amount_lock: FromTo = FromTo(
            from_=json_data['sonus_amount_lock']['from'], to_=json_data['sonus_amount_lock']['to'])
        self.untiled_bank: FromTo = FromTo(
            from_=json_data['untiled_bank']['from'], to_=json_data['untiled_bank']['to'])
        self.min_max_eth_swap: FromTo = FromTo(
            from_=json_data['min_max_eth_swap']['from'], to_=json_data['min_max_eth_swap']['to'])


class Contracts(Singleton):
    OWLTO_BRIDGE_ARBITRUM = RawContract(
            title = 'OWLTO_BRIDGE_ARBITRUM',
            address = '0x0e83DEd9f80e1C92549615D96842F5cB64A08762',
            abi=read_json(path=(ABIS_DIR, 'owlto_bridge.json'))
            )

    OWLTO_BRIDGE_BASE = RawContract(
            title = 'OWLTO_BRIDGE_BASE',
            address = '0xB5CeDAF172425BdeA4c186f6fCF30b367273DA19',
            abi=read_json(path=(ABIS_DIR, 'owlto_bridge.json'))
            )

    OWLTO_BRIDGE_OPTIMISM = RawContract(
            title = 'OWLTO_BRIDGE_OPTIMISM',
            address = '0x0e83DEd9f80e1C92549615D96842F5cB64A08762',
            abi=read_json(path=(ABIS_DIR, 'owlto_bridge.json'))
            )

    OWLTO_SWAP = RawContract(
            title = 'OWLTO_SWAP',
            address = '0xeAF495068cdF6857E3Fc244ba8Cf031c0EDe50aD',
            abi=read_json(path=(ABIS_DIR, 'owlto_swap.json'))
            )
    
    QUICK_SWAP = RawContract(
            title = 'QUICK_SWAP',
            address = '0xeba58c20629ddab41e21a3E4E2422E583ebD9719',
            abi=read_json(path=(ABIS_DIR, 'quick_swap.json'))
            )
    SONEX = RawContract(
            title = 'SONEX',
            address = '0xDEf357D505690F1b0032a74C3b581163c23d1535',
            abi=read_json(path=(ABIS_DIR, 'sonex.json'))
            )
    SONUS_LOCK = RawContract(
            title = 'SONUS_LOCK',
            address = '0x882Af8BD0A035d4BCEb42DEe8A5A7bC8Ef2F6FF9',
            abi=read_json(path=(ABIS_DIR, 'sonus_lock.json'))
            )
    SONUS_SWAP = RawContract(
            title = 'SONUS_SWAP',
            address = '0xA0133D304c54AB0ba9fBe4468018a5717f460D3a',
            abi=read_json(path=(ABIS_DIR, 'sonus_swap.json'))
            )

    UNTILED_BANK = RawContract(
            title = 'UNTILED_BANK',
            address = '0x2469362f63e9f593087EBbb5AC395CA607B5842F',
            abi=read_json(path=(ABIS_DIR, 'untiled_bank.json'))
            )

    UNTILED_EARN_USDC = RawContract(
            title = 'UNTILED_EARN_USDC',
            address = '0xc675BB95D73CA7db2C09c3dC04dAaA7944CCBA41',
            abi=read_json(path=(ABIS_DIR, 'untiled_earn.json'))
            )

    UNTILED_EARN_WETH = RawContract(
            title = 'UNTILED_EARN_WETH',
            address = '0x232554B4B291A446B4829300bec133FBB07A8f2A',
            abi=read_json(path=(ABIS_DIR, 'untiled_earn.json'))
            )

    USDC = RawContract(
        title='USDC',
        address='0xbA9986D2381edf1DA03B0B9c1f8b00dc4AacC369',
        abi=DefaultABIs.Token,
        # proxy_address='0x2dCc04f35E0E763301Cd482bE13AEa2c62462EC5'
    )

    USDT = RawContract(
        title='USDT',
        address='0x3A337a6adA9d885b6Ad95ec48F9b75f197b5AE35',
        abi=DefaultABIs.Token
    )

    SONUS = RawContract(
        title='SONUS',
        address='0x12BE6BA8Deaa28BC5C2FD9cdfceB47EB4FDB0B35',
        abi=DefaultABIs.Token
    )


    WETH = RawContract(
        title='WETH',
        address='0x4200000000000000000000000000000000000006',
        abi=read_json(path=(ABIS_DIR, 'weth.json'))
    )

    ETH = RawContract(
        title='ETH',
        address='0x4200000000000000000000000000000000000006',
        abi=read_json(path=(ABIS_DIR, 'weth.json'))
    )

    EMPTY_ADDRESS = RawContract(
        title='EMPTY_ADDRESS',
        address='0x0000000000000000000000000000000000000000',
    )
