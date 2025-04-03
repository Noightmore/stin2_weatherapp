import unittest
import mongomock
from weather_app.services.MongoHandler import MongoHandler

class TestMongoHandler_MockDB(unittest.TestCase):
    def setUp(self):
        # Create a mongomock client and inject it into MongoHandler.
        self.mock_client = mongomock.MongoClient()
        # We instantiate our MongoHandler normally.
        # The connection string is not used because we override the client.
        self.handler = MongoHandler("mongodb://fake_connection", "test_db")
        # Override the client's database with the mock client
        self.handler.client = self.mock_client
        self.handler.db = self.mock_client["test_db"]

        # Ensure the test database is clean before each test.
        self.mock_client.drop_database("test_db")


    def test_insert_and_find_document(self):
        collection_name = "cities"
        doc = {"name": "Test City", "latitude": 12.34, "longitude": 56.78}
        inserted_id = self.handler.insert_document(collection_name, doc)
        self.assertIsNotNone(inserted_id)

        # Now, retrieve the document
        found_doc = self.handler.find_one(collection_name, {"_id": inserted_id})
        self.assertIsNotNone(found_doc)
        self.assertEqual(found_doc["name"], "Test City")


    def test_update_document(self):
        collection_name = "cities"
        doc = {"name": "Update City", "latitude": 10.0, "longitude": 20.0}
        inserted_id = self.handler.insert_document(collection_name, doc)

        # Update the document's name
        modified_count = self.handler.update_document(collection_name, {"_id": inserted_id}, {"$set": {"name": "Updated City"}})
        self.assertEqual(modified_count, 1)

        found_doc = self.handler.find_one(collection_name, {"_id": inserted_id})
        self.assertEqual(found_doc["name"], "Updated City")


    def test_delete_document(self):
        collection_name = "cities"
        doc = {"name": "Delete City", "latitude": 0, "longitude": 0}
        inserted_id = self.handler.insert_document(collection_name, doc)

        # Now, delete the document
        deleted_count = self.handler.delete_document(collection_name, {"_id": inserted_id})
        self.assertEqual(deleted_count, 1)

        found_doc = self.handler.find_one(collection_name, {"_id": inserted_id})
        self.assertIsNone(found_doc)


    def test_data_retention(self):
        collection_name = "weather_data"
        # Set a low retention limit for testing purposes.
        self.handler.retention_limit = 10
        self.handler.delete_count = 3

        # Insert 12 documents (exceeding the limit)
        for i in range(12):
            doc = {"data": f"test_{i}"}
            self.handler.insert_document(collection_name, doc)

        # Now, check that the collection contains 12 - 3 = 9 documents (if 3 were deleted).
        collection = self.handler.get_collection(collection_name)
        count = collection.estimated_document_count()
        self.assertEqual(count, 9)

if __name__ == '__main__':
    unittest.main()
