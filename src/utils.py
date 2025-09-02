from sqlalchemy import create_engine

import pandas as pd

def save_data_to_db(data, table_name, db_path, search_category=None):
    """
    Save the data to a specified table in an SQLite database.
    :param data: Raw data that is to be saved.
    :param table_name: Name of the table to create/replace.
    :param db_path: Path to the SQLite database.
    :param search_category: Name of the searched job role.
    """
    df = pd.DataFrame(data)
    if df.empty:
        print("DataFrame is empty. Nothing to save.")
        return
    if search_category is not None:
        df['search_category'] = search_category
    try:
        engine = create_engine(f'sqlite:///{db_path}')
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False,
        )
        print(f"Successfully wrote {len(df)} records to the '{table_name}' table in {db_path}.")
    except Exception as e:
        print(f"An error occurred while saving to the database: {e}")

def deduplicate_table(table_name, db_path):
    """
    Reads a table, removes duplicate rows based on the 'url' column,
    and overwrites the table with the clean data.
    :param table_name: Name of the table to create/replace.
    :param db_path: Path to the SQLite database.
    """
    try:
        engine = create_engine(f'sqlite:///{db_path}')
        df = pd.read_sql_table(table_name, engine)
        print(f"Loaded {len(df)} rows from '{table_name}' (with duplicates).")
        df_clean = df.drop_duplicates(subset=['full_description'], keep='first')
        print(f"Removed {len(df) - len(df_clean)} duplicate rows.")
        print(f"New row count: {len(df_clean)}.")
        print(f"Overwriting '{table_name}' with de-duplicated data...")
        df_clean.to_sql(
            table_name,
            con=engine,
            if_exists='replace',
            index=False
        )
        print("De-duplication complete.")
    except Exception as e:
        print(f"An error occurred: {e}")


