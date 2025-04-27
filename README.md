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

