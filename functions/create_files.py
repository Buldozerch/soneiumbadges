import os

from libs.eth_async.utils.utils import update_dict
from libs.eth_async.utils.files import touch, write_json, read_json

from data import config


def create_files():
    touch(path=config.FILES_DIR)
    touch(path=config.LOG_FILE, file=True)
    touch(path=config.ERRORS_FILE, file=True)
    if not os.path.exists(config.PRIVATE_FILE):
        with open(config.PRIVATE_FILE, 'w') as f:
            pass
    if not os.path.exists(config.PROXY_FILE):
        with open(config.PROXY_FILE, 'w') as f:
            pass
    try:
        current_settings: dict | None = read_json(path=config.SETTINGS_FILE)
    except Exception:
        current_settings = {}

    settings = {
        'eth_deposit': {'from': 0.002, 'to': 0.0025},
        'use_arbitrum_for_bridge' : True,
        'use_base_for_bridge' : True,
        'use_optimism_for_bridge' : True,
        'delay_between_start_account': {'from': 0, 'to': 7200},
        'delay_between_swaps': {'from': 10, 'to': 30},
        'delay_between_actions': {'from': 10, 'to': 40},
        'quick_swaps': {'from': 10, 'to': 12},
        'owlto_swaps': {'from': 3, 'to': 4},
	'owlto_multiple_swapper': False,
	'owlto_bridger': False,
	'owlto_bridger_times': {'from': 5, 'to': 5},
        'sonex_swaps': {'from': 10, 'to': 12},
        'sonus_swaps': {'from': 10, 'to': 12},
        'sonus_lock': {'from': 5, 'to': 5},
        'sonus_amount_lock': {'from': 100, 'to': 101},
        'untiled_bank': {'from': 10, 'to': 12},
        'min_max_eth_swap': {'from': 10, 'to': 30},

    }
    write_json(path=config.SETTINGS_FILE, obj=update_dict(modifiable=current_settings, template=settings), indent=2)

create_files()
