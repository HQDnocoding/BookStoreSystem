# Python Flask Tutorial

Flask is a lightweight and flexible Python web framework, perfect for beginners looking to build small websites or learn web development with Python.

## Prerequisites

Before getting started, ensure you have the following installed:

- **Python 3.7+**: Download from [python.org](https://www.python.org/downloads/).
- **pip**: Python’s package manager (usually included with Python).
- A terminal or command-line interface (e.g., Command Prompt, PowerShell, or Bash).

---

## Installation

Follow these steps to set up Flask and Flask-Security in your project.

### 1. Create a Virtual Environment

A virtual environment keeps your project dependencies isolated.

```bash
python -m venv .venv
```

Activate it:

- **Windows**: `.venv\Scripts\activate`
- **MacOS/Linux**: `source .venv/bin/activate`

You’ll see `(.venv)` in your terminal when it’s active.

### 2. Install Flask - Database Library

Use pip to install Flask:

```bash
pip install flask flask-sqlalchemy
```

---

## Usage

### 1. Configure Flask Environment Variables

Set up environment variables to run your app:

- **Windows**:

  ```bash
  set FLASK_APP=run.py
  set FLASK_DEBUG=1
  ```

- **MacOS/Linux**:

  ```bash
  export FLASK_APP=run.py
  export FLASK_DEBUG=1
  ```

- `FLASK_APP`: Specifies the entry point of your app.
- `FLASK_DEBUG=1`: Enables debug mode for live reloading and error details.

### 2. Run the Application

Start the Flask development server:

```bash
python -m flask run
```

OR

```bash
python run.py
```

Visit `http://127.0.0.1:5000/` in your browser to see "Hello, Flask with Security!".

### 3. Explore Flask in the Python Interpreter

To experiment with Flask interactively:

```bash
python
>>> import flask
>>> flask.__version__  # Check the installed version
>>> exit()
```

---

## Managing Dependencies

To share your project or deploy it, use a `requirements.txt` file.

### 1. Generate `requirements.txt`

After installing all packages, run:

```bash
pip freeze > requirements.txt
```

This creates a file listing all installed packages and their versions.

### 2. Install Dependencies from `requirements.txt`

For someone else (or on a new machine):

```bash
pip install -r requirements.txt
```
