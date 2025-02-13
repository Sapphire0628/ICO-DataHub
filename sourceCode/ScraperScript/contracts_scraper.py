
#########################################################################################################################################################
#                                                                                                                                                       #   
# Every 1 minute: The script checks for new tokens in the tokens table and fetches their contract info if not already in the contracts table.           #        
#                                                                                                                                                       #
# Every 5 minutes: The script checks the contracts table for entries without source code and attempts to re-fetch the data                              #
#                                                                                                                                                       #
#########################################################################################################################################################
import requests
import sqlite3
from datetime import datetime
import schedule
import time
import logging
from config import *


class ContractScraper:
    def __init__(self, db_path, etherscan_api_url, etherscan_api_key, log_file="../sourceCode/Log/contracts_scraper.log"):
        # Initialize logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Set database path and API configurations
        self.db_path = db_path
        self.etherscan_api_url = etherscan_api_url
        self.etherscan_api_key = etherscan_api_key

    def fetch_contract_data(self, contract_address):
        """
        Fetch contract data from Etherscan API.
        """
        try:
            response = requests.get(self.etherscan_api_url, params={
                "module": "contract",
                "action": "getsourcecode",
                "address": contract_address,
                "apikey": self.etherscan_api_key
            })

            response_data = response.json()

            if response_data["status"] == "1" and response_data["message"] == "OK":
                result = response_data["result"][0]

                return {
                    "SourceCode": result["SourceCode"],
                    "CompilerVersion": result["CompilerVersion"],
                    "OptimizationUsed": result["OptimizationUsed"],
                    "Runs": result["Runs"],
                    "EVMVersion": result["EVMVersion"],
                    "Library": result["Library"],
                    "LicenseType": result["LicenseType"],
                    "Proxy": result["Proxy"],
                    "Implementation": result["Implementation"],
                    "SwarmSource": result["SwarmSource"]
                }
            else:
                logging.info(f"Failed to fetch data for contract {contract_address}: {response_data['message']}")
                return None
        except Exception as e:
            logging.error(f"Error fetching data for contract {contract_address}: {e}")
            return None

    def save_contract_data_to_db(self, contract_address, contract_data):
        """
        Save contract data to the SQLite database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get the current timestamp
                fetched_at = datetime.now().isoformat()

                # Insert or update contract data with fetching time
                cursor.execute("""
                    INSERT OR REPLACE INTO contracts (
                        contractAddress, SourceCode, CompilerVersion, OptimizationUsed, Runs, EVMVersion, 
                        Library, LicenseType, Proxy, Implementation, SwarmSource, FetchedAt
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contract_address,
                    contract_data["SourceCode"],
                    contract_data["CompilerVersion"],
                    contract_data["OptimizationUsed"],
                    contract_data["Runs"],
                    contract_data["EVMVersion"],
                    contract_data["Library"],
                    contract_data["LicenseType"],
                    contract_data["Proxy"],
                    contract_data["Implementation"],
                    contract_data["SwarmSource"],
                    fetched_at
                ))
                conn.commit()
                logging.info(f"Contract {contract_address} data saved to the database at {fetched_at}.")
        except Exception as e:
            logging.error(f"Error saving contract {contract_address} to the database: {e}")

    def check_new_tokens(self):
        """
        Check for new tokens in the tokens table and fetch their contract info.
        """
        logging.info("Checking for new tokens...")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Find contract addresses in tokens table that are not in contracts table
                cursor.execute("""
                    SELECT t.contractAddress
                    FROM tokens t
                    LEFT JOIN contracts c ON t.contractAddress = c.contractAddress
                    WHERE c.contractAddress IS NULL
                """)
                new_tokens = [row[0] for row in cursor.fetchall()]

            # Fetch and save contract data for new tokens
            for contract_address in new_tokens:
                logging.info(f"Fetching data for new contract: {contract_address}")
                contract_data = self.fetch_contract_data(contract_address)
                if contract_data:
                    self.save_contract_data_to_db(contract_address, contract_data)
       

        except Exception as e:
            logging.error(f"Error checking new tokens: {e}")

    def check_missing_source_code(self):
        """
        Check contracts table for entries without source code and re-fetch them.
        """
        logging.info("Checking for contracts missing source code...")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Find contracts with empty SourceCode
                cursor.execute("""
                    SELECT contractAddress
                    FROM contracts
                    WHERE SourceCode IS NULL OR SourceCode = ''
                """)
                missing_source_contracts = [row[0] for row in cursor.fetchall()]

            # Re-fetch and update contract data
            for contract_address in missing_source_contracts:
                logging.info(f"Re-fetching data for contract: {contract_address}")
                contract_data = self.fetch_contract_data(contract_address)
                if contract_data:
                    self.save_contract_data_to_db(contract_address, contract_data)

        except Exception as e:
            logging.error(f"Error checking contracts missing source code: {e}")

    def start(self):
        """
        Schedule periodic tasks for checking new tokens and missing source code.
        """
        logging.info("Starting the scheduler...")

        # Schedule tasks
        schedule.every(1).minutes.do(self.check_new_tokens)
        schedule.every(4).minutes.do(self.check_missing_source_code)

        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)


def main():
    # Set database path and API configurations
    contractscraper = ContractScraper(DB_PATH, ETHERSCAN_API_URL, ETHERSCAN_API_KEY)
    contractscraper.start()


if __name__ == "__main__":
    main()