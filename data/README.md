## Insert the Wikipedia dataset into the database

5000 Wikipedia articles have already been downloaded, vectorized, and added to the `data/` folder, so switch to that folder.

`wikipedia_tiny.json` is meant to be used with [`mongoimport`](https://www.mongodb.com/docs/database-tools/mongoimport/) or Compass to import data, whereas `wikipedia_tiny.gz` is the same file but compressed to make it easier to transfer around. This file contains 5,000 total records of cleaned wikipedia pages in English, French, German, Italian, and Frisian. 

To import `wikipedia_tiny.json` into a cluster using a database user authenticating with SCRAM (i.e. user & password), please use [`mongoimport`](https://www.mongodb.com/docs/database-tools/mongoimport/) like this:
```bash
mongoimport 'mongodb+srv://<username>:<password>@<clustername>.<atlasProjectHash>.mongodb.net/{DATABASE}' --collection {COLLECTION} --file='wikipedia_tiny.json'
```
To accomplish this using the Compass GUI, [follow this guide](https://www.mongodb.com/docs/compass/current/import-export/#import-data-into-a-collection).

# Get your own clean wikipedia dataset (optional)

 If you already inserted the Wikipedia dataset into your collection from the last step, you can skip this step. This optional step is if you want to run a vector embedding process on a different Wikipedia dataset.

 All code is contained within `main.py` and requirements within `requirements.txt`. All configuration for `main.py` is located immediately within the `main()` function near the top of the file, with comments indicated what to change.

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
pip install --no-deps multiprocess==0.70.15
```

2. Run the script:
```
python3 main.py
```