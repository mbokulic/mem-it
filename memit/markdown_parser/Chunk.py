'''A chunk is a class that takes markdown section content as input. From this
content it extracts a "chunk" of text that is relevant for some purpose.

Chunks exclude one another
'''

import re
import abc


class Chunk(abc.ABC):

    @abc.abstractmethod
    def to_JSON(self):
        pass

    @abc.abstractmethod
    def get_content(self):
        pass

    @abc.abstractmethod
    def get_prompt(self):
        pass

    @abc.abstractmethod
    def get_title(self):
        pass


class Code_chunk(Chunk):

    _regexp = '```([A-z]+)?\\n.+\\n```'
    _prompt_break = '```'

    def __init__(self, content_string, title):
        self._extract(content_string)
        self.title = title

    def get_content(self):
        return self.code

    def get_syntax(self):
        return self.syntax

    def get_title(self):
        return self.title

    def get_prompt(self):
        return self.prompt or '--no prompt for this chunk--'

    def _extract(self, string):
        code = re.search(self._regexp, string, re.DOTALL)
        prompt = ''
        if code:
            code = code.group()
            syntax = re.search('```([A-z]+)?\\n', code)
            self.syntax = syntax.group(1) or None
            code = re.sub('```([A-z]+)?\\n', '', code)
            code = re.sub('```', '', code)
            code = code.strip()

            prompt_break = re.search(self._prompt_break, string)
            prompt = string[:prompt_break.start()].strip()

        self.prompt = prompt or None
        self.code = code or None

    @classmethod  # why do I need to repeat this?
    def test(cls, string):
        match = re.search(cls._regexp, string, re.DOTALL)
        return True if match else False

    def to_JSON(self):
        return {
            'code': self.code,
            'syntax': 'python'
        }


def chunk_factory(string, title, chunk_type):

    if chunk_type == 'code':
        return Code_chunk(string, title)
    else:
        raise ValueError('unknown chunk type!')
