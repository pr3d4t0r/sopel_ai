# See:  https://raw.githubusercontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt


from sopel_ai.errors import SopelAIError


# +++ tests +++

def test_SopelAIError():
    message = 'This is an error message'
    e = SopelAIError(message)

    try:
        raise e
    except Exception as x:
        assert str(x) == message

