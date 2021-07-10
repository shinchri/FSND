import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, origins=["*"])
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def retreive_all_categories():

    categories = Category.query.order_by(Category.id).all()
    return jsonify({
      "categories": {category.id: category.type for category in categories}
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def retreive_all_questios():
    # page number is provided

    questions = Question.query.order_by(Question.id).all()

    question_list = paginate_questions(request, questions)

    if len(question_list) == 0:
      abort(404)
    else:
      categories = Category.query.order_by(Category.id).all()
      return jsonify({
        "questions": question_list,
        "total_questions": len(Question.query.all()),
        "current_category": None,
        "categories": {category.id: category.type for category in categories}
      })



  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        "success": True,
        "deleted": question_id
      })
    except Exception:
      abort(422)    

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  # implementing both posting new question, and searching for questions
  @app.route('/questions', methods=['POST'])
  def create_or_search_question():
    
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)
    search_term = body.get('searchTerm', None)

    try:
      if search_term:
        selected_questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()

        # pagination for search doesn't work right on React
        #question_list = paginate_questions(request, selected_questions)


        return jsonify({
          'questions': [question.format() for question in selected_questions],
          'total_questions': len(selected_questions),
          'current_category': None
        })
      else:
        question = Question(new_question, new_answer, new_category, new_difficulty)
        question.insert()


        return jsonify({
          'success': True
        })
    except Exception:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  # code provided above

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def retreive_questions_by_category(category_id):
    try:

      questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()

      if len(questions) == 0:
        abort(404)

      # pagination doesn't work...
      # the erro seems to be from the front end
      #question_list = paginate_questions(request, questions)
      
      return jsonify({
        'questions': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': category_id
      })

    except Exception:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def retreive_quiz_questions():
    body = request.get_json()
    previous_questions = body.get('previous_questions', [])
    quiz_category = body.get('quiz_category', None)
    try:
      if not quiz_category:
        abort(422)
      
      category_chosen = quiz_category['id']
      
      quiz_questions = None
      if category_chosen == 0:
        quiz_questions = Question.query.order_by(Question.id).all()
      else:
        quiz_questions = Question.query.filter_by(category=int(category_chosen)).order_by(Question.id).all()
   
      if len(quiz_questions) == 0:
        abort(404)

      available_questions = []
      
      for question in quiz_questions:
        if question.id not in previous_questions:
          available_questions.append(question.format())

      if len(available_questions) != 0:
        next_question = random.choice(available_questions)
        
        return jsonify({
          'success': True,
          'question': next_question
        })
      else:
        return jsonify({
          'success': True,
          'question': None
        })
    except Exception:
      abort(422)
    


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400) # happens when url typo, no variable/data provided
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400
  
  @app.errorhandler(404) # when resource is not found by id
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(405) # when wrong method was used
  def not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
    }), 405

  @app.errorhandler(422) # understandable content type, correct syntax, but unable to processed
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
    }), 422

  
  return app

    