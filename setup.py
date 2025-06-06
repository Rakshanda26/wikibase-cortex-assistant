from setuptools import setup, find_packages

setup(
    name="wikibase-cortex-assistant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.95.0",
        "uvicorn==0.22.0",
        "snowflake-connector-python==2.7.6",
        "snowflake-sqlalchemy==1.3.4",
        "python-dotenv==0.21.1",
        "pydantic==1.10.2",
        "wikipedia",
        "langchain",
        "duckduckgo-search"
    ],
)
