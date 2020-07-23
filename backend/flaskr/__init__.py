import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [Question.format() for Question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):

  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={"/": {"origins": '*'}})

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
  @app.route('/categories')
  def get_all_categories():
    categories = Category.query.order_by(Category.id).all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type

    if (len(categories) == 0):
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories_dict,
      'total_categories': len(categories)
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
  @app.route('/questions')
  def get_paginated_questions():
    all_questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, all_questions)

    categories = Category.query.order_by(Category.id).all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(all_questions),
      "categories": categories_dict,
      "total_categories": len(categories)
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    
    target_question = Question.query.filter(Question.id == question_id).one_or_none()

    if target_question is None:
      abort(422)

    try:
      target_question.delete()

      questions_list = [question.format() for question in Question.query.order_by(Question.id).all()]

      return jsonify({
        "success": True,
        "deleted_id": question_id,
        "questions": questions_list,
        "total_questions": len(questions_list)
      })
    except:
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
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    if body and 'searchTerm' in body:
      search_term = body.get('searchTerm', '')

      if search_term == '':
        abort(400)

      try:
        search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        if len(search_results) == 0:
            abort(404)

        paginated_questions = paginate_questions(request, search_results)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(Question.query.all())
        })

      except:
          abort(404)

    else:
      if not body or (body.get('question') is None or body.get('answer') is None or 
                        body.get('category') is None or body.get('difficulty') is None):
        abort(422)
      
      try:
        question = Question(question=body.get('question'), answer=body.get('answer'), category=body.get('category'), difficulty=body.get('difficulty'))
        question.insert()

        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        return jsonify({
          'success': True,
          'created_id': question.id,
          'created_question': question.question,
          'questions': current_questions,
          'total_questions': len(questions)
        })

      except: 
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
  # Post '/questions' with searchTerm in json body.

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_based_on_category(category_id):
    category = Category.query.filter(Category.id == category_id).one_or_none()

    if category is None:
      abort(404)
    
    questions = Question.query.filter(Question.category == category_id).all()

    if questions is None:
      abort(404)

    current_questions = paginate_questions(request, questions)

    return jsonify({
      "success": True,
      "current_category": category.type,
      "questions": current_questions,
      "total_questions": len(Question.query.all())
    })


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
  def quizzes():
    body = request.get_json()

    if not body or'quiz_category' not in body or 'previous_questions' not in body:
      abort(400)

    try:
      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

      if category['type'] == 'click':
        questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      else:
        questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()

      questions_len = len(questions)
      random_index = random.randrange(0, questions_len)
      
      new_question = questions[random_index].format() if questions_len > 0 else None

      return jsonify({
        'success': True,
        'question': new_question
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
      }), 422
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "internal server error"
    }), 500
  
  return app