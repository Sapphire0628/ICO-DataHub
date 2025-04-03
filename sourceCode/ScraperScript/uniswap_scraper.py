import logging
import requests
import sqlite3
from config import *
import time



class UniswapScraper:
    def __init__(self, db_path, log_file="../sourceCode/Log/uniswap_scraper.log"):
        self.db_path = db_path
        self.log_file = log_file
        
        # Set up logging
        self.logger = logging.getLogger('UniswapScraper')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(fh)

    def fetch_address(self):
        self.logger.info("Fetching addresses from database")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                SELECT ContractAddress FROM tokens WHERE isSpam IS NULL;                
            """)
        # WHERE isSpam IS NULL
        address = cursor.fetchall()
        conn.close()
        address = [c[0] for c in address]
        self.logger.info(f"Found {len(address)} addresses to process")
        return address

    def update_basic(self, address, isSpam, safetyLevel, spamCode):
        self.logger.info(f"Updating database for address: {address}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                    UPDATE tokens SET isSpam = ?, safetyLevel = ?, spamCode = ? WHERE ContractAddress = ?;
                """, (isSpam, safetyLevel, spamCode, address))
            conn.commit()
            self.logger.info("Database update successful")
        except Exception as e:
            self.logger.error(f"Error updating database: {str(e)}")
        finally:
            conn.close()
    
    def update_potential_spam(self, address, isPotentialSpam, attackTypes):
        self.logger.info(f"Updating database for address: {address}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                    UPDATE tokens SET isPotentialSpam = ?, attackTypes = ? WHERE ContractAddress = ?;
                """, (isPotentialSpam, attackTypes, address))
            conn.commit()
            self.logger.info("Database update successful")
        except Exception as e:
            self.logger.error(f"Error updating database: {str(e)}")
        finally:
            conn.close()

    def scrape_by_ca(self, address_list):
        self.logger.info(f"Starting scraping for {len(address_list)} addresses")
        for address in address_list:

            self.logger.info(f"Processing address: {address}")
            json_data = {
                'operationName': 'Token',
                'variables': {
                    'chain': 'ETHEREUM',
                    'address': address,
                },
                'query': 'query Token($chain: Chain!, $address: String) {\n  token(chain: $chain, address: $address) {\n    ...TokenParts\n    __typename\n  }\n}\n\nfragment TokenParts on Token {\n  ...TokenBasicInfoParts\n  ...TokenBasicProjectParts\n  ...TokenFeeDataParts\n  ...TokenProtectionInfoParts\n  __typename\n}\n\nfragment TokenBasicInfoParts on Token {\n  id\n  address\n  chain\n  decimals\n  name\n  standard\n  symbol\n  __typename\n}\n\nfragment TokenBasicProjectParts on Token {\n  project {\n    id\n    isSpam\n    logoUrl\n    name\n    safetyLevel\n    spamCode\n    tokens {\n      chain\n      address\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TokenFeeDataParts on Token {\n  feeData {\n    buyFeeBps\n    sellFeeBps\n    __typename\n  }\n  __typename\n}\n\nfragment TokenProtectionInfoParts on Token {\n  protectionInfo {\n    result\n    attackTypes\n    blockaidFees {\n      buy\n      sell\n      transfer\n      __typename\n    }\n    __typename\n  }\n  __typename\n}',
            }
            time.sleep(10)

            try:
                response = requests.post('https://interface.gateway.uniswap.org/v1/graphql', headers=UNISWAP_HEADERS, json=json_data)
                result = response.json()['data']['token']['project']

                isSpam = result['isSpam']
                if isSpam == False:
                    isSpam = 0
                else:
                    isSpam = 1
                safetyLevel = result['safetyLevel']
                spamCode = result['spamCode']
                protectionInfo = response.json()['data']['token']['protectionInfo']
                self.update_basic(address, isSpam, safetyLevel, spamCode)

                if protectionInfo:
                    isPotentialSpam = protectionInfo['result']
                    if len(protectionInfo['attackTypes']) > 1:
                        attackTypes = ','.join(protectionInfo['attackTypes'])
                    else:
                        attackTypes = protectionInfo['attackTypes'][0]
                    

                    self.update_potential_spam(address, isPotentialSpam, attackTypes)

                self.logger.info(f"Successfully processed address: {address}")
                
                

            except Exception as e:
                self.logger.error(f"Error processing address {address}: {str(e)}")
            
            

    def start(self):
        self.logger.info("Starting UniswapScraper")
        address_list = self.fetch_address()
        self.scrape_by_ca(address_list)
        self.logger.info("UniswapScraper finished")

if __name__ == "__main__":
    uniswapScraper = UniswapScraper(db_path = DB_PATH)
    uniswapScraper.start()