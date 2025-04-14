# Dublin Bikes Project

## Features
- Real-time bike station tracking
- Real-time Weather 
- Predictive bike availability model 
- Interactive web interface
- User Authentication

## Tech Stack
- Frontend: HTML/CSS/JavaScript
- Backend: Flask (Python)
- ML: Scikit-learn, Random Forest Regression
- Database: MySQL
- APIs: JCDecaux, OpenWeather, Google Maps

## Setup Instructions
1. Clone the repository
2. Install dependencies
    - Ensure you have Python 3.8+ and pip installed
    -  Install dependencies:
        `pip install -r requirements.txt`
3. Configuration: 
    - Copy `example.env` to `.env`
    - Edit `.env` with your own API keys and database credentials
4. Run the application: `python app.py`

## Contributors
- Jin, Xiaoxia
- He, Zhaofang
- Makkena, Bala Anush Choudhary

## Project Structure
Below is the structure of the project detailing the directories and files contained within:
```
Dublin-Bikes/
├── machine_learning/
│   ├── cleaned_historical_weather_data.csv
│   ├── historical_bike_data_cleaning.ipynb
│   ├── ml_training.ipynb
│   └── station_models/
│       └── station_1.pkl
│       └──   ……
│       └── station_117.pkl
│
├── website/
│   ├── templates/
│   │   ├── 404.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── sign-up.html
│   │   ├── station.html
│   │   └── use.html
│   ├── config.py
│   ├── database_connector.py
│   ├── login_routes.py
│   ├── scraper_dublin_bike.py
│   ├── scraper_weather.py
│   ├── stations_routes.py
│   └── weather_routes.py
│
├── test/
│   ├── test_all_predict_models.py
│   ├── test_integration.py
│   ├── test_login.py
│   ├── test_scrapers.py
│   ├── test_station_api.py
│   └── test_station_routes.py
│
│
├── app.py # Main application entry point
├── example.env # Environment configuration template
├── LICENSE # Project license
├── README.md # Project documentation
└── requirements.txt # Python dependencies
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
