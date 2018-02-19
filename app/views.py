"""cat list API endpoints."""
import re
from flask import g
import jwt
import json
from flask_restful import reqparse, Resource
from flask import jsonify, make_response, request
from app.models import User, Category, Recipe
from app import db

def validate_token(self):
    # get the auth token
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('Authorization', type=str, location="headers")
    args = self.reqparse.parse_args()
    token = args["Authorization"]
    if token:
        user_id = User.decode_auth_token(token)
        return user_id

class AuthRegister(Resource):
    """User registration."""

    def __init__(self):
        """Initialize register resource endpoint."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('password', type=str,
                                   help='Password required', required=True)
        self.reqparse.add_argument('username', type=str,
                                   help='Username required', required=True)
        self.reqparse.add_argument('email', type=str, help='Email required')

    def post(self):
        """Create new user."""
        args = self.reqparse.parse_args()
        username = args['username']
        if len(username.strip(" ")) == 0:
            response = {
                        "message": "Please provide a username!",
                        "status": "fail"
                        }

            return response, 400

        if len(args['password']) < 8:
            response = {
                        'message': 'Password needs to be 8 characters long!',
                        'status': 'fail'
                        }
            return response, 400

        if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$',
                        args['email']):
            response = {
                        'status': 'fail',
                        'message': 'Invalid email!'
                        }
            return (response), 400

        if User.query.filter_by(username=args['username']).first():
                    # if user with given username exists
            response = {
                        'message': 'A User with the same name already exists!',
                        'status': 'fail'
                        }
            return response, 409
        if User.query.filter_by(email=args['email']).first():
                    # if user with given username exists
            response = {
                        'message': 'This email account has already been used!',
                        'status': 'fail'
                        }
            return response, 409

        new_user = User(username=args['username'],
                    email=args['email'],
                    password=args['password'])
        new_user.save()
        return {'message': 'User Registration success!'}, 201


class AuthLogin(Resource):
    """Log in resource."""

    def __init__(self):
        """Initialize log in resource."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str,
                                   help='Username required', required=True)
        self.reqparse.add_argument('password', type=str,
                                   help='Password required', required=True)

    def post(self):
        """Authenticate user."""
        args = self.reqparse.parse_args()
        try:
            auth_user = User.query.filter_by(username=args['username'], password=args['password']).first()

            if not auth_user:
                response = {'status': 'fail',
                            'message': 'Invalid username/password!'
                            }
                return (response), 401
            auth_token = auth_user.encode_auth_token(auth_user.id)

            if not auth_token:
                response = {'status': 'fail',
                            'message': 'Login failed! Please try again'
                            }
                return (response), 401

            response = {'status': 'success',
                        'message': 'You have successfully logged in.',
                        'auth_token': auth_token
                        }

            return (response), 200
        except Exception as e:
            response = {'status': str(e),
                        'message': 'Login failed! Please try again'
                        }
            return (response), 500

