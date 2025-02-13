#%%
import time
from datetime import datetime
import sqlite3
from web3 import Web3
import logging
import schedule
from config import *


class TokenScraper:
    def __init__(self, db_path, infura_api_key, erc20_abi, log_file="../sourceCode/Log/token_scraper.log"):
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

    def check_token(self, contract_address, receipt):
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
            created_block = receipt.blockNumber
            logging.info(f"Token {name} ({symbol}) created in block {created_block} Creator: {owner}")

            fetched_at = datetime.now().isoformat()  # e.g., '2025-02-04T10:45:00'

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO tokens 
                    (ContractAddress,creator, TokenName, Symbol, TotalSupply, Decimal, CreatedBlock, FetchedAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (contract_address,owner, name, symbol, total_supply, decimals, created_block, fetched_at),
                )
                conn.commit()

            logging.info(f"Token {name} ({symbol}) stored in database.")

        except Exception as e:
            logging.error(f"Error processing token at {contract_address}: {e}")

    def process_block(self, block, processed_contracts):
        for tx in block.transactions:
            # Check if the transaction created a contract
            if tx.to is None:  # 'to' is None for contract creation
                try:
                    receipt = self.web3.eth.get_transaction_receipt(tx.hash)
                    contract_address = receipt.contractAddress

                    if contract_address and contract_address not in processed_contracts:
                        processed_contracts.add(contract_address)  # Mark as processed
                        self.check_token(contract_address, receipt)  # Call the function
                except Exception as e:
                    logging.error(f"Error processing transaction {tx.hash.hex()} (Not ERC20 Contract Creation) : {e}")

    def monitor_blocks(self, start_offset=100, sleep_interval=5):
        logging.info("Listening for new blocks...")
        processed_contracts = set()  # Track already processed contract addresses

        try:
            # Initial setup
            initial_latest = self.web3.eth.block_number
            start_block = max(0, initial_latest - start_offset)
            logging.info(f"Starting from block {start_block} up to {initial_latest}")

            # Process historical blocks
            for block_num in range(start_block, initial_latest + 1):
                block = self.web3.eth.get_block(block_num, full_transactions=True)
                self.process_block(block, processed_contracts)

            # Now monitor new blocks
            last_processed = initial_latest
            while True:
                current_latest = self.web3.eth.block_number
                if current_latest > last_processed:
                    logging.info(f"Processing blocks from {last_processed + 1} to {current_latest}")
                    for block_num in range(last_processed + 1, current_latest + 1):
                        block = self.web3.eth.get_block(block_num, full_transactions=True)
                        self.process_block(block, processed_contracts)
                    last_processed = current_latest
                else:
                    # No new blocks, sleep for a bit
                    time.sleep(sleep_interval)

        except KeyboardInterrupt:
            logging.info("\nStopped monitoring.")
        except Exception as e:
            logging.error(f"Error: {e}")

    def start(self):
        """
        Schedule periodic tasks for checking new tokens and missing source code.
        """
        logging.info("Starting the scheduler...")

        # Run the scheduler
        while True:
            self.monitor_blocks(start_offset=100, sleep_interval=10)
            


def main():
    # Set database path and API configurations
    tokenscraper = TokenScraper(DB_PATH, INFURA_API_KEY, ERC20_ABI)
    tokenscraper.start()

if __name__ == "__main__":
    main()