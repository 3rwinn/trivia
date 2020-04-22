import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'superadmin', 'localhost:5432',
                                                             self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "is the earth flat?",
            "answer": "no",
            "difficulty": 3,
            "category": 3
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

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['total_questions'], len(Question.query.all()))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "ressource not found")

    def test_delete_specific_question(self):
        question = Question.query.options(load_only('id')).first()
        question_id = question.id

        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data["deleted"], question_id)
        self.assertEqual(question, None)

    def test_create_new_question(self):
        res = self.client().post('/questions',
                                 json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_questions_from_search_term(self):
        search_term = 'Which American artist'
        res = self.client().post('/questions/search', json={'search_term': search_term})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_questions_by_category(self):
        category = Category.query.options(load_only('id')).first()
        cat_id = category.id

        res = self.client().get('/categories/{}/questions'.format(cat_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_quizz_question_by_category(self):
        category = Category.query.first()
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': category.format()})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
