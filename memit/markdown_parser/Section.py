'''Class for parsing markdown files into a structure ready for ingestion by
the memory app
'''

import logging
import re
import os
import json


log = logging.getLogger('memit.markdown_parser')


class Section():

    def __init__(self, title, content, children):
        self.title = title
        self.content = content
        self.children = children

    def to_JSON(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        '''returns a dict representation of the section. Will call to_dict()
        recursively for all children
        '''
        if self.children:
            children = [ch.to_dict() for ch in self.children]
        else:
            children = None
        dict_repr = {
            'title': self.title,
            'content': self.content,
            'children': children
        }
        return dict_repr

    @classmethod
    def from_file(cls, filepath):
        '''creates a Section from a markdown file. Will recursively go through
        sections inside the file and create Sections of them.
        '''
        title = os.path.splitext(
            os.path.basename(filepath))[0]
        with open(filepath, 'r') as file:
            md_string = file.read()
        content, rest = cls._split_content(md_string)
        children = cls._get_children(rest)
        return cls(title, content, children)

    @classmethod
    def from_markdown_header(cls, md_string):
        '''creates a Section from a markdown string. The string should start
        with a header, otherwise use from_file()
        '''
        title, rest = cls._split_title(md_string)
        content, rest = cls._split_content(rest)
        children = cls._get_children(rest)
        return cls(title, content, children)

    @classmethod
    def _get_children(cls, md_string):
        if md_string:
            children = []
            subsections = cls._split_sections(md_string)
            for idx in range(len(subsections)):
                child = cls.from_markdown_header(subsections[idx])
                children.append(child)
        else:
            children = None

        return children

    @staticmethod
    def _split_content(md_string):
        '''splits a markdown section string into content below a heading, and
        other headings. Input md_string has to start with a hashtag and the
        first line will be treated as the title.

        Returns a dictionary with title, content and rest. Leading and trailing
        whitespace characters will be removed from title and content, and
        leading from rest.
        '''
        regexp = '^#+|\\n#+'
        has_headings = re.search(regexp, md_string)
        if has_headings:
            content = md_string[:has_headings.start()]
            rest = md_string[has_headings.start():]
            rest = rest.lstrip()
        else:
            content = md_string
            rest = None

        content = content.strip()

        return content, rest

    @classmethod
    def _split_sections(cls, md_string):
        '''splits a markdown string into sections of headings of the highest
        level found. Returns a list of strings representing each section.
        The newlines between sections are stripped.
        '''
        lvl = cls._find_highest_h(md_string)
        hashtags = '#' + '{' + str(lvl) + '}' + '[^#]*?\\n'
        regexpr = '|'.join(['\\n' + hashtags, '^' + hashtags])

        headings = re.findall(regexpr, md_string)
        content = re.split(regexpr, md_string)[1:]

        result = [re.sub('^\\n', '', h) + c for h, c in zip(headings, content)]

        return result

    @staticmethod
    def _split_title(md_string):
        if not re.match('#', md_string):
            raise ValueError('Error: input string should start '
                             'with a "#" heading!')

        split = md_string.split('\n', 1)
        title, rest = split[0], split[1]
        title = re.sub('#+ *', '', title)

        return title, rest

    @staticmethod
    def _find_highest_h(md_string):
        '''returns int representing the lowest heading found in the markdown
        string
        '''
        headings = re.findall(pattern='\n#+.*\n|^#+.*\n', string=md_string)
        counts = [len(re.search('#+', h).group()) for h in headings]
        return(min(counts))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', required=True)
    args = parser.parse_args()

    result = Section.from_file(args.path)
    result = result.to_JSON()
    print(result)
