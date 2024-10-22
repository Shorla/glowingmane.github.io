import pytest
from app import app, db, cache
from app import Users
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'


    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"calculator" in response.data

def test_blog(client):
    response = client.get('/blog')
    assert response.status_code == 200
    assert b"Blog" in response.data

def test_login(client):
    """Test the login route."""
    # Test the GET request to the login page
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data  # Assuming the word "Login" is on the page

    # Test POST request for login with valid credentials
    with app.app_context():
        # Add a user to the database (for testing purposes)
        user = Users(username="testuser", hash=generate_password_hash("testpassword"), firstname="test", lastname="user")
        db.session.add(user)
        db.session.commit()

    # Test POST with valid data
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200


#@pytest.fixture
#def redis_client():
#    """Fixture to provide a Redis client."""
#    redis_url = 'redis://default:CIGkdmqKpI6NLMf7o4znqDkASfithEv0@redis-19111.c83.us-east-1-2.ec2.redns.redis-cloud.com:19111'
#    return redis.StrictRedis.from_url(redis_url)

def test_mysql_connection(client):
    """Test the MySQL connector by adding and retrieving a user."""
    with app.app_context():
        # Create a new user
        new_user = Users(username="testuser", hash=generate_password_hash("testpassword"), firstname="test", lastname="user")
        db.session.add(new_user)
        db.session.commit()

        # Retrieve the user from the database
        retrieved_user = Users.query.filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.firstname == "test"

def test_cache_replication(client):
    # Simulate a GET request to the calculator page
    response = client.get('/calculator')
    assert response.status_code == 200

    # Simulate form data for the POST request
    form_data = {
        'firstmonth': '2023-01-01',
        'f-measurement': '10',
        'secondmonth': '2023-02-01',
        's-measurement': '12',
        'thirdmonth': '2023-03-01',
        't-measurement': '14',
        'fourthmonth': '2023-04-01',
        'fo-measurement': '15',
    }

    # Simulate the POST request with form data
    response = client.post('/calculator', data=form_data)
    assert response.status_code == 302  # Should redirect to the login page

    # Simulate login by creating a test user and setting session data
    test_user = Users(username='testuser', hash=generate_password_hash('password123'), firstname="test", lastname="user")
    db.session.add(test_user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id  # Simulate user ID after login

    # Now simulate a GET request to the calculator page after login
    response = client.get('/calculator')

    # Verify if the form is populated with cached data
    assert b'10' in response.data  # Check if the first month measurement is in the response
    assert b'12' in response.data  # Check if the second month measurement is in the response
    assert b'14' in response.data  # Check if the third month measurement is in the response
    assert b'15' in response.data  # Check if the fourth month measurement is in the response

