from app import Users

def test_new_user():
    user = Users( 'assurance', 'Iamgreat')
    assert user.username == 'assurance'
    assert user.hash != 'Iamgreat'