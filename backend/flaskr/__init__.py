import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    def paginated_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    # CORS Header
    CORS(app, ressources={r"*": {"origins": "*"}})

    # after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Get categories
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {category.id: category.type for category in categories}

        if len(categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": formatted_categories
        })

    # Get questions
    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        questions = paginated_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {category.id: category.type for category in categories}

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions,
            'categories': formatted_categories,
            'total_questions': len(Question.query.all()),
            'current_category': None
        })

    # Delete question by id
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
        except:
            abort(422)

    # Create new question
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category,
                                difficulty=new_difficulty)
            question.insert()

            return jsonify({
                'success': True
            })

        except:
            abort(422)

    # Search question
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search_term = body.get('search_term', '')
        look_for = '%{0}%'.format(search_term)

        search_result = Question.query.filter(Question.question.ilike(look_for))

        questions = [question.format() for question in search_result]

        if len(questions) == 0:
          abort(404)

        return jsonify({
            "success": True,
            "questions": questions
        })



    # Get questions by category id
    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).all()

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'current_category': category_id
        })

    # Get quizzes by category
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()

        previous_questions = body.get('previous_questions', None)
        category = body.get('quiz_category', None)

        if category is None or previous_questions is None:
            abort(422)

        if category['id'] == 0:
            question = Question.query.filter(Question.id.notin_(previous_questions)).first()
        else:
            question = Question.query.filter(Question.category == category['id'],
                                             Question.id.notin_(previous_questions)).first()

        return jsonify({
            "success": True,
            "question": question.format() if question is not None else None
        })

    # Handle errors

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "ressource not found"
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

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    return app
