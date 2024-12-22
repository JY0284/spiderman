# Data Collection and Notification System

A simple, modular system for collecting data from multiple sources, aggregating it, and sending notifications via email. The system is designed to be scalable and can start small, running on a local machine, and grow as your needs increase.

## Features

- **Multiple Collectors**: Fetch data from various sources (API, local files, sensors, etc.)
- **Task Scheduling**: Collect data at configurable intervals (hourly, daily, etc.)
- **Data Aggregation**: Aggregate data from multiple collectors into a single formatted report.
- **Email Notifications**: Send formatted data reports to users via email.
- **User Preferences**: Store user preferences in a local SQLite database.
- **Logging**: Track system operations and exceptions with comprehensive logging.

## Installation and Usage

### Install
```bash
pip install -e .
```

### Usage
```bash
python db/add_user.py name email # add a user
python scheduler/scheduler.py # start scheduler
