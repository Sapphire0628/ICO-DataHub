#%%
import requests
from config import *
import sqlite3
import logging
from web3 import Web3
from datetime import datetime

class DextoolScraper:
    def __init__(self, db_path, infura_api_key, erc20_abi, log_file="../sourceCode/Log/dextool_scraper.log"):

        # Set up logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        
        # Initialize Web3 provider
        self.web3 = Web3(Web3.HTTPProvider(infura_api_key))
        
        # Set database path and ABI
        self.db_path = db_path
        self.erc20_abi = erc20_abi

    def fetch_old_address(self):
        logging.info("Fetching addresses from database")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                SELECT ContractAddress FROM tokens WHERE pairAddress IS '0x0000000000000000000000000000000000000000';                
            """)
        # WHERE isSpam IS NULL
        address = cursor.fetchall()
        conn.close()
        address = [c[0] for c in address]
        logging.info(f"Found {len(address)} addresses to process")
        return address

    def check_token(self, contract_address, result):
        try:
            # Create a contract object
            contract = self.web3.eth.contract(address=contract_address, abi=self.erc20_abi)

            # Fetch token details
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            total_supply = contract.functions.totalSupply().call() / (10 ** decimals)
            owner = contract.functions.owner().call()
            
            # Store the token details in the SQLite database
            
            created_block = result['pair']['creationBlock']
            
            pair_address, TwitterUrl, WebsiteUrl, TelegramUrl, is_open_source, is_honeypot, is_mintable, is_proxy, slippage_modifiable, is_blacklisted, min_sell_tax, max_sell_tax, min_buy_tax, max_buy_tax, is_contract_renounced, is_potentially_scam, transfer_pausable, warnings = self.process_dextool_data(contract_address, result)   

            logging.info(f"Token {name} ({symbol}) created in block {created_block} Owner: {owner}")

            fetched_at = datetime.now().isoformat()  # e.g., '2025-02-04T10:45:00'

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO tokens 
                    (ContractAddress,pairAddress, Owner, TokenName, Symbol, TotalSupply, Decimal, CreatedBlock, FetchedAt, TwitterUrl, WebsiteUrl, TelegramUrl, is_open_source, is_honeypot, is_mintable, is_proxy, slippage_modifiable, is_blacklisted, min_sell_tax, max_sell_tax, min_buy_tax, max_buy_tax, is_contract_renounced, is_potentially_scam, transfer_pausable, warnings)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (contract_address,pair_address, owner, name, symbol, total_supply, decimals, created_block, fetched_at, TwitterUrl, WebsiteUrl, TelegramUrl, is_open_source, is_honeypot, is_mintable, is_proxy, slippage_modifiable, is_blacklisted, min_sell_tax, max_sell_tax, min_buy_tax, max_buy_tax, is_contract_renounced, is_potentially_scam, transfer_pausable, warnings),
                )
                conn.commit()

            logging.info(f"Updating database for address: {contract_address} , pair address: {pair_address}")

        except Exception as e:
            logging.error(f"Error processing token at {contract_address}: {e}")
    
    def process_dextool_data(self,contractAddress, result):

        TwitterUrl = result['token']['links']['twitter']
        WebsiteUrl = result['token']['links']['website']
        TelegramUrl = result['token']['links']['telegram']
        audit = result['token']['audit']['dextools']
        is_open_source = audit['is_open_source'] # Can detect when launch
        is_honeypot = audit['is_honeypot']       # Can detect when launch
        is_mintable = audit['is_mintable']       # Can detect when launch
        is_proxy = audit['is_proxy']             # ...? 
        slippage_modifiable = audit['slippage_modifiable']   # Can't detect when launch
        is_blacklisted = audit['is_blacklisted']             # Can detect when launch
        sell_tax = audit['sell_tax']                         # ...? 
        min_sell_tax = sell_tax['min']
        max_sell_tax = sell_tax['max']                       # ...?
        buy_tax = audit['buy_tax']                           # ...?
        min_buy_tax = buy_tax['min']
        max_buy_tax = buy_tax['max'] 
        is_contract_renounced = audit['is_contract_renounced']# Can't detect when launch
        is_potentially_scam = audit['is_potentially_scam']      
        transfer_pausable = audit['transfer_pausable']        # Can detect when launch
        warnings = audit['summary']['providers']['warning']
        pair_address = self.get_pair_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', contractAddress)
        if len(warnings) > 0:
            warnings = ','.join(warnings)
        else:
            warnings = None 
        return pair_address, TwitterUrl, WebsiteUrl, TelegramUrl, is_open_source, is_honeypot, is_mintable, is_proxy, slippage_modifiable, is_blacklisted, min_sell_tax, max_sell_tax, min_buy_tax, max_buy_tax, is_contract_renounced, is_potentially_scam, transfer_pausable, warnings

    
    def update_dextool_info(self, address,pair_address, TwitterUrl, WebsiteUrl, TelegramUrl, is_open_source, is_honeypot, is_mintable, is_proxy, slippage_modifiable, is_blacklisted, min_sell_tax, max_sell_tax, min_buy_tax, max_buy_tax, is_contract_renounced, is_potentially_scam, transfer_pausable, warnings):
        logging.info(f"Updating database for address: {address} , pair address: {pair_address}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                    UPDATE tokens SET pairAddress = ?, TwitterUrl = ?, WebsiteUrl = ?, TelegramUrl = ?, is_open_source = ?, is_honeypot = ?, is_mintable = ?,  is_proxy = ?, slippage_modifiable = ?, is_blacklisted = ?, min_sell_tax = ?, max_sell_tax = ?, min_buy_tax = ?,  max_buy_tax = ?, is_contract_renounced = ?, is_potentially_scam = ?, transfer_pausable = ?, warnings = ?  WHERE ContractAddress = ?;
                """, (pair_address, TwitterUrl, WebsiteUrl, TelegramUrl, is_open_source, is_honeypot, is_mintable, is_proxy, slippage_modifiable, is_blacklisted, min_sell_tax, max_sell_tax, min_buy_tax, max_buy_tax, is_contract_renounced, is_potentially_scam, transfer_pausable, warnings, address))
            conn.commit()
            logging.info("Database update successful")
        except Exception as e:
            logging.error(f"Error updating database: {str(e)}")
        finally:
            conn.close()

    def scrape_good_token(self):
        for page in range(1, 15):
            try:
                params = {
                    'limit': '51',
                    'interval': '24h',
                    'page': str(page),
                    'chain': 'ether',
                    'exchange': 'univ2',
                    'dextScore': '80',
                    'audit': 'verified',
                    'creationLowerTimeRange': '31104000000',
                }
                

                response = requests.get('https://www.dextools.io/shared/analytics/pairs', params=params, headers=headers).json()
                for i in response['data']:
                    ContractAddress = Web3.to_checksum_address(i['_id']['token'])
                    scraper.check_token(ContractAddress, i)
            except Exception as e:
                print(e)

    def get_pair_address(self, token0, token1):
        factory_contract = self.web3.eth.contract(address=FACTORY_ADDRESS, abi=FACTORY_ABI)
        # Ensure checksum addresses
        token0 = self.web3.to_checksum_address(token0)
        token1 = self.web3.to_checksum_address(token1)
        
        # Call getPair function
        pair_address = factory_contract.functions.getPair(token0, token1).call()
        return pair_address
        
    def scrape_old_info(self):
        
        address_list = self.fetch_old_address()
        
        
        for contractAddress in address_list:
            
            try:
                pair_address = self.get_pair_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', contractAddress)
                if pair_address == "0x0000000000000000000000000000000000000000":
                    continue

                params = {
                'address':  pair_address.lower(),
                'chain': 'ether',
                'audit': 'true',
                }
                result = requests.get('https://www.dextools.io/shared/data/pair', params=params, cookies=DEXTOOL_COOKIES, headers=DEXTOOL_HEADERS).json()
                result = result['data'][0]

            
            
                pair_address, TwitterUrl, WebsiteUrl, TelegramUrl, is_open_source, is_honeypot, is_mintable, is_proxy, slippage_modifiable, is_blacklisted, min_sell_tax, max_sell_tax, min_buy_tax, max_buy_tax, is_contract_renounced, is_potentially_scam, transfer_pausable, warnings = self.process_dextool_data(contractAddress, result)  
                self.update_dextool_info(contractAddress,pair_address,  TwitterUrl, WebsiteUrl, TelegramUrl, is_open_source, is_honeypot, is_mintable, is_proxy, slippage_modifiable, is_blacklisted, min_sell_tax, max_sell_tax, min_buy_tax, max_buy_tax, is_contract_renounced, is_potentially_scam, transfer_pausable, warnings)
            except Exception as e:
                logging.error(f"Error processing token at {contractAddress}: {e}")
                continue
                        





if __name__ == "__main__":
    scraper = DextoolScraper(DB_PATH, INFURA_API_KEY, ERC20_ABI)
    #scraper.scrape_good_token()
    response = scraper.scrape_old_info()

    
