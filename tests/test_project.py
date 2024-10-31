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

        # Clean up by removing data from Users table after each test
        Users.query.delete()
        db.session.commit()
        db.session.rollback()
        db.session.remove()

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
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

    # Add a test user to the database
    with app.app_context():
        user = Users(username="testuser", hash=generate_password_hash("testpassword"), firstname="test", lastname="user")
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_mysql_connection(client):
    """Test the MySQL connector by adding and retrieving a user."""
    with app.app_context():
        new_user = Users(username="testuser", hash=generate_password_hash("testpassword"), firstname="test", lastname="user")
        db.session.add(new_user)
        db.session.commit()

        retrieved_user = Users.query.filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.firstname == "test"

def test_cache_replication(client):
    response = client.get('/calculator')
    assert response.status_code == 200

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

    response = client.post('/calculator', data=form_data)
    assert response.status_code == 302  # Redirect to login page

    test_user = Users(username='testuser', hash=generate_password_hash('password123'), firstname="test", lastname="user")
    db.session.add(test_user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = test_user.user_id  # Simulate user login

    response = client.get('/calculator')

    assert b'10' in response.data
    assert b'12' in response.data
    assert b'14' in response.data
    assert b'15' in response.data
