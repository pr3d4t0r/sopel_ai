# See:  https://raw.githubusercontent.com/pr3d4t0r/m0toko/master/LICENSE.txt


class M0tokoError(Exception):
    def __init__(self, exceptionInfo):
        super().__init__(exceptionInfo)

