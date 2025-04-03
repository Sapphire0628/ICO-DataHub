from config import *
import json
import logging
import requests
import sqlite3

class GetAddressTxn:
    def __init__(self, db_path, etherscan_api_url,etherscan_api_key,  log_file="../Log/get_address_txn.log", save_folder="../DB/creator_txn/"):

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
        self.save_folder = save_folder

    def fetch_address_txn(self, address, start_block=0, end_block=99999999) -> dict:
        """Fetch transaction data for an address from Etherscan API."""
        try:
            response = requests.get(self.etherscan_api_url, params={
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": start_block,
                "endblock": end_block,
                "page": 1,
                "offset" : 10,
                "sort": "asc",
                "apikey": self.etherscan_api_key
            })

            response_data = response.json()

            if response_data["status"] == "1" and response_data["message"] == "OK":
                return {address :response_data["result"]}
            else:
                logging.info(f"Failed to fetch data for address {address}: {response_data['message']}")
                return None
        except Exception as e:
            logging.error(f"Error fetching data for address {address}: {e}")
            return None
        
    def fetch_address_txn_list(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                SELECT Owner FROM tokens WHERE Owner IS NOT NULL;                
            """)
        creator = cursor.fetchall()
        conn.close()
        creator = [c[0] for c in creator]
        return creator


    def start(self):
        creator = self.fetch_address_txn_list()
        print(creator[0])
        result = self.fetch_address_txn(creator[0])
        with open(str(self.save_folder)+f"{creator[0]}.json", "w") as json_file:
            json.dump(result, json_file)

                

        
if __name__ == "__main__":
    getAddressTxn = GetAddressTxn("../DB/data.db", ETHERSCAN_API_URL, ETHERSCAN_API_KEY)
    GetAddressTxn.start(getAddressTxn)

        
    