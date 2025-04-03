# File: services/mongo_handler.py

import logging
from pymongo import MongoClient, errors

class MongoHandler:
    def __init__(self, connection_string, db_name, retention_limit=400000, delete_count=1000):
        """
        Initialize the MongoHandler with connection parameters.

        :param connection_string: MongoDB connection string.
        :param db_name: Name of the database.
        :param retention_limit: Hard limit on document count (default 400,000).
        :param delete_count: Number of oldest documents to delete when limit is exceeded.
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            self.retention_limit = retention_limit
            self.delete_count = delete_count
            logging.info(f"Connected to MongoDB database: {db_name}")

        except errors.ConnectionError as ce:
            logging.error("Failed to connect to MongoDB", exc_info=True)
            raise ce

    def verify_connection(self):
        """
        Verify the connection to the MongoDB server.
        """
        try:
            self.client.admin.command('ping')
            logging.info("MongoDB connection verified.")
            return True
        except errors.ConnectionFailure as cf:
            logging.error("MongoDB connection failed", exc_info=True)
            return False


    def get_collection(self, collection_name):
        """
        Retrieve a collection by name.
        """
        return self.db[collection_name]


    def insert_document(self, collection_name, document):
        """
        Insert a document into a specified collection and trigger data retention if needed.

        :param collection_name: Name of the collection.
        :param document: Dictionary representing the document to insert.
        :return: The inserted document's id.
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            logging.info(f"Inserted document with id {result.inserted_id} into {collection_name}")
            # After insertion, check retention.
            self.data_retention(collection_name)
            return result.inserted_id

        except Exception as e:
            logging.error("Error inserting document", exc_info=True)
            raise e


    def data_retention(self, collection_name):
        try:
            collection = self.get_collection(collection_name)
            count = collection.estimated_document_count()
            logging.info(f"Collection '{collection_name}' has {count} documents.")
            if count > self.retention_limit:
                # Calculate number to delete so that exactly retention_limit remain.
                num_to_delete = count - self.retention_limit
                logging.info(f"Document count {count} exceeds retention limit {self.retention_limit}. Deleting {num_to_delete} oldest records...")
                oldest_docs = list(collection.find().sort('_id', 1).limit(num_to_delete))
                if oldest_docs:
                    ids_to_delete = [doc['_id'] for doc in oldest_docs]
                    result = collection.delete_many({'_id': {'$in': ids_to_delete}})
                    logging.info(f"Deleted {result.deleted_count} documents from {collection_name}.")
                else:
                    logging.info("No documents found to delete for retention.")

        except Exception as e:
            logging.error("Error in data retention process", exc_info=True)


    def find_one(self, collection_name, query):
        """
        Find a document matching the query.
        """
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query)
        except Exception as e:
            logging.error("Error finding document", exc_info=True)
            raise e


    def update_document(self, collection_name, query, update_data):
        """
        Update a document in the specified collection.
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, update_data)
            logging.info(f"Updated {result.modified_count} document(s) in {collection_name}")
            return result.modified_count
        except Exception as e:
            logging.error("Error updating document", exc_info=True)
            raise e


    def delete_document(self, collection_name, query):
        """
        Delete a document from the specified collection.
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            logging.info(f"Deleted {result.deleted_count} document(s) from {collection_name}")
            return result.deleted_count
        except Exception as e:
            logging.error("Error deleting document", exc_info=True)
            raise e


    def close(self):
        """
        Close the MongoDB connection.
        """
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed.")
