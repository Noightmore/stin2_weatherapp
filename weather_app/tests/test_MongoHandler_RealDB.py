import unittest
import os
from dotenv import load_dotenv
from weather_app.services.MongoHandler import MongoHandler
import os


class TestMongoHandler_RealDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        # Get the directory of the current file (inside tests)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Go up two levels to the main project folder
        project_dir = os.path.dirname(os.path.dirname(current_dir))

        DOT_ENV_PATH = os.path.join(project_dir, '.env.local')

        # check if file is found
        if not os.path.exists(DOT_ENV_PATH):
            raise FileNotFoundError(f".env.local file not found at {DOT_ENV_PATH}")

        # Load environment variables from .env.local
        load_dotenv(DOT_ENV_PATH)

        cls.mongo_url = os.getenv("MONGO_URL")
        if cls.mongo_url is None:
            raise Exception("MONGO_URL not set in .env.local")
        cls.db_name = "test_db"  # use a test database

        # Set a low retention limit for testing purposes
        cls.retention_limit = 5
        cls.delete_count = 2
        cls.handler = MongoHandler(cls.mongo_url, cls.db_name,
                                   retention_limit=cls.retention_limit,
                                   delete_count=cls.delete_count)

        # Ensure we start with a clean database
        #cls.handler.db.drop_database(cls.db_name) # DANGEROUS


    @classmethod
    def tearDownClass(cls):
        cls.handler.close()


    def test_insert_and_find(self):
        collection_name = "weather_data"
        doc = {
            "message": "Count: 24",
            "cod": "200",
            "city_id": 4298960,
            "calctime": 0.00297316,
            "cnt": 24,
            "list": [
                {
                    "dt": 1578384000,
                    "main": {
                        "temp": 275.45,
                        "feels_like": 271.7,
                        "pressure": 1014,
                        "humidity": 74,
                        "temp_min": 274.26,
                        "temp_max": 276.48
                    },
                    "wind": {"speed": 2.16, "deg": 87},
                    "clouds": {"all": 90},
                    "weather": [
                        {"id": 501, "main": "Rain", "description": "moderate rain", "icon": "10n"}
                    ],
                    "rain": {"1h": 0.9}
                }
            ]
        }
        inserted_id = self.handler.insert_document(collection_name, doc)
        self.assertIsNotNone(inserted_id)
        found_doc = self.handler.find_one(collection_name, {"_id": inserted_id})
        self.assertIsNotNone(found_doc)
        self.assertEqual(found_doc["cod"], "200")


    def test_update_document(self):
        collection_name = "weather_data"
        doc = {
            "message": "Count: 24",
            "cod": "200",
            "city_id": 4298960,
            "calctime": 0.00297316,
            "cnt": 24,
            "list": []
        }
        inserted_id = self.handler.insert_document(collection_name, doc)
        modified_count = self.handler.update_document(collection_name, {"_id": inserted_id}, {"$set": {"message": "Count: 25"}})
        self.assertEqual(modified_count, 1)
        found_doc = self.handler.find_one(collection_name, {"_id": inserted_id})
        self.assertEqual(found_doc["message"], "Count: 25")


    def test_delete_document(self):
        collection_name = "weather_data"
        doc = {
            "message": "Count: 24",
            "cod": "200",
            "city_id": 4298960,
            "calctime": 0.00297316,
            "cnt": 24,
            "list": []
        }
        inserted_id = self.handler.insert_document(collection_name, doc)
        deleted_count = self.handler.delete_document(collection_name, {"_id": inserted_id})
        self.assertEqual(deleted_count, 1)
        found_doc = self.handler.find_one(collection_name, {"_id": inserted_id})
        self.assertIsNone(found_doc)


    def test_data_retention(self):
        collection_name = "weather_data"
        # With a retention limit of 5, inserting 7 documents should trigger deletion of 2 oldest.
        for i in range(7):
            doc = {
                "message": f"Count: {24 + i}",
                "cod": "200",
                "city_id": 4298960,
                "calctime": 0.00297316,
                "cnt": 24,
                "list": [{"dt": 1578384000 + i}]
            }
            self.handler.insert_document(collection_name, doc)

        collection = self.handler.get_collection(collection_name)
        count = collection.estimated_document_count()
        self.assertEqual(count, self.retention_limit)  # should be 5 documents left


if __name__ == '__main__':
    unittest.main()
