from setuptools import setup, find_packages

setup(
    name="pscyAgent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "openai",
        "pydantic",
        "pydantic-settings",
        "sqlalchemy",
        "aiofiles",
    ]
)