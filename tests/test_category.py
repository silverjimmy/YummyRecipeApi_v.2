"""Test registration."""

import unittest
import json
import os
from app import create_app, db
from config import app_config

app = create_app("testing")
# app.config.from_object(app_config["testing"])

class TestCategory(unittest.TestCase):
    """Test case for the category blueprint."""

    def setUp(self):
        """Set up test variables."""

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # create all tables
        db.create_all()

        self.user_data = {
            "password": "12345678923",
            "username": "Bruno",
            "email": "boon@gmail.com"
        }

        self.user_data1 = {
            "password": "12345678923",
            "username": "Black",
            "email": "black@gmail.com"
        }

        self.category = {
            "name" : "Breakfast",
            "description" : "First Meal of the day"
        }
        res1 = self.client.post('/auth/register', data=self.user_data)
        self.res = self.client.post('/auth/login', data=self.user_data)
        self.assertEqual(self.res.status_code, 200)
        res1 = self.client.post('/auth/register', data=self.user_data1)
        self.res1 = self.client.post('/auth/login', data=self.user_data1)
        self.assertEqual(self.res1.status_code, 200)
        self.response_data_in_json_format2 = json.loads(self.res1.data.decode('utf-8'))
        self.response_data_in_json_format = json.loads(self.res.data.decode('utf-8'))
        # get auth token
        self.token = (self.response_data_in_json_format["auth_token"])
        self.token2 = (self.response_data_in_json_format2["auth_token"])
        self.headers = {'Authorization': self.token}
        self.headers2 = {'Authorization': self.token2}

        # create category for first user



    def test_add_category(self):
        """Test that a user can  add."""
        res_category = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual("Category Blackg Added!",
                         res_message['message'])
        self.assertEqual(res_category.status_code, 201)

    def test_add_already_existing_category(self):
        """Test that a user can  add."""



        res_category = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")

        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category1.data.decode('utf8'))
        self.assertEqual("This Category already exists !",
                         res_message['message'])
        self.assertEqual(res_category1.status_code, 409)

    def test_add_category_with_empty_name(self):
        """Test that a user can  add."""
        category = {
            "name" : "",
            "description" : "Black don't crack"
        }
        res_category = self.client.post('/category/', data=json.dumps(category)
                                          ,headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual("Please enter a Category name!",
                         res_message['message'])
        self.assertEqual(res_category.status_code, 400)

    def test_add_category_with_invalid_token(self):
        """Test that a user can  add."""

        res_category = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers={'Authorization':'hjbjnbgjksngjvkdfnkj'}
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual("Invalid token. Please log in again.",
                         res_message['message'])
        self.assertEqual(res_category.status_code, 401)

    def test_get_all_category(self):
        """Test that a user can  add."""
        category = {
            "name" : "BlackD",
            "description" : "Black don't crack"
        }
        res_category1 = self.client.post('/category/', data=json.dumps(category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category2 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.get('/category/',headers=self.headers
                                          ,content_type="application/json")

        self.assertEqual(res_category.status_code, 200)
        
    def test_get_category_id(self):
        """Test that a user can  add."""
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.get('/category/1',headers=self.headers
                                          ,content_type="application/json")


        self.assertEqual(res_category.status_code, 200)

    def test_get_category_with_invalid_token(self):
        """Test that a user can  add."""
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.get('/category/1',headers={'Authorization':'hjbjnbgjksngjvkdfnkj'}
                                          ,content_type="application/json")


        self.assertEqual(res_category.status_code, 401)

    def test_get_category_with_unauthorized_token(self):
        """Test that a user can  add."""
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.get('/category/1',headers=self.headers2
                                          ,content_type="application/json")
        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 404)
        self.assertEqual("Category cannot be found",
                         res_message['message'])


    def test_get_none_existent_category_id(self):
        """Test that a user can  add."""
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.get('/category/2',headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 404)
        self.assertEqual("Category cannot be found",
                         res_message['message'])

    def test_update_category(self):
        """Test that a user can update category."""
        data = {
        "name": "Blackd",
        "description": "hey hey hey"
        }
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.put('/category/1',data= json.dumps(data),
                                          headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 200)
        self.assertEqual("Category Blackd Updated!",
                         res_message['message'])

    def test_update_non_existent_category(self):
        """Test that a user can update category."""
        data = {
        "name": "Blackd",
        "description": "hey hey hey"
        }
        res_category = self.client.put('/category/4',data= json.dumps(data),
                                          headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 404)
        self.assertEqual("Category does not exist!!",
                         res_message['message'])

    def test_update_empty_category_name(self):
        """Test that a user can not update category with empty name."""
        data = {
        "name": "",
        "description": "hey hey hey"
        }
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.put('/category/1',data= json.dumps(data),
                                          headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 400)
        self.assertEqual("Cannot update to empty category name.!!",
                         res_message['message'])

    def test_update_category_with_same_name(self):
        """Test that a user can not update category with same name."""
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        self.assertEqual(res_category1.status_code, 201)
        res_category = self.client.put('/category/1',data= json.dumps(self.category),
                                          headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 200)

    def test_update_category_with_invalid_token(self):
        """Test that a user can not update category with same name."""
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        self.assertEqual(res_category1.status_code, 201)
        res_category = self.client.put('/category/1',data= json.dumps(self.category),
                                          headers={'Authorization':'hjbjnbgjksngjvkdfnkj'}
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 401)
        self.assertEqual("Invalid token. Please log in again.",
                         res_message['message'])

    def test_update_category_with_unauthorized_token(self):
        """Test that a user can not update category with same name."""
        res_category1 = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        self.assertEqual(res_category1.status_code, 201)
        res_category = self.client.put('/category/1',data= json.dumps(self.category),
                                          headers=self.headers2
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 404)
        self.assertEqual("Category does not exist!!",
                         res_message['message'])


    def test_delete_category(self):
        """Test that a user can update category."""
        res_category = self.client.post('/category/',data= json.dumps(self.category),
                                          headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.delete('/category/1',
                                          headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 200)
        self.assertEqual("Category deleted.!!",
                         res_message['message'])

    def test_delete_non_existent_category(self):
        """Test that a user can update category."""
        res_category = self.client.delete('/category/1',
                                          headers=self.headers
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 404)
        self.assertEqual("Category does not exist.!!",
                         res_message['message'])

    def test_delete_category_with_unauthorized_token(self):
        """Test that a user can update category."""
        res_category1 = self.client.post('/category/',data= json.dumps(self.category),
                                          headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.delete('/category/1',
                                          headers=self.headers2
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 404)
        self.assertEqual("Category does not exist.!!",
                         res_message['message'])

    def test_delete_category_with_invalid_token(self):
        """Test that a user can update category."""
        res_category1 = self.client.post('/category/',data= json.dumps(self.category),
                                          headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.delete('/category/1',
                                          headers={'Authorization':'hjbjnbgjksngjvkdfnkj'}
                                          ,content_type="application/json")

        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual(res_category.status_code, 401)
        self.assertEqual("Invalid token. Please log in again.",
                         res_message['message'])
    def test_search_non_existent_category(self):
        """Test that a user can  add."""
        category = {
            "name" : "BlackD",
            "description" : "Black don't crack"
        }
        res_category1 = self.client.post('/category/', data=json.dumps(category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.get('/category/?q=nothin',headers=self.headers
                                          ,content_type="application/json")

        self.assertEqual(res_category.status_code, 200)
        self.assertTrue(len(json.loads(res_category.data)) == 0)

    def test_search_existent_category(self):
        """Test that a user can  add."""
        category = {
            "name" : "BlackD",
            "description" : "Black don't crack"
        }
        res_category1 = self.client.post('/category/', data=json.dumps(category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_category = self.client.get('/category/?q=black',headers=self.headers
                                          ,content_type="application/json")

        self.assertEqual(res_category.status_code, 200)
        self.assertTrue(len(json.loads(res_category.data)) > 0)


    def tearDown(self):
        db.drop_all()
        self.app_context.pop()





if __name__ == "__main__":
    unittest.main()
