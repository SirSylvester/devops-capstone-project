"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_account(self):
        """It should Read a single Account"""
    # First, create an account to be read
        account = self._create_accounts(1)[0]  # Create 1 account
    
    # Make a GET request to read the account by its ID
        resp = self.client.get(f"{BASE_URL}/{account.id}", content_type="application/json")
    
    # Assert that the response status code is HTTP 200 OK
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
    # Check that the returned account data is correct
        data = resp.get_json()
        self.assertEqual(data["name"], account.name)
        self.assertEqual(data["email"], account.email)
    
    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
    # Send a GET request to read an account that doesn't exist (e.g., ID 0)
        resp = self.client.get(f"{BASE_URL}/0")
    
    # Assert that the response status code is HTTP 404 NOT FOUND
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# ADD YOUR TEST CASES HERE ...
    def test_list_accounts(self):
        """It should List all Accounts"""
    # First, create some accounts to be listed
        self._create_accounts(3)  # Creates 3 accounts for testing
    
    # Make a GET request to the /accounts endpoint to list all accounts
        resp = self.client.get(f"{BASE_URL}", content_type="application/json")
    
    # Assert that the response status code is HTTP 200 OK
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
    # Get the list of accounts from the response
        data = resp.get_json()
    
    # Assert that the response contains 3 accounts
        self.assertEqual(len(data), 3)

    def test_update_account(self):
        """It should Update an existing Account"""
    # First, create an account that we will update
        account = self._create_accounts(1)[0]  # Create one account
    
    # Define new data to update the account
        updated_data = {
        "name": "Updated Name",
        "email": "updated.email@example.com",
        "address": "Updated Address",
        "phone_number": "1234567890"
        }
    
    # Make a PUT request to the /accounts/<id> endpoint to update the account
        resp = self.client.put(
        f"{BASE_URL}/{account.id}", json=updated_data, content_type="application/json"
        )   
    
    # Assert that the response status code is HTTP 200 OK
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
    # Get the updated account from the response
        data = resp.get_json()
    
    # Assert that the updated account data matches the provided data
        self.assertEqual(data["name"], "Updated Name")
        self.assertEqual(data["email"], "updated.email@example.com")
        self.assertEqual(data["address"], "Updated Address")
        self.assertEqual(data["phone_number"], "1234567890")
   
    def test_delete_account(self):
        """It should Delete an Account"""
    # First, create an account that we will delete
        account = self._create_accounts(1)[0]  # Create one account
    
    # Make a DELETE request to the /accounts/<id> endpoint to delete the account
        resp = self.client.delete(f"{BASE_URL}/{account.id}", content_type="application/json")
    
    # Assert that the response status code is HTTP 204 NO CONTENT
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    
    # Make a GET request to ensure the account is deleted
        resp = self.client.get(f"{BASE_URL}/{account.id}", content_type="application/json")
    
    # Assert that the response status code is HTTP 404 NOT FOUND
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
