#!/usr/bin/python3
"""
Contains the TestDBStorageDocs and TestDBStorage classes
"""

from datetime import datetime
import inspect
from models import storage, storage_t
from models.engine import db_storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
import MySQLdb
import os
import pep8
import sqlalchemy
import unittest
DBStorage = db_storage.DBStorage
classes = {"Amenity": Amenity, "City": City, "Place": Place,
           "Review": Review, "State": State, "User": User}


class TestDBStorageDocs(unittest.TestCase):
    """Tests to check the documentation and style of DBStorage class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.dbs_f = inspect.getmembers(DBStorage, inspect.isfunction)

    def test_pep8_conformance_db_storage(self):
        """Test that models/engine/db_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/engine/db_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_db_storage(self):
        """Test tests/test_models/test_db_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_models/test_engine/\
test_db_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_db_storage_module_docstring(self):
        """Test for the db_storage.py module docstring"""
        self.assertIsNot(db_storage.__doc__, None,
                         "db_storage.py needs a docstring")
        self.assertTrue(len(db_storage.__doc__) >= 1,
                        "db_storage.py needs a docstring")

    def test_db_storage_class_docstring(self):
        """Test for the DBStorage class docstring"""
        self.assertIsNot(DBStorage.__doc__, None,
                         "DBStorage class needs a docstring")
        self.assertTrue(len(DBStorage.__doc__) >= 1,
                        "DBStorage class needs a docstring")

    def test_dbs_func_docstrings(self):
        """Test for the presence of docstrings in DBStorage methods"""
        for func in self.dbs_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


@unittest.skipUnless(storage_t == "db", "Not testing database storage")
class TestDBStorage(unittest.TestCase):
    """Test DBStorage methods"""

    @staticmethod
    def __create_db_connection():
        """create a new database connection"""
        options = {
            "host": os.environ.get("HBNB_MYSQL_HOST"),
            "user": os.environ.get("HBNB_MYSQL_USER"),
            "password": os.environ.get("HBNB_MYSQL_PWD"),
            "database": os.environ.get("HBNB_MYSQL_DB"),
        }
        return MySQLdb.connect(**options)

    @staticmethod
    def __count(tablename):
        """Return the number of items in the given table

        Args:
            tablename (str): table name.
        """
        conn = TestDBStorage.__create_db_connection()
        cur = conn.cursor()
        # Using format. Not safe.
        cur.execute("""SELECT * FROM {}""".format(tablename))
        count = len(cur.fetchall())
        cur.close()
        conn.close()

        return count

    def test_storage_type(self):
        """Test that storage is an instance of DBStorage"""
        self.assertTrue(type(storage), DBStorage)

    def test_new_and_save(self):
        """Test that the new and save methods add a new object
        to the database"""

        count1 = self.__count("users")
        new_user = User(email="DBStorage", password="1234")
        storage.new(new_user)
        storage.save()
        count2 = self.__count("users")
        self.assertTrue(count2 - count1, 1)

    def test_all_without_class(self):
        """Test that the all method returns dictionary of all objects"""

        objs_dict = storage.all()
        for key, value in objs_dict.items():
            with self.subTest(key=key):
                self.assertTrue('.' in key)
                self.assertEqual(key.split('.')[0], value.__class__.__name__)
                self.assertEqual(key.split('.')[1], value.id)

    def test_all_with_class(self):
        """Test that all returns dictionary of objects in specified class"""

        for _ in range(5):
            State(name="DBStorage test all").save()

        user_objs = storage.all(User)
        for key, value in user_objs.items():
            with self.subTest(key=key):
                self.assertTrue('.' in key)
                self.assertEqual(key.split('.')[0], "User")
                self.assertEqual(key.split('.')[1], value.id)

    def test_delete(self):
        """Test that delete removes the specified object from the database"""

        new_state = State(name="DBStorage test delete")
        new_state.save()

        count1 = self.__count("states")
        storage.delete(new_state)
        storage.save()
        count2 = self.__count("states")

        self.assertEqual(count1 - count2, 1)

    def test_delete_with_not_added_obj(self):
        """Test that delete raises an exception if object is not
        persisted in the session"""

        new_state = State(name="DBStorage test delete")

        with self.assertRaises(sqlalchemy.exc.InvalidRequestError):
            storage.delete(new_state)

    def test_delete_cascades(self):
        """Test that deleting a parent causes children to also be deleted"""

        new_state = State(name="DBStorage test delete cascade")
        new_state.save()
        City(
            name="DBStorage test delete cascade",
            state_id=new_state.id
        ).save()

        city_count1 = self.__count("cities")
        state_count1 = self.__count("states")

        storage.delete(new_state)
        storage.save()

        city_count2 = self.__count("cities")
        state_count2 = self.__count("states")

        self.assertEqual(city_count1 - city_count2, 1)
        self.assertEqual(state_count1 - state_count2, 1)

    def test_get(self):
        """Test the get method of DBStorage"""

        new_state = State(name="DBStorage test get")
        new_state.save()

        state = storage.get(State, new_state.id)

        self.assertEqual(state, new_state)

        none_state = storage.get(State, "1234")

        self.assertFalse(none_state)

    def test_count(self):
        """Test the count method of DBStorage"""

        count1 = self.__count("states")
        count2 = storage.count(State)

        self.assertEqual(count1, count2)

        State(name="DBStorage test count").save()

        count3 = self.__count("states")
        count4 = storage.count(State)

        self.assertEqual(count3, count4)
        self.assertEqual(count4 - 1, count2)
