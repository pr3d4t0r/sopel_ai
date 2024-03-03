# See:  https://raw.githubusercontent.com/pr3d4t0r/m0toko/master/LICENSE.txt


from sopel_motoko.errors import M0tokoError


# +++ tests +++

def test_M0tokoError():
    message = 'This is an error message'
    e = M0tokoError(message)

    try:
        raise e
    except Exception as x:
        assert str(x) == message

