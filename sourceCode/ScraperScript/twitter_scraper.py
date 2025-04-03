#%%
import re
import math
import time
import json
import requests
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from config import *
import schedule
import logging
import random
from functools import partial


class TweetDatabase:
    """處理用於儲存和檢索推文 tweets 資料的所有資料庫互動。"""
    #Done
    def __init__(self, db_path):
        self.db_path = db_path

    # Done 
    def get_connection(self):
        """建立並返回新的資料庫連接"""
        return sqlite3.connect(self.db_path)

    # Done 
    def update_tweets(self, user_id: str, tweets: List[Dict[str, Any]]):
        """更新用戶的最新推文"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """
            INSERT OR REPLACE INTO tweets (
                user_id, tweet_id, tweet_full_text, tweet_favorite_count, tweet_view_count, tweet_quote_count,
                tweet_reply_count, tweet_retweet_count, tweet_created_at, user_name, tweet_mention_list
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for tweet in tweets:
                cursor.execute(query, (user_id, tweet["tweet_id"], tweet["tweet_full_text"], tweet["tweet_favorite_count"],tweet["tweet_view_count"],tweet["tweet_quote_count"],tweet["tweet_reply_count"],tweet["tweet_retweet_count"],tweet["tweet_created_at"],tweet["user_name"],tweet["tweet_mention_list"]))
                conn.commit()


        except sqlite3.Error as e:
            logging.info(f"Database error (update_tweets): {e}")

    # Done
    def get_new_twitter_users_from_db(self) -> List[str]:
        """從 token 表中獲取所有 Twitter URL，提取用戶名，並僅傳回 twitter_user 表中尚不存在的 Twitter URL。"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # SQL query to fetch Twitter URLs from the tokens table that are NOT in the twitter_user table
            query = """
            SELECT t.TwitterUser 
            FROM tokens t
            WHERE t.TwitterUser IS NOT NULL 
            AND NOT EXISTS (
                SELECT 1 FROM twitter_users u WHERE u.username = t.TwitterUser
            )
            """
            cursor.execute(query)
            twitter_user = cursor.fetchall()

            # Extract and clean Twitter usernames
            return list(set(twitter_user))
        
        except sqlite3.Error as e:
            logging.info(f"Database error (get_twitter_users_from_db): {e}")
            return []
        except Exception as e:
            logging.info(f"Error processing Twitter URLs: {e}")
            return []
    
    def save_user_info(self, user_dict :Dict[str, Any]):
        """儲存使用者資訊到資料庫"""

        query = """
        INSERT OR REPLACE INTO twitter_users (
            user_id, username, created_time, description, available
        ) VALUES (?, ?, ?, ?, ?)
        """
        try:
            # Execute the query with values from user_dict
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    user_dict.get("user_id"),
                    user_dict.get("username"),
                    user_dict.get("created_time"),
                    user_dict.get("description"),
                    "True"
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            logging.info(f"Database error (save_user_info): {e}")
        except Exception as ex:
            logging.info(f"Unexpected error (save_user_info): {ex}")

        
    def save_unavailable_user_info(self, username):
        """儲存使用者資訊到資料庫"""

        query = """
        INSERT OR REPLACE INTO twitter_users (
            user_id, username, created_time, description, available
        ) VALUES (?, ?, ?, ?, ?)
        """
        try:
            # Execute the query with values from user_dict
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    None,
                    username,
                    None,
                    None,
                    "False"
                ),
            )
            conn.commit()

        except sqlite3.Error as e:
            logging.info(f"Database error (save_unavailable_user_info): {e}")
        except Exception as ex:
            logging.info(f"Unexpected error (save_unavailable_user_info): {ex}")

    def get_all_user_ids(self) -> List[Any]:
        """從 twitter_user 表中檢索所有使用者 ID"""
        query = "SELECT user_id FROM twitter_users WHERE available = 'True'"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            user_ids = [row[0] for row in cursor.fetchall()]  # Extract the first column (user_id) from each row

            return user_ids
        except sqlite3.Error as e:
            logging.info(f"Database error (get_all_user_ids): {e}")
            return []
        except Exception as ex:
            logging.info(f"Unexpected error (get_all_user_ids): {ex}")
            return []



class TwitterScraper:
    """Handles scraping of tweets from the Twitter API."""

    def __init__(self, get_tweet_url: str,get_user_url:str, auth: List[List[Any]] , get_tweet_features: str,get_user_features:str, tweet_fieldToggles: Optional[str] = None, user_fieldToggles: Optional[str] = None, log_file: str = "../sourceCode/Log/twitter_scraper.log"):
        self.tweet_url = get_tweet_url
        self.user_url = get_user_url
        self.auth = auth
        self.get_tweet_features = get_tweet_features
        self.get_user_features = get_user_features
        self.tweet_fieldToggles = tweet_fieldToggles
        self.user_fieldToggles = user_fieldToggles

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    # Done
    def build_get_tweets_params(self, user_id: str, count: int) -> Dict[str, Any]:
        variables = {
            "userId": user_id,
            "count": count,
            "includePromotedContent": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withVoice": True,
            "withV2Timeline": True
        }
        return {
            'variables': json.dumps(variables),
            'features': self.get_tweet_features,
            'fieldToggles': self.tweet_fieldToggles,
        }

    # Done 
    def build_get_user_params(self, screen_name: str) -> Dict[str, Any]:
        variables = {
            "screen_name": screen_name,
        }
        return {
            'variables': json.dumps(variables),
            'features': self.get_user_features,
            'fieldToggles': self.user_fieldToggles,
        }
    
    # Done
    def fetch(self,url:str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch tweets from the Twitter API."""
        try:

            auth_set = random.choice(self.auth)
            response = requests.get(url, params=params, cookies=auth_set[0], headers=auth_set[1])
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            logging.info(f"Error fetching tweets (fetch): {e}")
            
            return {}
    
    
    def get_user(self, screen_name: str ,db: TweetDatabase) -> Optional[str]:
        """ 取得給定 username 的 user id"""
        params = self.build_get_user_params(screen_name)

        try:
            response_json = self.fetch(self.user_url, params)
            
            # Extract user ID from the response
            if response_json['data'] != {}: # Check if the response is not empty
                
                user_result = response_json['data']['user']['result']
                self.process_user_response(user_result, screen_name, db)
            if response_json['data'] == {}:
                db.save_unavailable_user_info(screen_name)

        except requests.exceptions.RequestException as e:
            logging.info(f"HTTP request error (get_user): {e}")
        except KeyError as e:
            logging.info(f"Error parsing response (get_user): {e}")

        return None
    
    def process_user_response(self, user_result: dict, username:str,  db: TweetDatabase) -> Optional[Dict[str, Any]]:
        """Parse user data."""
        try:
            if "message" in user_result:
                db.save_unavailable_user_info(username)
                return None
            else:
                db.save_user_info({
                    "user_id": user_result['rest_id'],
                    "username": username,
                    "created_time":  user_result['legacy']['created_at'],
                    "description": user_result['legacy']['description'],
                })
                                
        except KeyError as e:
            logging.info(f"Error parsing response (get_user): {e}")


    def get_latest_tweets(self, user_id: str, count: int = 30) -> List[Dict[str, Any]]:
        """Get the latest tweets for a user."""
        params = self.build_get_tweets_params(user_id, count)
        response_json = self.fetch(self.tweet_url, params)

        try:
            response_entries = response_json['data']['user']['result']['timeline_v2']['timeline']['instructions'][-1]['entries']

            return self.process_tweet_response(response_entries)
        except (KeyError, IndexError) as e:
            logging.info(f"Error processing response (get_latest_tweets): {e}")
            return []
    

    # Done 
    def parse_tweet(self,tweet_id, tweet_results: dict) -> Optional[Dict[str, Any]]:
        """Parse individual tweet data."""
        try:
            tweet_content = tweet_results['legacy']
            user_content = tweet_results['core']['user_results']['result']['legacy']

            return {
                "tweet_id": tweet_id,
                "tweet_full_text": tweet_content['full_text'],
                "tweet_favorite_count": tweet_content['favorite_count'],
                "tweet_view_count": tweet_results.get('views', {}).get('count', 0),
                "tweet_quote_count": tweet_content['quote_count'],
                "tweet_reply_count": tweet_content['reply_count'],
                "tweet_retweet_count": tweet_content['retweet_count'],
                "tweet_created_at": datetime.strptime(tweet_content['created_at'], "%a %b %d %H:%M:%S %z %Y").isoformat(),
                "user_name": user_content['name'],
                "tweet_mention_list": json.dumps(
                    {mention['screen_name']: mention['name'] for mention in tweet_content['entities']['user_mentions']},
                    ensure_ascii=False
                ),
            }
        except (KeyError, ValueError) as e:
            logging.info(f"Error parsing tweet (parse_tweet): {e}")
            return None

    # Done
    def process_tweet_response(self, response_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process API response entries and extract tweets."""
        tweets = []
        for entry in response_entries:
            entry_id = entry.get('entryId', '')
            if "who-to-follow" in entry_id:
                continue  # Skip "who-to-follow" entries
    
            if 'profile-conversation' in entry['entryId']:
                parsed_tweet = self.parse_tweet(entry_id, entry['content']['items'][0]['item']['itemContent']['tweet_results']['result']) 
                 
            if "tweet" in entry['entryId']:
                # Extract tweet and user content
                parsed_tweet = self.parse_tweet(entry_id, entry['content']['itemContent']['tweet_results']['result'])
                if parsed_tweet:
                    tweets.append(parsed_tweet)
        return tweets
    
    def update_new_twitter_users(self, db: TweetDatabase):
        """Update the twitter_users table with new Twitter users."""
        try:
            logging.info("Updating new Twitter users...")    
            twitter_usernames = db.get_new_twitter_users_from_db()

            if twitter_usernames == []:
                logging.info("No new Twitter users to update.")
            else:
                for username in twitter_usernames:
                    logging.info(username[0])
                    self.get_user(username[0], db)
                    time.sleep(5)
            
        except KeyboardInterrupt:
            logging.info("Updating new Twitter users interrupted by user.")

    
    def scrape_tweets_periodically(self, db: TweetDatabase):
        """Periodically fetch the latest tweets for all Twitter users in the database and update the tweets table."""
        try:

            logging.info("Scraping tweets periodically...")
            user_ids = db.get_all_user_ids()
            for user_id in user_ids:
                latest_tweets = self.get_latest_tweets(user_id, 30)
                db.update_tweets(user_id, latest_tweets)
                logging.info(f"Updating tweets for user ID: {user_id}")
                time.sleep(5)



        except KeyboardInterrupt:
            logging.info("Tweet scraping interrupted by user.")



    def start(self, db: TweetDatabase):
        """
        Schedule periodic tasks for checking new tokens and missing source code.
        """
        logging.info("Starting the scheduler...")
        logging.info("Scheduler started. Running tasks...")

        # Schedule tasks
        schedule.every(1).minutes.do(lambda: self.update_new_twitter_users(db))
        schedule.every(5).minutes.do(lambda: self.scrape_tweets_periodically(db))

        # Run the scheduler loop
        while True:
            schedule.run_pending()
            time.sleep(1)  # Prevent busy-waiting

def main():
    # Set database path and API configurations
    twitter_scraper = TwitterScraper(get_tweet_url, get_user_url, auth, get_tweet_features, get_user_features, tweet_fieldToggles, user_fieldToggles)
    db = TweetDatabase(DB_PATH)
    twitter_scraper.start(db)


if __name__ == "__main__":
    main()
