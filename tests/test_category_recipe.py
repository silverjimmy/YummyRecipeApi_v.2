"""Test registration."""

import unittest
import json
import os
from app import create_app, db
from config import app_config

app = create_app("testing")
# app.config.from_object(app_config["testing"])

class TestCategoryRecipes(unittest.TestCase):
    """Test case for the authentication blueprint."""

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

        self.category = {
            "name" : "Lunch",
            "description" : "Meal taken at Lunch"
        }
        self.user_data1 = {
            "password": "12345678923",
            "username": "Black",
            "email": "black@gmail.com"
        }

        self.categoryrecipe = {
            "name" : "Supper",
            "description" : "Thrid Meal of the day"
        }
        res = self.client.post('/auth/register', data=self.user_data)
        self.res = self.client.post('/auth/login', data=self.user_data)
        self.assertEqual(self.res.status_code, 200)
        self.response_data_in_json_format = json.loads(self.res.data.decode('utf-8'))
        # get auth token
        self.token = (self.response_data_in_json_format["auth_token"])
        self.headers = {'Authorization': self.token}
        #register second user
        res1 = self.client.post('/auth/register', data=self.user_data1)
        self.res1 = self.client.post('/auth/login', data=self.user_data1)
        self.response_data_in_json_format2 = json.loads(self.res1.data.decode('utf-8'))
        # get token for second user
        self.token2 = (self.response_data_in_json_format2["auth_token"])
        self.headers2 = {'Authorization': self.token2}
        # create category for first user
        res_category = self.client.post('/category/', data=json.dumps(self.category)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_category.data.decode('utf8'))
        self.assertEqual("Category BlackB Added!",
                         res_message['message'])
        self.assertEqual(res_category.status_code, 201)

        res_categoryrecipe = self.client.post('/category/1/recipes/', data=json.dumps(self.categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Recipe SouthC has been added",
                         res_message['message'])
        self.assertEqual(res_category.status_code, 201)

    def test_add_category_recipe(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "SouthAfrica",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.post('/category/1/recipes/', data=json.dumps(categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Recipe SouthAfrica has been added",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 201)

    def test_add_already_category_recipe(self):
        """Test that a user can  add."""
        res_categoryrecipe1 = self.client.post('/category/1/recipes/', data=json.dumps(self.categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_categoryrecipe = self.client.post('/category/1/recipes/', data=json.dumps(self.categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Category Recipe already exists!!",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 409)

    def test_add_category_recipe_empty_name(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.post('/category/1/recipes/', data=json.dumps(categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Please provide a name!!",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 400)

    def test_add_category_recipe_invalid_token(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.post('/category/1/recipes/', data=json.dumps(categoryrecipe)
                                          ,headers={'Authorization':'hjbjnbgjksngjvkdfnkj'}
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Invalid token. Please log in again.",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 401)

    def test_get_all_category_recipes(self):
        """Test that a user get all recipes."""
        categoryrecipe = {
            "name" : "BlackBill",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.post('/category/1/recipes/', data=json.dumps(categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_categoryrecipes = self.client.get('/category/1/recipes/',headers=self.headers
                                          ,content_type="application/json")

        self.assertEqual(res_categoryrecipes.status_code, 200)
        

    def test_get_category_recipe_with_id(self):
        """Test that a user get all recipes."""
        res_categoryrecipes = self.client.get('/category/1/recipes/1',headers=self.headers
                                          ,content_type="application/json")

        self.assertEqual(res_categoryrecipes.status_code, 200)
        self.assertTrue(len(json.loads(res_categoryrecipes.data)) > 0)

    def test_get_category_recipe_invalid_token(self):
        """Test that a user get all recipes."""
        res_categoryrecipes = self.client.get('/category/1/recipes/1'
                                              ,headers={'Authorization':'hjbjnbgjksngjvkdfnkj'}
                                              ,content_type="application/json")

        self.assertEqual(res_categoryrecipes.status_code, 401)

    def test_get_category_recipe_unauthorized_token(self):
        """Test that a user get all recipes."""
        res_categoryrecipes = self.client.get('/category/1/recipes/'
                                              ,headers=self.headers2
                                              ,content_type="application/json")

        self.assertEqual(res_categoryrecipes.status_code, 404)

    def test_get_non_existent_category_recipe(self):
        """Test that a user get all recipes."""
        res_categoryrecipes = self.client.get('/category/1/recipes/3',headers=self.headers
                                          ,content_type="application/json")

        self.assertEqual(res_categoryrecipes.status_code, 404)

    def test_update_category_recipe_empty_name(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.put('/category/1/recipes/1', data=json.dumps(categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Name cannot be empty!",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 409)

    def test_update_category_recipe(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "BlackN",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.put('/category/1/recipes/1', data=json.dumps(categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Category Recipe updated",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 201)

    def test_update_non_existent_category_recipe(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "BlackN",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.put('/category/1/recipes/3', data=json.dumps(categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Recipe does not exist!",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 404)

    def test_update_category_recipe_with_same_name(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "SouthC",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.put('/category/1/recipes/1', data=json.dumps(categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Nothing to be updated!",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 409)

    def test_update_category_recipe_invalid_token(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "SouthC",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.put('/category/1/recipes/1', data=json.dumps(categoryrecipe)
                                          ,headers={'Authorization':'hjbjnbgjksngjvkdfnkj'}
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Invalid token. Please log in again.",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 401)

    def test_update_category_recipe_unauthorized_token(self):
        """Test that a user can  add."""
        categoryrecipe = {
            "name" : "SouthC",
            "description" : "Black don't crack"
        }
        res_categoryrecipe = self.client.put('/category/1/recipes/1', data=json.dumps(categoryrecipe)
                                          ,headers=self.headers2
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Category cannot be found",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 404)

    def test_delete_category_recipe(self):
        """Test that a user can  add."""
        res_categoryrecipe = self.client.delete('/category/1/recipes/1', data=json.dumps(self.categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Recipe succesfully deleted",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 200)

    def test_delete_non_existent_category_recipe(self):
        """Test that a user can  add."""
        res_categoryrecipe = self.client.delete('/category/1/recipes/4', data=json.dumps(self.categoryrecipe)
                                          ,headers=self.headers
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual(" Recipe not found ",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 404)

    def test_delete_category_recipe_invalid_token(self):
        """Test that a user can  add."""
        res_categoryrecipe = self.client.delete('/category/1/recipes/4', data=json.dumps(self.categoryrecipe)
                                          ,headers={'Authorization':'hjbjnbgjksngjvkdfnkj'}
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual("Invalid token. Please log in again.",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 401)

    def test_delete_category_recipe_unauthorized_token(self):
        """Test that a user can  add."""
        res_categoryrecipe = self.client.delete('/category/1/recipes/4', data=json.dumps(self.categoryrecipe)
                                          ,headers=self.headers2
                                          ,content_type="application/json")
        res_message = json.loads(res_categoryrecipe.data.decode('utf8'))
        self.assertEqual(" Recipe not found ",
                         res_message['message'])
        self.assertEqual(res_categoryrecipe.status_code, 404)

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()





if __name__ == "__main__":
    unittest.main()
