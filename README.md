## 311 Dashboard 

This gets updates on 311 complaints from NYC Open Data and then visualizes them by community board and borough. The dashboard is a dash app that is not hosted anywhere at the moment, so if you'd like to use it clone the repository and run the app locally. Data refreshes daily via a scheduled GitHub Actions workflow.

## Setup

```
git clone https://github.com/SamTGoodson/311_dashboard.git
cd 311_dashboard
```

This project uses two requirements files:
- `requirements.txt` — cross-platform dependencies needed to run the pipeline and app (used by GitHub Actions)
- `dev-requirements.txt` — additional Windows-specific packages for local development

To run the full pipeline locally on Windows:
​```
pip install -r requirements.txt -r dev-requirements.txt
​```

To run just the app, or to replicate the CI environment:
​```
pip install -r requirements.txt
​```
If you want to run the whole thing you'll also need API credentials from NYC Open Data, locally you can put them into a .env file which will load automatically in fetch_data.py.

Add a `.env` file with:
```
NYC_API_TOKEN=your_key_here
NYC_USERNAME=your_username
NYC_PASSWORD=your_password
```



## Run the app 

```
# In the directory root
python app.py
```