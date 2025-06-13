# neo-ai

A project for sentiment analysis and generative AI-based voice applications using FastAPI.

---

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)

---

## Introduction

**neo-ai** is a GenAI application built with [FastAPI](https://fastapi.tiangolo.com/). It provides APIs for sentiment analysis and voice-based interactions using advanced machine learning models.

---

## Project Structure

neo-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                   # Entry point of the FastAPI application
│   ├── config/
│   │   ├── __init__.py
│   │   └── routes.py  
│   ├── services/sesame_voice_model
│   │   ├── csm_voice_trainer.py
│   │   └── voicechat.py   
│   ├── static/
│   │   └── voice_chat.html
├── dependencies.sh
├── requirements.txt
├── docker-compose.yml
├── environment.list
├── Dockerfile
├── Makefile
└── README.md


---

## Installation

### Prerequisites

- [Python 3.12](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [Docker](https://docs.docker.com/get-docker/) (optional, for containerization)
- [Virtual Environment (venv)](https://docs.python.org/3/library/venv.html)

### Clone the Repository

```bash
git clone https://github.com/your-org/neo-ai.git
cd neo-ai



Set Up a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.
python3 -m venv venv
source venv/bin/activate  # On Windows use 'venv\Scripts\activate'


pip install -r requirements.txt


Usage
Running the Application Locally
After activating the virtual environment and installing dependencies, you can run the application:
uvicorn app.main:app --reload --port 9000