import sqlite3


class DatabaseManager:
    def __init__(self, db_path):
        """
        Initialize the DatabaseManager with a path to the SQLite database.
        """
        self.db_path = db_path
        
    def execute_query(self, query, parameters=None):
        """
        Execute a given SQL query (e.g., DROP TABLE or DELETE FROM).

        Parameters:
            query (str): The SQL query to execute.
            parameters (tuple): Optional parameters for parameterized queries.
        """
        try:
            # Connect to the database
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                # Execute the query with parameters if provided
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def drop_table(self, table_name):
        """
        Drop a table from the database.

        Parameters:
            table_name (str): The name of the table to drop.
        """
        self.execute_query(f"DROP TABLE IF EXISTS {table_name}")
        print(f"Table '{table_name}' dropped (if it existed).")

    def delete_records(self, table_name):
        """
        Delete all records from a table.

        Parameters:
            table_name (str): The name of the table from which to delete all records.
        """
        self.execute_query(f"DELETE FROM {table_name}")
        print(f"All records deleted from table '{table_name}'.")

    def create_table(self, table_name, schema):
        """
        Create a table with the given schema.

        Parameters:
            table_name (str): The name of the table to create.
            schema (str): The schema definition for the table.
        """
        self.execute_query(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
        print(f"Table '{table_name}' created.")

    def create_tokens_table(self):
        """
        Create the 'tokens' table.
        """
        schema = """
            ContractAddress TEXT PRIMARY KEY,   -- Unique identifier for the token
            pairAddress TEXT NOT NULL,            -- Address of the token pair
            Owner TEXT NOT NULL,                 -- Owner of the token contract
            TokenName TEXT NOT NULL,            -- Name of the token
            Symbol TEXT NOT NULL,               -- Symbol of the token (e.g., ETH, BTC)
            TotalSupply INTEGER NOT NULL,       -- Total supply of the token
            Decimal INTEGER NOT NULL,           -- Number of decimals for the token
            CreatedBlock INTEGER NOT NULL,      -- Block number when the token was created
            TwitterUrl TEXT,
            TwitterUser TEXT,
            WebsiteUrl TEXT,
            TelegramUrl TEXT,
            WhitepaperUrl TEXT,
            isSpam TEXT,                  -- Indicates if the token is spam
            isPotentialSpam TEXT,         -- Indicates if the token is potentially spam
            safetyLevel TEXT,             -- Safety level of the token
            spamCode INT,                -- Code indicating the type of spam
            attackTypes TEXT,             -- Types of attacks associated with the token
            is_open_source TEXT,         -- Indicates if the token is open source
            is_honeypot TEXT,          -- Indicates if the token is a honeypot
            ismintable TEXT,          -- Indicates if the token is mintable
            is proxy TEXT,          -- Indicates if the token is a proxy
            slippage_modifiable TEXT,          -- Indicates if the token is slippage modifiable
            is_blacklisted TEXT,          -- Indicates if the token is blacklisted
            min_sell_tax FLOAT,          -- Minimum sell tax for the token
            max_sell_tax FLOAT,          -- Maximum sell tax for the token
            min_buy_tax FLOAT,           -- Minimum buy tax for the token
            max_buy_tax FLOAT,           -- Maximum buy tax for the token
            is_contract_renounced TEXT,          -- Indicates if the contract is renounced
            is_potentially_scam TEXT,          -- Indicates if the token is potentially a scam
            transfer_pausable TEXT,          -- Indicates if the token is transfer pausable
            warning TEXT,          -- Warning message associated with the token
            FetchedAt TEXT                      -- Timestamp of when the contract data was fetched
        """
        self.create_table("tokens", schema)

    def create_contracts_table(self):
        """
        Create the 'contracts' table.
        """
        schema = """
            ContractAddress TEXT PRIMARY KEY,
            SourceCode TEXT,
            CompilerVersion TEXT,
            OptimizationUsed TEXT,
            Runs TEXT,
            EVMVersion TEXT,
            Library TEXT,
            LicenseType TEXT,
            Proxy TEXT,
            Implementation TEXT, 
            SwarmSource TEXT,
            FetchedAt TEXT                      -- Timestamp of when the contract data was fetched
        """
        self.create_table("contracts", schema)

    def create_tweets_table(self):
        """
        Create the 'tweets' table.
        """
        schema = """
            user_id TEXT NOT NULL,
            tweet_id TEXT PRIMARY KEY,
            tweet_full_text TEXT,
            tweet_favorite_count INTEGER,
            tweet_view_count INTEGER,
            tweet_quote_count INTEGER,
            tweet_reply_count INTEGER,
            tweet_retweet_count INTEGER,
            tweet_created_at TEXT,
            user_name TEXT,
            tweet_mention_list TEXT
        """
        self.create_table("tweets", schema)

    def create_twitter_users_table(self):
        """
        Create the 'twitter_users' table.
        """
        schema = '''
                user_id INTEGER ,   
                username TEXT PRIMARY KEY,         
                description TEXT,                
                created_time TEXT, 
                available TEXT
                
            '''
        self.create_table("twitter_users", schema)

    def add_column_to_table(self, table_name, column_name, column_type):
        """
        Add a new column to an existing table.

        Parameters:
            table_name (str): The name of the table to modify.
            column_name (str): The name of the new column to add.
            column_type (str): The data type of the new column.
        """
        self.execute_query(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"Column '{column_name}' added to table '{table_name}'.")