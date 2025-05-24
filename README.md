# Devin Credit Usage Tracker

A web application that tracks and displays Devin's credit usage and limits by scraping the relevant data once a day.

## Features

- Automated scraping of Devin credit usage data
- Daily scheduled updates
- Web interface to view current and historical usage data

## Setup

### Prerequisites

- Python 3.8+
- Chrome browser (for Selenium WebDriver)
- ChromeDriver

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/codeforjapan/devinwork.git
   cd devinwork
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure the application:
   - Copy `.env.example` to `.env`
   - Update the configuration values in `.env`

### Running the Application

1. Start the web server:
   ```
   python src/web/app.py
   ```

2. Access the web interface at `http://localhost:5000`

3. To manually run the scraper:
   ```
   python src/scraper/run.py
   ```

## Project Structure

- `src/scraper/`: Contains the web scraping code
- `src/web/`: Contains the web server code
- `static/`: Static assets for the web interface
- `templates/`: HTML templates for the web interface
- `data/`: Storage for scraped data

## License

[MIT License](LICENSE)
