# Project Info

**Objective**: The aim of this project is to build a FastAPI backend capable of handling heavy file uploads and secure storage. The implementation should provide a solid foundation that ensures smooth, efficient data retrieval and usage from the frontend.



## File route

#### POST /upload_file
File ingestion endpoint to upload csv files

#### GET /files
List all uploaded files by returnning their metadata from the database

#### GET /files/{file_id}/metadata
Retrieve the full metadata for a single file by its unique ID

#### GET /files/{file_id}/data
Retrieve and return the entire content of the stored file (the actual CSV data) by its unique ID




## Features

- ![Obstore](https://developmentseed.org/obstore/v0.2.0/) for storage, which is a high-throughput Python interface allows you to save any object to a persistent storage system such as Local,Amazon S3, Google Cloud Storage, Azure Storage.
   By default, the application relies on local storage; however, it can be configured to use an alternative storage option.
The default root directory for uploads is configured in the .env file (uploads) and will be created in the home directory, which translates to:;
   - `/home/<username>/uploads` (Linux) 
   -  `C:\Users\<username>\uploads` (Windows)
   -  `/Users/<username>/uploads` (Mac)

- Asynchronous code is employed to prevent blocking during file uploads, storage, reading, and streaming, and all database operations are handled asynchronously.

- Pagination is applied to limit the amount of data retrieved per request, ensuring manageable response sizes
- Docker Compose configuration is provided to simplify running the application locally

## Requirements:
 The code was tested on `Python 3.12.11`.
- ![FastAPI](https://fastapi.tiangolo.com/tutorial/)
- ![Postgres](https://www.postgresql.org/download/)
- ![Obstore](https://developmentseed.org/obstore/v0.2.0/)
- ![Pytest](https://docs.pytest.org/en/stable/)



# Setup and running instructions

## Manual approach
First clone this repo by using following command
````

git clone this repository 

````
then 
````

cd data-uploadt-fastapi

````

Then install the requirements

````

pip install -r requirements.txt

````


### Setup a postgres database on your computer and the environment variables 

Ensure that PostgreSQL is installed on your machine, either through a standard installation or by running it in a Docker container.

Create a database in postgres then create a file name `.env` and write the following things in you file 

````
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=<your_db_password>
DATABASE_NAME=<your_db_name>
DATABASE_USERNAME=<your_db_username>
UPLOAD_DIR = uploads
DEFAULT_STORE_TYPE=local
DATABASE_TEST_NAME=test_db

````
Then go to this repo folder in your local computer run follwoing command
````

uvicorn app.main:app --reload

````

Then you can use following link to use the  API

````

http://127.0.0.1:8000/docs 

````


## Docker approach:

![Docker desktop](https://docs.docker.com/desktop/) should be already installed.

You can setup the app entirely using docker compose, which spin up two containers:
- FastAPI app
- Postgres

To setup all, run:

````
docker compose up
````

To stop the container and remove the data volumes, run:
````
docker compose down -v
````

Then you can use following link to use the  API

````

http://127.0.0.1:8000/docs 

````

## Testing

Unit and integration tests are implemented using Pytest to ensure the reliability of all FastAPI endpoints.

To run all the tests, use:

````
pytest -v
````

## Further enhancement
- Implement file uploads using the TUS protocol for resumable uploads
- Optimize large file uploads
- Write tests
