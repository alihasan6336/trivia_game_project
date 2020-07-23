import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "test_trivia"
        self.database_path = "postgres://{}/{}".format('postgres:P01019056637p@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_data['success'], True)
        self.assertTrue(len(json_data['categories']))
        self.assertTrue(json_data['total_categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_data['success'], True)
        self.assertTrue(len(json_data['questions']))
        self.assertTrue(json_data['total_questions'])
        self.assertTrue(len(json_data['categories']))
        self.assertTrue(json_data['total_categories'])

    def test_error_404_on_paginated_questions(self):
        res = self.client().get('/questions?page=1000')
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(json_data['success'], False)
        self.assertEqual(json_data['error'], 404)
        self.assertEqual(json_data['message'], 'resource not found')

    def test_delete_question(self):
        question = Question(question='question', answer='answer', category=1, difficulty=1)
        question.insert()
        question_id = question.id

        res = self.client().delete('/questions/' + str(question.id))
        json_data = json.loads(res.data)
        
        question = Question.query.filter(Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_data['success'], True)
        self.assertEqual(json_data['deleted_id'], question_id)
        self.assertTrue(len(json_data['questions']))
        self.assertTrue(json_data['total_questions'])

        self.assertEqual(question, None)

    def test_error_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/100000')
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(json_data['success'], False)
        self.assertEqual(json_data['error'], 422)
        self.assertEqual(json_data['message'], 'unprocessable')

    def test_post_question(self):
        question_fields = {
            'question': 'question1',
            'answer': 'answer1',
            'category': 1,
            'difficulty': 1,
        }

        res = self.client().post('/questions', json=question_fields)
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_data['success'], True)
        self.assertTrue(json_data['created_question'])
        self.assertTrue(len(json_data['questions']))
        self.assertTrue(json_data['total_questions'])

    def test_422_error_in_post_questions(self):
        question_fields = {
            'question': '',
            'answer': '',
            # missing the 'category' field!
            'difficulty': 1,
        }

        res = self.client().post('/questions', json=question_fields)
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(json_data['success'], False)
        self.assertEqual(json_data['error'], 422)
        self.assertEqual(json_data['message'], 'unprocessable')

    def test_search_in_questions(self):
        res = self.client().post('/questions', json={'searchTerm': 'question1'})
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_data['success'], True)
        self.assertTrue(len(json_data['questions']))
        self.assertTrue(json_data['total_questions'])
    
    def test_with_wrong_value_for_searchTerm(self):
        res = self.client().post('/questions', json={'searchTerm': 'asdaasdasdfasdasdasdfasfassd'})
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(json_data['success'], False)
        self.assertEqual(json_data['error'], 404)
        self.assertEqual(json_data['message'], 'resource not found')

    def test_get_questions_based_on_category(self):
        category_id = 1
        res = self.client().get('/categories/' + str(category_id) + '/questions')
        json_data = json.loads(res.data)

        category = Category.query.filter(Category.id == category_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_data['success'], True)
        self.assertEqual(json_data['current_category'], category.type)
        self.assertTrue(len(json_data['questions']))
        self.assertTrue(json_data['total_questions'])

    def test_404_in_get_questions_based_on_category(self):
        category_id = 100000
        res = self.client().get('/categories/' + str(category_id) + '/questions')
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(json_data['success'], False)
        self.assertEqual(json_data['error'], 404)
        self.assertEqual(json_data['message'], 'resource not found')

    def test_post_quizzes(self):
        requested_data = {
            'quiz_category': {
                'id': 5,
                'type': 'Entertainment'
            }, 'previous_questions': [10, 11]
        }

        res = self.client().post('/quizzes', json=requested_data)
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_data['success'], True)
        self.assertTrue(len(json_data['question']))

    def test_400_in_post_quizzes(self):
        requested_data = {
            'quiz_category': {
                'id': 15,
                'type': 'category1'
            }
        }

        res = self.client().post('/quizzes', json=requested_data)
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(json_data['success'], False)
        self.assertEqual(json_data['error'], 400)
        self.assertEqual(json_data['message'], 'bad request')

    def test_422_in_post_quizzes(self):
        requested_data = {
            'quiz_category': {
                'id': 15,
                'type': '5'
            }, 'previous_questions': [10, 11]
        }

        res = self.client().post('/quizzes', json=requested_data)
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(json_data['success'], False)
        self.assertEqual(json_data['error'], 422)
        self.assertEqual(json_data['message'], 'unprocessable')

        










# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()