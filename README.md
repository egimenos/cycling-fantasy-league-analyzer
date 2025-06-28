# ProCyclingStats Scraper

This project is a Python application designed to scrape UCI points and race data from `procyclingstats.com`. It is built following Domain-Driven Design (DDD) principles and Clean Code practices.

## Development Setup

These instructions will get you a copy of the project up and running on your local machine for development purposes.

### Prerequisites

- Python 3.8

### Installation

1.  **Clone the Repository**

    ```bash
    # git clone <repository_url>
    # cd procycling_scraper
    ```

2.  **Activate the Virtual Environment**

    This project uses a Python virtual environment to manage its dependencies. Activating it ensures that you are using the project-specific packages and not interfering with your global Python installation.

    From the project root directory, run:

    ```bash
    source .venv/bin/activate
    ```

    You will know the environment is active when your terminal prompt is prefixed with `(venv)`.

3.  **Install Dependencies**

    The required Python packages are listed in the `requirements.txt` file. Install them using `pip`:

    ```bash
    python3.8 -m pip install -r requirements.txt
    ```

    This command reads the `requirements.txt` file and installs the exact versions of the libraries needed for this project.

---
