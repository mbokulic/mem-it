'''A chunk is a class that takes markdown section content as input. From this
content it extracts a "chunk" of text that is relevant for some purpose.

Chunks exclude one another
'''

import re
import abc


class Chunk(abc.ABC):

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def to_JSON(self):
        pass

    @classmethod
    @abc.abstractmethod
    def test(cls, string):
        pass


class Code_chunk(Chunk):

    _regexp = '\\n```[A-z]+\\n.+\\n```\\n'

    def __init__(self, string):
        self.string = string
        self.code = self._extract_code(string)

    def __str__(self):
        return self.string

    def _extract_code(self, string):
        code = re.search(self._regexp, string, re.DOTALL)
        if code:
            code = code.group()
            code = re.sub('```([A-z]+)?\\n', '', code)
        else:
            code = ''
        return code

    @classmethod  # why do I need to repeat this?
    def test(cls, string):
        match = re.search(cls._regexp, string, re.DOTALL)
        return True if match else False

    def to_JSON(self):
        return {
            'code': self.code,
            'syntax': 'python'
        }
