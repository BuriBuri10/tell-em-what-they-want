import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s')

BASE_DIR = Path(__file__).resolve().parent

folders_and_files = {
    "api": ["main.py"],
    "api/routes": ["__init__.py", "user.py", "campaign.py", "analytics.py"],

    "configs": ["__init__.py", "app_config.py"],

    "core": [
        "__init__.py", "llm_manager.py", "chain.py", "prompt_templates.py",
        "segmentation_engine.py", "recommendation_engine.py", "ad_generator.py"
    ],
    "core/utils": ["campaign_recs.py"],

    "data_preprocessing_pipeline": [
        "__init__.py", "user_data_analyzer.py", "data_cleaner.py", "utils.py"
    ],

    "models": [
        "__init__.py", "campaign_model.py", "user_profile_model.py", "ad_model.py"
    ],

    "services": [
        "__init__.py", "human_in_the_loop.py",
        "user_service.py", "campaign_service.py"
    ],

    "services/analytics": ["metrics_collector.py"],

    "workflows": ["state.py", "workflow.py"],

    "workflows/graphs/campaign": ["__init__.py"],

    "workflows/graphs/campaign/nodes": [
        "__init__.py", "check_external_logs_node.py",
        "segmenting_node.py", "analytics_node.py",
        "generate_ad_node.py", "recommend_node.py",
        "human_in_the_loop_node.py", 
        "feedback_loop_node.py"
    ],

    "workflows/graphs/campaign/subgraphs": [
        "persona_subgraph.py", "strategy_subgraph.py"
    ],

    "workflows/graphs/campaign/prompts": ["segment_prompt.py", "ad_prompt.py", "recommendation_prompt.py", "human_in_the_loop_prompt.py"],

    "tests": ["test_user.py", "test_campaign.py", "test_llm_integration.py"],

    "logs": ["__init__.py", "logging_config.py", "app.log"]
}

base_files = [".env", ".env.example", "requirements.txt"]

# Generate folders and files
for folder, files in folders_and_files.items():
    for file in files:
        path = BASE_DIR / folder / file
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()
            logging.info(f"Created file: {path}")
        else:
            logging.info(f"File already exists: {path}")

# Create base files
for file in base_files:
    path = BASE_DIR / file
    if not path.exists():
        path.touch()
        logging.info(f"Created base file: {file}")
    else:
        logging.info(f"Base file already exists: {file}")

# Dockerfile
dockerfile_content = """\
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

dockerfile_path = BASE_DIR / "Dockerfile"
if not dockerfile_path.exists():
    dockerfile_path.write_text(dockerfile_content)
    logging.info("Created Dockerfile")
else:
    logging.info("Dockerfile already exists")

# .dockerignore
dockerignore_content = """\
__pycache__/
*.pyc
*.pyo
*.pyd
.env
*.db
*.sqlite3
*.log
outputs/
"""

dockerignore_path = BASE_DIR / ".dockerignore"
if not dockerignore_path.exists():
    dockerignore_path.write_text(dockerignore_content)
    logging.info("Created .dockerignore")
else:
    logging.info(".dockerignore already exists")

# docker-compose.yml
docker_compose_content = """\
version: "3.8"

services:
  ai-marketing-platform:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
"""

docker_compose_path = BASE_DIR / "docker-compose.yml"
if not docker_compose_path.exists():
    docker_compose_path.write_text(docker_compose_content)
    logging.info("Created docker-compose.yml")
else:
    logging.info("docker-compose.yml already exists")
