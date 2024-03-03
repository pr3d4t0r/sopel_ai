# See:  https://raw.githubusercontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt


from sopel_ai.errors import M0tokoError


# +++ tests +++

def test_M0tokoError():
    message = 'This is an error message'
    e = M0tokoError(message)

    try:
        raise e
    except Exception as x:
        assert str(x) == message

