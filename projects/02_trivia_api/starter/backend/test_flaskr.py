import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
categories = [
    {"id": 1, "type": "science"},
    {"id": 2, "type": "art"},
    {"id": 3, "type": "geography"},
    {"id": 4, "type": "history"},
    {"id": 5, "type": "entertainment"},
    {"id": 6, "type": "sports"}
]

questions = [
    {"question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?", "answer": "Maya Angelou", "difficulty": 2, "category": 4},
    {"question": "What boxer's original name is Cassius Clay?", "answer": "Muhammad Ali", "difficulty": 1, "category": 4},
    {"question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?", "answer": "Apollo 13", "difficulty": 4, "category": 5},
    {"question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?", "answer": "Tom Cruise", "difficulty": 4, "category": 5},
    {"question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?", "answer": "Edward Scissorhands", "difficulty": 3, "category": 5},
    {"question": "Which is the only team to play in every soccer World Cup tournament?", "answer": "Brazil", "difficulty": 3, "category": 6},
    {"question": "Which country won the first ever soccer World Cup in 1930?", "answer": "Uruguay", "difficulty": 4, "category": 6},
    {"question": "Who invented Peanut Butter?", "answer": "George Washington Carver", "difficulty": 2, "category": 4},
    {"question": "What is the largest lake in Africa?", "answer": "Lake Victoria", "difficulty": 2, "category": 3},
    {"question": "In which royal palace would you find the Hall of Mirrors?", "answer": "", "difficulty": 3, "category": 3},
    {"question": "The Taj Mahal is located in which Indian city?", "answer": "", "difficulty": 2, "category": 3},
    {"question": "Which Dutch graphic artist–initials M C was a creator of optical illusions?", "answer": "Escher", "difficulty": 1, "category": 2},
    {"question": "La Giaconda is better known as what?", "answer": "Mona Lisa", "difficulty": 3, "category": 2},
    {"question": "How many paintings did Van Gogh sell in his lifetime?", "answer": "One", "difficulty": 4, "category": 2},
    {"question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?", "answer": "Jackson Pollock", "difficulty": 2, "category": 2},
    {"question": "What is the heaviest organ in the human body?", "answer": "The Liver", "difficulty": 4, "category": 1},
    {"question": "Who discovered penicillin?", "answer": "Alexander Fleming", "difficulty": 3, "category": 1},
    {"question": "Hematology is a branch of medicine involving the study of what?", "answer": "Blood", "difficulty": 4, "category": 1},
    {"question": "Which dung beetle was worshipped by the ancient Egyptians?", "answer": "Scarab", "difficulty": 4, "category": 4}
]

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

            # for category in categories:
            #     obj = Category(type=category['type'])
            #     self.db.session.add(obj)
                
            #     self.db.session.commit()

            # for question in questions:
            #     obj = Question(question=question['question'], answer=question['answer'], category=question['category'], difficulty=question['difficulty'])
            #     self.db.session.add(obj)
            
            #     self.db.session.commit()

            #     self.db.session.close()
        
    
    def tearDown(self):
        """Executed after reach test"""
        # print("s;dfnk;sldkfn")
        # with self.app.app_context():
        #     self.db.drop_all(app=self.app)

    


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
        self.assertEqual(data['total_questions'], 3)
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
        res = self.client().delete('/questions/9') # use different id everytime
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==9).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 9)
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