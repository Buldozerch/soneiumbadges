import os
import sys
from pathlib import Path

from loguru import logger
from dotenv import load_dotenv


load_dotenv()


if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

ABIS_DIR = os.path.join(ROOT_DIR, 'data', 'abis')
FILES_DIR = os.path.join(ROOT_DIR, 'files')

LOG_FILE = os.path.join(FILES_DIR, 'log.log')
ERRORS_FILE = os.path.join(FILES_DIR, 'errors.log')

PRIVATE_FILE = os.path.join(FILES_DIR, 'private.txt')
PROXY_FILE = os.path.join(FILES_DIR, 'proxy.txt')

SETTINGS_FILE = os.path.join(FILES_DIR, 'settings.json')

WALLETS_DB = os.path.join(FILES_DIR, 'wallets.db')

logger.add(ERRORS_FILE, level='ERROR')
logger.add(LOG_FILE, level='INFO')

# logger.info('INFO')
# logger.debug('DEBUG')
# logger.success('SUCCESS')
# logger.warning('WARNING')
# logger.error('ERROR')
# logger.critical('CRITICAL')
