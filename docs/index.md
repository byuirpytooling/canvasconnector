![Canvas Connector](assets/banner.png)

# Canvas Connector

A Python package for easily connecting to the Canvas LMS API.

## Features

- Easy authentication with Canvas API
- Fetch courses, assignments, and grades (WIP)
- Get peer information
- Track upcoming assignments
- Built with Polars for fast data processing

## Quick Start

```python
from canvasconnector import CanvasClient, get_courses_polars
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create client
client = CanvasClient(
    canvas_url="https://byui.instructure.com",
    api_token=os.getenv("CANVAS_API_TOKEN"),
    timezone="America/Denver"  # Optional: defaults to UTC. Necesarry for the upcomming assignment function.
)

# Get your courses
courses = get_courses_polars(client)
print(courses)
```

## Installation

### Using uv (recommended)

```bash
uv pip install git+https://github.com/byuirpytooling/canvasconnector.git
```

### Using pip

```bash
pip install git+https://github.com/byuirpytooling/canvasconnector.git
```

### For development (contributing)

```bash
# Fork the repository on GitHub first, then clone your fork
git clone https://github.com/YOUR-USERNAME/canvasconnector.git
cd canvasconnector

# Create a virtual environment and install
uv venv
uv sync

# Make your changes, then push to your fork and create a PR
```
