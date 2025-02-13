#%%
import sqlite3
import re
import requests
from twitter_config import *
import time

def get_twitter_name(db_path: str) -> list:
    """Fetches all SourceCode values from the contracts table and returns them as a list."""
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Execute SQL query to fetch SourceCode column
        cursor.execute("SELECT TwitterUrl FROM tokens")
        twitter_users = cursor.fetchall()

        clear_twitter_users_list = list(
            {  # Use a set to automatically handle duplicates
                re.search(r"^https:\/\/(?:x\.com|twitter\.com)\/([a-zA-Z0-9_]+)$", user).group(1)
                for user in (user[0] for user in twitter_users)  # Extract the first element 
                if user is not None and re.match(r"^https:\/\/(?:x\.com|twitter\.com)\/[a-zA-Z0-9_]+$", user)
            }
            
        )
        return clear_twitter_users_list

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        # Close the connection
        conn.close()


# Example usage
if __name__ == "__main__":
    database_path = "../database/data.db"  # Replace with your database path
    source_code_list = get_twitter_name(database_path)
    print("SourceCode List:", source_code_list)
    for i in source_code_list:
        params = {
                'variables': f'{{"screen_name":"{i}"}}',
                'features': get_user_id_features,
                'fieldToggles': fieldToggles,
            }
        try:
            response = requests.get(get_user_id_url, params=params, cookies=cookies, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            response_json = response.json()
            # Extract the user ID from the response
            if response_json['data'] != {}:

                user_id = response_json['data']['user']['result']['rest_id']
                description = response_json['data']['user']['result']['legacy']['description']
                created_at = response_json['data']['user']['result']['legacy']['created_at']
                print(description)
                print(created_at)

                time.sleep(5)
            

                print(f"User ID for {i}: {user_id}")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            continue

# %%
