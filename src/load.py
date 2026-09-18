import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("transform")

COMPLAINT_DAILY_PATH = "data/_complaint_type_daily.csv"
GEO_DAILY_PATH = 'data/_community_board_daily.csv'

COMPLAINT_HISTORY_PATH = "data/complaint_type_history.csv"
GEO_HISTORY_PATH = "data/community_board_history.csv"


def load_data(path):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

def check_date(daily_df,history_df):
    history_last_date = history_df['date'].max()
    daily_date = daily_df['date'].max()

    if daily_date > history_last_date:
        history_df = pd.concat([history_df,daily_df])
        logger.info("Appended %d rows", len(daily_df))
        return history_df, True
        
    else:
        return None, False
    
    
def main():

    type_daily = load_data(COMPLAINT_DAILY_PATH)
    geo_daily = load_data(GEO_DAILY_PATH)

    if Path(COMPLAINT_HISTORY_PATH).exists():
        type_history = load_data(COMPLAINT_HISTORY_PATH)
        updated_type_history, was_appended = check_date(type_daily,type_history)
        if was_appended:
            updated_type_history.to_csv(COMPLAINT_HISTORY_PATH,index=False)
        else:
            logger.info('No Borough level data to write')
        
    else:
        type_daily.to_csv(COMPLAINT_HISTORY_PATH, index=False)
        logger.info('No previous historical data, started fresh')

    if Path(GEO_HISTORY_PATH).exists():
        geo_history = load_data(GEO_HISTORY_PATH)
        updated_geo_history, was_appended = check_date(geo_daily,geo_history)
        if was_appended:
            updated_geo_history.to_csv(GEO_HISTORY_PATH,index=False)
        else:
            logger.info('No CB level data to write')

    else:
        geo_daily.to_csv(GEO_HISTORY_PATH, index=False)
        logger.info('No previous historical data, started fresh')
    


if __name__ == "__main__":
    main()