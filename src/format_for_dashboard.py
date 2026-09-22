import pandas as pd

BOROUGH_TYPE = "data/complaint_type_history.csv"
CB_TYPE = "data/community_board_history.csv"


borough_codes = {
    "MANHATTAN": 1,
    "BRONX": 2,
    "BROOKLYN": 3,
    "QUEENS": 4,
    "STATEN ISLAND": 5,
}


def load_data(filepath):
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    return df

def rolling_avg(filepath,col):
    df = load_data(filepath)
    
    df = df.sort_values(
    [col, "complaint_type", "date"]
    ).reset_index(drop=True)

    df['rolling_avg'] = df.groupby([col, "complaint_type"])['count'].transform(
        lambda x: x.rolling(window=2, min_periods=1).mean()
    )


    return df

def format_cb(df,borough_codes):
    df = df[~df['community_board'].str.contains('Unspecified', na=False)]
    df["board_num"] = pd.to_numeric(
    df["community_board"].str.extract(r"(\d+)")[0],
    errors="coerce"
    )

    df["borough"] = (
        df["community_board"]
        .str.extract(r"([A-Z ]+)$")[0]
        .str.strip()
    )

    df["borough_code"] = df["borough"].map(borough_codes)

    df["BoroCD"] = (
        df["borough_code"] * 100
        + df["board_num"]
    )

    return df

def main():
    borough_df = rolling_avg(BOROUGH_TYPE,'borough')
    cb_df = rolling_avg(CB_TYPE,'community_board')
    formatted_cb_df = format_cb(cb_df,borough_codes)

    formatted_cb_df.to_csv('data/cb_df.csv',index=False)
    borough_df.to_csv('data/borough_df.csv',index = False)

if __name__ == "__main__":
    main()