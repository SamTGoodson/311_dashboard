import pandas as pd
import logging
from pathlib import Path

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("transform")

COMPLAINT_DAILY_PATH = "data/_complaint_type_daily.csv"
GEO_DAILY_PATH = 'data/_community_board_daily.csv'


def load_data(path):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

def load_sheet(data):
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df

def check_date(daily_df,history_df):
    history_last_date = history_df['date'].max()
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=31)
    daily_date = daily_df['date'].max()

    if daily_date > history_last_date:
        logger.info("Appended %d rows", len(daily_df))
        return daily_df, True
        
    else:
        return None, False
    
    
def main():

    bor_daily = load_data(COMPLAINT_DAILY_PATH)
    cb_daily = load_data(GEO_DAILY_PATH)

    sh = client.open('311 Data')
    BOROUGH_SHEET = sh.worksheet("Sheet2")
    BOROUGH_DATA = BOROUGH_SHEET.get_all_records()

    CB_SHEET= sh.worksheet('Sheet1')
    CB_DATA = CB_SHEET.get_all_records()


    bor_history = load_sheet(BOROUGH_DATA)
    updated_bor_history, was_appended = check_date(bor_daily,bor_history)
    if was_appended:
        updated_bor_history["date"] = updated_bor_history["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        BOROUGH_SHEET.append_rows(updated_bor_history.values.tolist(), value_input_option="USER_ENTERED")
    else:
        logger.info('No Borough level data to write')
        

    cb_history = load_sheet(CB_DATA)
    updated_cb_history, was_appended = check_date(cb_daily,cb_history)
    if was_appended:
        updated_cb_history["date"] = updated_cb_history["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        CB_SHEET.append_rows(updated_cb_history.values.tolist(), value_input_option="USER_ENTERED")
    else:
        logger.info('No CB level data to write')

    


if __name__ == "__main__":
    main()