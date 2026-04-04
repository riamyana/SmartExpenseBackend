# SmartExpenseBackend

# Specific python version used for this project
- 3.12.7

# Add virtual environment to add dependencies to the required python environemnt.
In VS Code:
- Press Cntrl+Shift+P
- Select: Python: Select Interpreter
    - Select Python version (If not shown in the specific python version then add the path)
- Select: Create Virtual Environment
    - Select Venv
    - Select Interpreter Path

# Install python dependencies
- pip install -r requirements.txt

# To run FastApi (in /src path):
- uvicorn app:main:app

# To view docs of api
- http://127.0.0.1:8000/docs