#%%
import os
import sqlite3
import re
import json
import time
import logging
from config import *

class SocialMediaExtractor:
    """
    A class to extract and update social media URLs (Twitter, Telegram, Website) 
    from contract source code and update the tokens table in the database.
    """

    def __init__(self, db_path, log_file="../sourceCode/Log/social_media_extractor.log"):
        """
        Initialize the extractor with database path and logging configuration.
        """
        self.db_path = db_path
        

        # Set up logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # URL extraction regex patterns
        self.url_patterns = {
            "twitter": r"(https?://(x\.com|twitter\.com)/[^\s\/\\]+)",  # Match Twitter URLs
            "telegram": r"(https?://t\.me/[^\s\\]+)",  # Match Telegram URLs
            "website": r"(https?://[^\s\\]+)",  # Match any general URL
        }

    def clean_url(self, url):
        """
        Clean and normalize extracted URLs.
        """
        if url:
            url = url.strip().rstrip("\\\r\n")
            # Remove fragments or invalid characters
            for delim in ["#", "[", "]", "(", ")"]:
                if delim in url:
                    url = url.split(delim)[0]
            return url
        return None

    def get_source_content(self, source_code_json):
        """
        Extract the first available 'content' from a JSON source.
        """
        try:
            source_data = json.loads(source_code_json)
            for value in source_data.get("sources", {}).values():
                if "content" in value:
                    return value["content"]
        except (json.JSONDecodeError, AttributeError):
            pass
        return source_code_json  # Fallback to plain text if parsing fails

    def extract_urls(self, source_code):
        """
        Extract Twitter, Telegram, and general website URLs from source code.
        """
        extracted_urls = {key: None for key in self.url_patterns}
        all_urls = re.findall(self.url_patterns["website"], source_code)

        for key, pattern in self.url_patterns.items():
            match = re.search(pattern, source_code)
            if match:
                extracted_urls[key] = self.clean_url(match.group(1))

        # Find the first general website URL not matching Twitter/Telegram
        for url in all_urls:
            clean = self.clean_url(url)
            if clean and clean not in (extracted_urls["twitter"], extracted_urls["telegram"]):
                extracted_urls["website"] = clean
                break

        return extracted_urls["twitter"], extracted_urls["website"], extracted_urls["telegram"]

    def update_tokens_table(self):
        """
        Update the tokens table with extracted URLs.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ContractAddress, SourceCode 
                FROM contracts
                WHERE SourceCode IS NOT NULL;
                
            """)
            contracts = cursor.fetchall()
            


            for contract_address, source_code in contracts:
                twitter_url, website_url, telegram_url = self.extract_urls(source_code)



                # Fetch existing token data for comparison
                cursor.execute("""
                    SELECT TwitterUrl,TwitterUser, WebsiteUrl, TelegramUrl 
                    FROM tokens
                    WHERE ContractAddress = ?
                """, (contract_address,))
                token_data = cursor.fetchone()

                updates = []
                # Skip if no token data exists
                if token_data is None:
                    logging.warning(f"No token data found for ContractAddress: {contract_address}")
                    continue



                if  token_data[0] is None and twitter_url:
                    
                    updates.append(("TwitterUrl", twitter_url))
                    print(twitter_url)
                if token_data[1] is None and twitter_url:
            
                    twitter_user = re.search(r"^https:\/\/(?:x\.com|twitter\.com)\/([a-zA-Z0-9_]+)$", twitter_url)
                    if twitter_user:
                        twitter_user = twitter_user.group(1)  # Extract username
                        updates.append(("TwitterUser", twitter_user))
                        print(twitter_user)


                if token_data[2] is None and website_url:
                    updates.append(("WebsiteUrl", website_url))
                if token_data[3] is None and telegram_url:
                    updates.append(("TelegramUrl", telegram_url))

                # Apply updates only if there are changes
                for column, value in updates:
                    # Ensure value is a valid SQLite type
                    if not isinstance(value, (str, type(None))):
                        raise ValueError(f"Invalid data type for column {column}: {type(value)}")
                            
                    cursor.execute(f"""
                        UPDATE tokens
                        SET {column} = ?
                        WHERE ContractAddress = ?
                    """, (value, contract_address))

                    conn.commit()
            logging.info("Tokens table updated successfully.")
            time.sleep(60)

        except sqlite3.Error as e:
            logging.error(f"An error occurred: {e}")


    def start(self):
        """
        Schedule periodic tasks for checking new tokens and missing source code.
        """
        logging.info("Starting the scheduler...")


        # Run the scheduler
        while True:
            self.update_tokens_table()



def main():
    # Set database path and API configurations
    social_media_extractor = SocialMediaExtractor(DB_PATH)
    social_media_extractor.start()

if __name__ == "__main__":
    main()