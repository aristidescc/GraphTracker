# GraphTracker App

## Overview

Minimalist backend and integrated frontend Flask web application to manage a navigation graph and a way to visit and travel through this graph structure, with a log over every operation.

This will be used as part of the LLM Navigation Agent experiment I'm running.

## How to Run

- Clone the repository:
```bash
git clone https://github.com/aristidescc/GraphTracker.git
```

- Navigate to the project directory:
```bash
cd GraphTracker
```

- Create a virtual environment (optional but recommended):
```bash 
python -m venv venv
```

- Activate the virtual environment:
  - On Windows:
  ```bash
  venv\Scripts\activate
  ```
  - On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- Install the required packages:
```bash
pip install -r requirements.txt
```
- Seed the SQLLite DB with the initial data:
```bash
python src/seed_db.py
```

- Run the Flask application:
```bash
python src/integrated_app.py
```
Go to http://localhost:5001 in your web browser to access the application.

## Test and execute API endpoints

This application includes Bruno's API collection to test the API endpoints. First make sure you have Bruno installed:

- [Bruno download page](https://www.usebruno.com/downloads)

Execute bruno and open <project_root>/api-test/GraphTrackerAPI/bruno.json to load the API collection.

