# youtube_data_etl

## Description

This code snippet is a Python script that retrieves data from the YouTube Data API, stores it in a MongoDB database, converts the data to MySQL format, and performs various queries on the data stored in the MySQL database. It also includes a Streamlit application for interactive data retrieval and query execution.

The script first sets up connections to MongoDB and MySQL databases. It then prompts the user to enter a YouTube Channel ID. Upon clicking the "Retrieve and Store Data" button, the script makes API calls to retrieve channel statistics, video details, and comments from the specified YouTube channel. The retrieved data is stored in separate collections in the MongoDB database.

The script also provides functionality to convert the data stored in MongoDB to MySQL format. Upon clicking the "Convert to MySQL" button, the script fetches the documents from MongoDB collections, converts them to pandas DataFrames, and inserts them into corresponding tables in the MySQL database using SQLAlchemy. Predefined queries are executed on the MySQL data, and the results are displayed in a Streamlit application.

This code can be used as a starting point for building a YouTube data retrieval and analysis project. It demonstrates how to interact with the YouTube Data API, store data in databases, convert data between different database systems, and perform queries on the data.

## Installation

To run the script, you need to install the following packages:

- google-api-python-client
- pymongo
- streamlit
- pandas
- mysql-connector-python
- sqlalchemy

You can install these packages using pip:


## Set up MongoDB Connection

Before running the script, make sure you have MongoDB installed and running on your system. You also need to set up a MongoDB connection string. Modify the `MONGO_CONNECTION_STRING` variable in the script to match your MongoDB configuration.

## Set up MySQL Connection

Ensure that you have MySQL installed and running on your system. Modify the `host`, `user`, `password`, and `database` variables in the script to match your MySQL connection details.

## Usage

To use the script, follow these steps:

1. Run the script using Python.(IDE with .py files are recommended)
2. The script will launch a Streamlit application in your browser.
3. In the YouTube Data Retrieval section, enter the Channel ID for which you want to retrieve data.
4. Click the "Retrieve and Store Data" button to retrieve the data from the YouTube Data API and store it in the MongoDB database.
5. Once the data retrieval is complete, click the "Convert to MySQL" button to convert the data from MongoDB to MySQL format and execute predefined queries on the data.
6. The Streamlit application will display the results of the queries.

## Workflow Overview

1. The script connects to MongoDB and MySQL databases.
2. It retrieves channel statistics, video details, and comments from the YouTube Data API using the provided Channel ID.
3. The retrieved data is stored in separate collections in the MongoDB database.
4. The data stored in MongoDB is converted to MySQL format using pandas DataFrames and SQLAlchemy.
5. Predefined queries are executed on the MySQL data, and the results are displayed in the Streamlit application.

## Capabilities

- Retrieve and store YouTube channel statistics, video details, and comments in a MongoDB database.
- Convert the data stored in MongoDB to MySQL format.
- Execute predefined queries on the MySQL data and display the results.
- It can retrieve and strore multiple YouTube channel statistics, video details, and comments one at a time as long as its within quotas and limitations of the YouTube Data API.

## Limitations

- The script relies on the YouTube Data API and its quotas and limitations.
- The script assumes a single channel ID input for data retrieval and conversion.
- Error handling and validation for input values are minimal.
