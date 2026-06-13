[project]
name = "returniq"
version = "0.1.0"
description = "Intelligent returns disposition engine — Amazon HackOn Season 6"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.3.0",
    "dependency-injector>=4.41.0",
    "boto3>=1.34.0",
    "boto3-stubs[s3,dynamodb,rekognition,bedrock-runtime,sagemaker-runtime,sns,stepfunctions,sqs]>=1.34.0",
    "qrcode[pil]>=7.4.2",
    "structlog>=24.2.0",
    "python-ulid>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "httpx>=0.27.0",
    "moto[s3,dynamodb,sns,sqs]>=5.0.0",
    "mypy>=1.10.0",
    "ruff>=0.4.0",
    "factory-boy>=3.3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=app --cov-report=term-missing --cov-fail-under=85"

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E","W","F","I","N","UP","B","A","C4","DTZ","RET","SIM","TCH","ARG","PTH","PL","RUF"]
ignore = ["PLR0913","PLR2004"]

[tool.ruff.lint.isort]
known-first-party = ["app"]

[tool.coverage.run]
source = ["app"]
omit = ["app/main.py","app/container.py"]