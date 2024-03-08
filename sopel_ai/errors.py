# See:  https://raw.githubusercontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt


class SopelAIError(Exception):
    def __init__(self, exceptionInfo):
        super().__init__(exceptionInfo)