class CategoryView(Resource):
    """Category list CRUD functionality."""

    def __init__(self):
        """Initialize category Resource."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('Authorization', type=str, location="headers")
        self.reqparse.add_argument('name', type=str, location="json")
        self.reqparse.add_argument('description', type=str, location="json")


    def post(self):
        """Add new category."""
        args = self.reqparse.parse_args()
        user_id = validate_token(self)

        if not isinstance(user_id, int):
            response = {
                        'status': 'fail',
                        'message': user_id
                        }
            return (response), 401

        if not args['name']:
            response = {
                        'message': 'Please enter a Category name!',
                        'status': 'fail'
                        }
            return response, 400

        if Category.query.filter_by(name=args['name'], created_by=user_id).first():
                    # if category with given name exists
            response = {
                        'message': 'This Category already exists !',
                        'status': 'fail'
                        }
            return response, 409
        category = Category(name=args['name'],
                                description=args['description'],
                                created_by=user_id)
        category.save()
        response = {
                    'message': 'Category {} Added!'.format(args['name']),
                    'status': 'success'
                    }
        return response, 201

    def get(self, id=None):
        """View categories."""
        user_id = validate_token(self)
        if not isinstance(user_id, int):
            response = {
                        'status': 'fail',
                        'message': user_id
                        }
            return (response), 401

        self.reqparse.add_argument('limit', type=int, help='invalid limit',
            required=False, default=20, location='args')
        self.reqparse.add_argument('q', type=str, help='Invalid Query',
            required=False, location='args')
        self.reqparse.add_argument('page', type=int, required=False, default=1, location='args')
        args = self.reqparse.parse_args()
        categories_data = []
        if id:
            # retrieve a category
            category = Category.query.filter_by(id=id, created_by=user_id).first()
            if not category:
                    response = {
                                'status': 'fail',
                                'message': 'Category cannot be found'
                                }
                    return (response), 404

            if not category.recipes:
                    recipes = {}
            else:
                recipe_data = []
            for recipe in category.recipes:
                recipes = {
                        "recipe_id": recipe.id,
                        "recipe_name": recipe.name,
                        "recipe_description": recipe.description
                        }
                recipe_data.append(recipes)
            response = { "category" :
                                      {
                                        'id': category.id,
                                        'title': category.name,
                                        'description': category.description,
                                        'created_on': str(category.created_on),
                                        'recipes': recipe_data
                                      }
                       }
            return (response), 200
        if args['q']:

            category = Category.query \
                          .filter(Category.name
                                  .ilike('%' + args['q'] + '%')).filter_by(created_by=user_id).paginate(page=args.get('page', 1),
                                                                         per_page=args.get('limit', 3),
                                                                         error_out=False)


            for cat in category.items:
                categories = {
                        'id': cat.id,
                        'title': cat.name,
                        'description': cat.description,
                        'created_on': str(cat.created_on),
                        }
                categories_data.append(categories)
                format_category = {
                                     "categories": categories_data,
                                    "total": category.pages,
                                    "current_page": category.page,
            }
            return (format_category), 200

        else:
            category = (Category.query.filter_by(created_by=user_id).paginate(page=args['page'],
                                                   per_page=args['limit'],
                                                   error_out=False))

            for meal in category.items:
                categories = {
                        'id': meal.id,
                        'title': meal.name,
                        'description': meal.description,
                        'created_on': str(meal.created_on),
                        }
                categories_data.append(categories)
            format_category = {
                                    "categories": categories_data,
                                    "total": category.pages,
                                    "current_page": category.page,
            }
            return (format_category), 200

    def put(self, id=None):
        """Update category."""
        args = self.reqparse.parse_args()
        user_id = validate_token(self)

        if not isinstance(user_id, int):
            response = {
                        'status': 'fail',
                        'message': user_id
                        }
            return (response), 401
        updatecategory = Category.query.filter_by(id=id, created_by=user_id).first()
        if not updatecategory:
            response = {
                        'message': 'Category does not exist!!',
                        'status': 'success'
                        }
            return response, 404
        if args["name"]:
            if Category.query.filter_by(
                    name=args.get('name').lower()).first():
                    return ({"error": "Cannot update category with same name."},
                            409)
            else:
                    updatecategory.name = args.get("name")
                    updatecategory.description = args["description"]
                    updatecategory.save()

                    response = {
                                'message': 'Category {} Updated!'.format(args.get('name')),
                                'status': 'success'
                                }
                    return response, 200

        else:
            response = {
                        'message': 'Cannot update to empty category name.!!',
                        'status': 'fail'
                        }
            return response, 400



    def delete(self, id=None):
        """Delete category."""
        user_id = validate_token(self)
        if not isinstance(user_id, int):
            response = {
                        'status': 'fail',
                        'message': user_id
                        }
            return (response), 401
        deletecat = Category.query.filter_by(id=id, created_by=user_id).first()
        if deletecat:
                deletecat.delete()
                response = {
                            'message': 'Category deleted.!!',
                            'status': 'success'
                            }
                return response, 200
        else:
            response = {
                        'message': 'Category does not exist.!!',
                        'status': 'fail'
                        }
            return response, 404

class RecipeView(Resource):
    def __init__(self):
        """Initialize category Resource."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        self.reqparse.add_argument('description', type=str)

    def post(self, id=None):
        args = self.reqparse.parse_args()
        user_id = validate_token(self)
        if not isinstance(user_id, int):
            response = {
                        'status': 'fail',
                        'message': user_id
                        }
            return (response), 401

        if not args['name']:
            response = {
                        'message': 'Please provide a name!!',
                        'status': 'fail'
                        }
            return response, 400
        category = Category.query.filter_by(id=id).first()
        if not category:
            response = {
                        'message': 'Category does not exist.!!',
                        'status': 'fail'
                        }
            return response, 404

        duplicate_recipe = Recipe.query.filter_by(name=
                                              args['name'],
                                              category_id=
                                              id).first()
        if duplicate_recipe:
            response = {
                        'message': 'Category Recipe already exists!!',
                        'status': 'fail'
                        }
            return response, 409



        category_id = category.id
        recipe = Recipe(name=args['name'],
                    description=args['description'],
                    category_id=category_id)
        recipe.save()
        response = {
                    'status': 'success',
                    'message': 'Recipe {} has been added'
                    .format(args['name'])
                    }
        return response, 201

    def get(self, id, recipe_id=None):
        """View Category."""
        user_id = validate_token(self)
        if not isinstance(user_id, int):
            response = {
                        'status': 'fail',
                        'message': user_id
                        }
            return (response), 401

        self.reqparse.add_argument('limit', type=int, help='invalid limit',
            required=False, default=20, location='args')
        self.reqparse.add_argument('q', type=str, help='Invalid Query',
            required=False, location='args')
        self.reqparse.add_argument('page', type=int, required=False, default=1, location='args')
        args = self.reqparse.parse_args()
        recipes_data = []   
        if id:
            # retrieve a category
            category = Category.query.filter_by(id=id, created_by=user_id).first()
            if not category:
                    response = {
                                'status': 'fail',
                                'message': 'Category cannot be found'
                                }
                    return (response), 404
            if recipe_id:
                recipe = Recipe.query.filter_by(id=recipe_id, category_id=id).first()

                if not recipe:
                        response = {
                                    'status': 'fail',
                                    'message': 'Recipe cannot be found'
                                    }
                        return (response), 404
                else:

                    response = {
                            "recipe_id": recipe.id,
                            "recipe_name": recipe.name,
                            "recipe_description": recipe.description
                            }
                    return (response), 200
            else:
                categoryrecipes = (Recipe.query.filter_by(category_id=id))
                recipes = []
                for recipe in categoryrecipes:
                    recipe = {
                            'id': recipe.id,
                            'title': recipe.name,
                            'description': recipe.description,
                            'created_on': str(recipe.created_on),
                            }
                    recipes.append(recipe)

        if args['q']:
            recipe = Recipe.query \
                          .filter_by(category_id=user_id) \
                          .filter(Recipe.name
                                  .ilike('%' + args['q'] + '%')).paginate(page=args['page'],
                                                                         per_page=args['limit'],
                                                                         error_out=False)


            for recipe in recipe.items:
                categories = {
                        'id': recipe.id,
                        'title': recipe.name,
                        'description': recipe.description,
                        'created_on': str(recipe.created_on),
                        }
                recipes_data.append(categories)
            return (recipes_data), 200

        else:
            recipe = (Recipe.query.filter_by(recipe_id=id).paginate(page=args['page'],
                                                per_page=args['limit'],
                                                error_out=False))

            for meal in recipe:
                recipes = {
                        'id': meal.id,
                        'title': meal.name,
                        'description': meal.description,
                        'created_on': str(meal.created_on),
                        }
                recipes_data.append(recipes)           

                format_recipe = {
                                        "recipes": recipes_data,
                                        "total":"recipe.pages"
                }
                return (format_recipe), 200


        return (response), 200

    def put(self, id, recipe_id):
        args = self.reqparse.parse_args()
        user_id = validate_token(self)
        if not isinstance(user_id, int):
            response = {
                        'status': 'fail',
                        'message': user_id
                        }
            return (response), 401

        if id:
            # retrieve a category
            category = Category.query.filter_by(id=id, created_by=user_id).first()
            if not category:
                    response = {
                                'status': 'fail',
                                'message': 'Category cannot be found'
                                }
                    return (response), 404
        recipe = Recipe.query.filter_by(id=recipe_id, category_id=id).first()
        if not recipe:
            response = {
                        'status': 'fail',
                        'message': 'Recipe does not exist!'
                        }
            return response, 404
        if not args["name"]:
            response = {
                       'status': 'fail',
                       'message': 'Name cannot be empty!'
                       }
            return response, 409
        if recipe.name == args['name'] and \
            recipe.description == args['description']:

            response = {
                       'status': 'fail',
                       'message': 'Nothing to be updated!'
                       }
            return response, 409

        recipe.name = args['name']
        recipe.description = args['description']

        recipe.save()

        response = {
                    'status': 'success',
                    'message': 'Category Recipe updated'
                    }
        return response, 201
        
    def delete(self, id, recipe_id):
        user_id = validate_token(self)
        if not isinstance(user_id, int):
            response = {
                        'status': 'fail',
                        'message': user_id
                        }
            return (response), 401
        args = self.reqparse.parse_args()
        recipe = Recipe.query.filter_by(id=recipe_id, category_id=id).first()
        if not recipe:
            response = {
                        'status': 'fail',
                        'message': ' Recipe not found '
                        }
            return response, 404

        recipe.delete()

        response = {
                    'status': 'success',
                    'message': 'Recipe succesfully deleted'
                    }
        return response, 200
