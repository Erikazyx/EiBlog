from app.admin import test

@test.route('/')
def ello():
    return 'ello bibo!'