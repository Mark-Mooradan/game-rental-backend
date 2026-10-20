import os, tempfile, pytest, logging, unittest
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import create_db, db
from App.models import User, Staff, Customer, Game, Listing, Rental, Payment
from App.controllers import (
    create_customer,
    create_game,
    get_customer,
    create_staff,
    get_all_users_json,
    authenticate,
    get_staff,
    get_game,
    get_rental,
    get_listing,
    update_staff
)

app = create_app({"SQLALCHEMY_DATABASE_URI":'sqlite:///test_database.db', "TESTING":True, "DEBUG":True})

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = Staff("bob", "bobpass")
        assert user.username == "bob"

    def test_toJSON(self):
        user = Staff("bob", "bobpass")
        user_json = user.toJSON()
        self.assertDictEqual(user_json, {"id":None, "username":"bob", "type": 'staff'})
    

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    create_db(app)
    yield app.test_client()
    db.session.remove()
    db.drop_all()


def test_authenticate():
    staff = create_staff("staff_auth", "password123")
    assert authenticate("staff_auth", "password123") is not None

def test_create_game():
    game = create_game("Mario Kart", "NSW", "Racing", "E", "url")
    assert game.title == "Mario Kart"

def test_create_user():
    customer = create_customer("cust_test", "password123")
    assert customer.username == "cust_test"

def test_create_staff():
    staff = create_staff("staff_test", "password123")
    assert staff.username == "staff_test"

def test_staff_create_listing():
    staff = create_staff("staff_list", "pass")
    customer = create_customer("cust_list", "pass")
    game = create_game("Zelda", "NSW", "Adventure", "E", "url")
    
    listing = staff.list_game(customer, game, "good", 50.0)
    
    assert listing.gameId == game.gameId
    assert listing.ownerId == customer.id

def test_staff_confirm_rental():
    staff = create_staff("staff_rent", "pass")
    customer = create_customer("cust_rent", "pass")
    game = create_game("Halo", "XBOX", "FPS", "M", "url")
    
    listing = staff.list_game(customer, game, "good", 40.0)
    rental = staff.confirm_rental(customer, listing)
    
    assert rental is not None
    assert rental.listingId == listing.listingId
    
    # Changed 'availability' to 'status' based on the Tutorial 5 schema
    updated_listing = Listing.query.get(listing.listingId)
    assert updated_listing.status.lower() == "rented"

def test_staff_confirm_return():
    staff = create_staff("staff_ret", "pass")
    customer = create_customer("cust_ret", "pass")
    game = create_game("FIFA", "PS5", "Sports", "E", "url")
    
    listing = staff.list_game(customer, game, "fair", 30.0)
    rental = staff.confirm_rental(customer, listing)
    
    staff.confirm_return(rental)
    
    # Changed 'returnDate' to 'return_date' as the error suggested
    updated_rental = Rental.query.get(rental.rentalId)
    assert updated_rental.return_date is not None
    
    # Changed 'availability' to 'status'
    updated_listing = Listing.query.get(listing.listingId)
    assert updated_listing.status.lower() == "available"