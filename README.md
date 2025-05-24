# Devin Credit Usage Tracker

A web application that tracks and displays Devin's credit usage and limits by scraping the relevant data once a day.

## Features

- Automated scraping of Devin credit usage data from:
  - Main usage page: https://app.devin.ai/settings/usage (for Available ACUs)
  - History page: https://app.devin.ai/settings/usage?tab=history (for Session, Created At, and ACUs Used)
- Daily scheduled updates
- Web interface to view current and historical usage data

## Authentication Note

The Devin platform uses email confirmation codes for authentication instead of passwords. This means:

1. The scraper will submit your email address to the login form
2. Devin will send a confirmation code to that email
3. You need to provide this confirmation code to the scraper via the `DEVIN_CONFIRMATION_CODE` environment variable

**Important Limitation**: Since the confirmation codes are temporary and sent to email, fully automated scraping requires additional integration with an email API to retrieve the codes automatically. The current implementation requires manually updating the confirmation code in the `.env` file before each scraping run.

### Potential Solutions for Automation

1. **Email API Integration**: Implement an integration with an email service API to automatically retrieve confirmation codes
2. **Scheduled Manual Updates**: Run the scraper manually once a day after receiving the confirmation code
3. **Extended Session Cookies**: Store and reuse session cookies if they remain valid for extended periods

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
   - Update the configuration values in `.env`, including:
     - `DEVIN_USERNAME`: Your Devin account email
     - `DEVIN_CONFIRMATION_CODE`: The confirmation code sent to your email (needs to be updated before each run)

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
