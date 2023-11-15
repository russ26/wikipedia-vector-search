from sentence_transformers import SentenceTransformer, util
from flask import Flask, render_template, request, jsonify
import os
import sys
import pymongo
import ssl
from bson import json_util
import json

sys.path.insert(1, '../config/')
from config_database import mongo_uri, db, collection

app = Flask(__name__,
            static_url_path='',
            static_folder='../encoder',)

connection = pymongo.MongoClient(mongo_uri)
product_collection = connection[db][collection]
preTrainedModelName = "all-MiniLM-L6-v2"
model = SentenceTransformer(preTrainedModelName)


@app.route('/search', methods=['GET'])
def search():

    vector_text = request.args.get('vector', default=None, type=str)
    boost_text = request.args.get('text', default=None, type=str) 
    languages = request.args.get('languages', default=None, type=str).split(",")
    vector_query = model.encode(vector_text).tolist()
    vectorSearchPipeline = [
        {
        '$vectorSearch': {
            'index': 'default', 
            'path': 'vector', 
            'filter': {
                '$or': [
                    {
                        'language': {
                            '$in': languages,
                        }
                    }
                ]
            }, 
            'queryVector': vector_query, 
            'numCandidates': 20, 
            'limit': 20
        }
        }, {
            '$addFields': {
                'vs_score': {
                    '$meta': 'vectorSearchScore'
                }, 
                'fts_score': 0,
                'total_search_score':  {
                    '$meta': 'vectorSearchScore'
                }
            }
        },
        {
            '$project': {
                '_id': 0, 
                'vector': 0
            }
        }
    ]

    hybridPipeline = [
    {
        '$vectorSearch': {
            'index': 'default', 
            'path': 'vector', 
            'filter': {
                '$or': [
                    {
                        'language': {
                            '$in': languages,
                        }
                    }
                ]
            }, 
            'queryVector': vector_query, 
            'numCandidates': 200, 
            'limit': 200
        }
    }, {
        '$addFields': {
            'vs_score': {
                '$meta': 'vectorSearchScore'
            }
        }
    }, {
        '$unionWith': {
            'coll': collection, 
            'pipeline': [
                {
                    '$search': {
                        'index': 'textSearch', 
                        'compound': {
                            'must': [{
                                'text': {
                                    'query': boost_text,
                                    'path': "text",
                            }
                            }],
                            'should': [{
                                'text': {
                                    'query': vector_text,
                                    'path': "text",
                            }
                            }],
                            'filter': [{
                                "text": {
                                    "path": "language",
                                    "query": languages
                                } 
                            }
                            ],
                        },
                    }
                }, {
                    '$limit': 200
                }, {
                    '$addFields': {
                        'fts_score': {
                            '$divide': [
                                {'$meta': "searchScore"}, 10
                            ]
                        }
                    }
                }
            ]
        }
    }, {
        '$group': {
            '_id': '$_id', 
            'language': {
                '$first': '$language'
            }, 
            'title': {
                '$first': '$title'
            }, 
            'text': {
                '$first': '$text'
            }, 
            'url': {
                '$first': '$url'
            }, 
            'vs_score': {
                '$max': '$vs_score'
            }, 
            'fts_score': {
                '$max': '$fts_score'
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'language': 1, 
            'title': 1, 
            'text': 1, 
            'url': 1, 
            'vs_score': {
                '$ifNull': [
                    '$vs_score', 0
                ]
            }, 
            'fts_score': {
                '$ifNull': [
                    '$fts_score', 0
                ]
            },
            'total_search_score': {'$sum': ["$vs_score", "$fts_score"]}
        }
    },
    {
        '$sort': {
            'total_search_score': -1
        }
    },
    {
        '$limit': 20
    }
    ]

    if len(boost_text) <= 0:
         pipeline = vectorSearchPipeline
    else: 
        pipeline = hybridPipeline
    

    # Execute the pipeline
    docs = list(product_collection.aggregate(pipeline))
    # Return the results unders the docs array field
    json_result = json_util.dumps(
        {'docs': docs}, json_options=json_util.RELAXED_JSON_OPTIONS)
    return jsonify(json_result)


# page
@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="localhost", port=5050, debug=True)
