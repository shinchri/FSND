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
        DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')  
        DB_USER = os.getenv('DB_USER', 'postgres')  
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')  
        DB_NAME = os.getenv('DB_NAME', 'trivia_test')  
        self.database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': "What is the capital city of Germany?",
            'answer': "Berlin",
            'difficulty': 1,
            'category': 4
        }

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

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], None)

    def test_404_sent_requests_beyond_valid_page(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_get_questions_by_categories(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 2)
        self.assertEqual(data['current_category'], 1)

    def test_422_for_invalid_category_id(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_search_questions(self):
        res = self.client().post('/questions', json={"searchTerm": 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 2) # assuming there are two questions with %title%
        self.assertEqual(data['current_category'], None)

    def test_search_question_without_results(self):
        res = self.client().post('/questions', json={"searchTerm": "red apple"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['questions'])
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], None)

    def test_delete_questions(self):
        res = self.client().delete('/questions/27') # use different id everytime
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==27).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 27)
        self.assertEqual(question, None)

    def test_422_delete_none_existing_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_405_making_get_request_to_delete_question(self):
        res = self.client().get('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "method not allowed")

    def test_retrieve_quiz_questions_with_no_previous_questions(self):
        res = self.client().post('/quizzes', json={'previous_questions':[],'quiz_category': {"type":"geography","id":3}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(len(data['question']), 5) # there are five key,value pair in the dictionary

    def test_retrieve_quiz_questions_with_previous_questions(self):
        res = self.client().post('/quizzes', json={'previous_questions':[13,14,15],'quiz_category': {"type":"geography","id":3}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNone(data['question'])

    def test_422_invalid_category_id(self):
        res = self.client().post('/quizzes', json={'previous_questions':[13,14,15],'quiz_category': {"type":"geography","id":10}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")



    

    




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()