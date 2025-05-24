# Devin Credit Usage Tracker

A web application that tracks and displays Devin's credit usage and limits by scraping the relevant data once a day.

## Features

- Automated scraping of Devin credit usage data from:
  - Main usage page: https://app.devin.ai/settings/usage (for Available ACUs)
  - History page: https://app.devin.ai/settings/usage?tab=history (for Session, Created At, and ACUs Used)
- Daily scheduled updates
- Web interface to view current and historical usage data
- Server-side login window for authentication
- Admin-only manual scrape functionality
- Public view for non-admin users

## Authentication

The Devin platform uses email confirmation codes for authentication instead of passwords. The application provides two ways to handle this:

### 1. Server-Side Login Window

The application now includes a two-step login process:
1. Enter your user ID (email address)
2. Enter the confirmation code sent to your email
3. Use these credentials for scraping

This approach allows you to:
- Manually trigger scrapes after logging in (admin only)
- View your credit usage data without modifying environment variables
- Maintain a session for the duration of your browser session

### 2. Environment Variables (Alternative)

You can still use environment variables for automated scraping:
1. Set `USER_ID` in your `.env` file
2. Update `DEVIN_CONFIRMATION_CODE` with the latest code before running the scraper

## Admin vs. Non-Admin Access

- **Non-Admin Users**: Can view all credit usage data without logging in
- **Admin Users**: Can log in and access additional features like manual scraping
- Admin status is configured via the `ADMIN_USER` setting in the `.env` file

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
     - `ORGANIZATION_NAME`: Your organization name (displayed in the UI)
     - `USER_ID`: Your Devin account email
     - `ADMIN_USER`: Set to "true" to enable admin features
     - `FLASK_SECRET_KEY`: A secure random key for session management

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
