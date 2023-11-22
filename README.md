# Atlas Vector Search with Full-Text Search boosting

# Atlas Vector Search on Wikipedia Articles
This demo will show how to perform semantic search on Wikipedia articles of different languages. It also gives you the ability to use full-text search capabilities to boose the relevancy scores of the results based on keyword matches.

```json
{
    "language": "english",
    "title": "Lake Andes, South Dakota",
    "text": "Lake Andes is a city in, and the county seat of, Charles Mix County, South Dakota, United States. The population was 710 at the 2020 census...",
    "url" : "https://en.wikipedia.org/wiki/Lake%20Andes%2C%20South%20Dakota"
}
```

# Prerequisites

- MongoDB Atlas Cluster with the M10+ tier in your preferred region
- Execution was successful with the following dependencies
  - Check the steps in the section [link][# Steps to Install and Test]
  - Python 3.9.2 along with pip
    - Following libraries will be required
      - Flask==2.1.0
      - Pillow==9.3.0
      - pymongo==4.1.1
      - sentence_transformers==2.2.2
    - `requirements.txt` includes all the dependencies and if you want to install dependencies in one shot:
      ```bash
      pip install -r requirements.txt
      ```



# Steps to Install and Test

## Configure database connection 

Modify the `config/config_database.py` file accordingly with the database connection string, database and collection information. 

## Create the Search and Vector Search Indexes

Create the following search indexes on the collection that you configured in the config file:

Default:
```json
{
  "mappings": {
    "fields": {
      "language": {
        "normalizer": "lowercase",
        "type": "token"
      },
      "vector": [
        {
          "dimensions": 384,
          "similarity": "cosine",
          "type": "knnVector"
        }
      ]
    }
  }
}
```

textSearch:
```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "language": {
        "type": "string"
      },
      "text": {
        "type": "string"
      }
    }
  },
  "storedSource": true
}
```

## Run Encoding and Store the Vector in the database

5000 Wikipedia articles have already been downloaded and added to the `data/` folder, so switch to that folder. We will run encoding on the application side and store the vector inside the database. 

`wikipedia_tiny.json` is meant to be used with [`mongoimport`](https://www.mongodb.com/docs/database-tools/mongoimport/) or Compass to import data, whereas `wikipedia_tiny.gz` is the same file but compressed to make it easier to transfer around. This file contains 5,000 total records of cleaned wikipedia pages in English, French, German, Italian, and Frisian. 

To import `wikipedia_tiny.json` into a cluster using a database user authenticating with SCRAM (i.e. user & password), please use [`mongoimport`](https://www.mongodb.com/docs/database-tools/mongoimport/) like this:
```bash
mongoimport 'mongodb+srv://<username>:<password>@<clustername>.<atlasProjectHash>.mongodb.net/' --file='wikipedia_tiny.json'
```
To accomplish this using the Compass GUI, [follow this guide](https://www.mongodb.com/docs/compass/current/import-export/#import-data-into-a-collection).

To import `wikipedia_tiny.gz` into a cluster using a databse user authenticating with SCRAM (i.e. username & password), please use [mongorestore](https://www.mongodb.com/docs/database-tools/mongorestore/) like this:
```bash
mongorestore 'mongodb+srv://<username>:<password>@<clustername>.<atlasProjectHash>.mongodb.net' --archive='wikipedia_tiny.gz' --gzip
```

# Vectorize Query

1. Set up your python environment (if not done already):

```
python3 -m venv .ENV
```

```
source .ENV/bin/activate
```

```
pip install -r requirements.txt
```

2. Open a terminal session where you activated your ENV. 

3. Start python interpreter: ```python3```

4. Import HuggingFace transformers library: ```from sentence_transformers import SentenceTransformer```

5. Get handle on the ```all-MiniLM-L6-v2``` model: ```encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')```

6. Encode query text into vector representation: ```encoder.encode(<yourquery>).tolist()```

# Get your own clean wikipedia dataset

All code is contained within `main.py` and requirements within `requirements.txt`. The latter was produced using `pip freeze > requirements.txt`. All configuration for `main.py` is located immediately within the `main()` function near the top of the file, with comments indicated what to change. **The main requirement is to replace the `mongo_uri` variable with your [cluster's connection string](https://www.mongodb.com/docs/guides/atlas/connection-string/).**

The defaults of `main.py` are:
    - Indexing all of the clean, English language wikipedia dataset from [HuggingFace](https://huggingface.co/datasets/wikipedia). This amounts to **~16.18GB of raw data**. The python file also includes options to index by a given max bytes or max record count. Other languages are available, just visit the HuggingFace dataset link.
    - The `all-MiniLM-L6-v2` embedding model is used to vectorize the body of the each wikipedia entry. This also comes from HuggingFace and has 384 dimensions. 
    - All content is shaped into a JSON document and is inserted into the target Atlas cluster **concurrently** in batches of `1000` documents.

To run the script yourself and generate a different dataset: 

1. Set up your python environment (if not done already):

```
python3 -m venv .ENV
```

```
source .ENV/bin/activate
```

```
pip install -r requirements.txt
```

2. Update the `mongo_uri` variable with your connection string. 

3. Run the script:
```
python3 main.py
```

## Run the Web Application to Search for Articles

Switch to `webapp/` folder and run `flask_server.py`.

```bash
$ python flask_server.py
```

To use this application to search for Wikipedia articles, open a browser and navigate to `http://localhost:5050/`.
