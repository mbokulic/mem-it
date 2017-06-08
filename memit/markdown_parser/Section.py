'''Class for parsing markdown files into a structure ready for ingestion by
the memory app
'''

import logging
import re
import os
import json


log = logging.getLogger('memit.markdown_parser')


class Section():

    VALID_EXT = ('.md', '.mdown', '.txt')

    def __init__(self, title, content, children):
        self.title = title
        self.content = content
        self.children = children

    def get_content(self):
        return self.content

    def get_title(self):
        return self.title

    def get_children(self):
        return self.children

    def to_JSON(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        '''returns a dict representation of the section. Will call to_dict()
        recursively for all children
        '''
        if self.children:
            children = [child.to_dict() for child in self.children]
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
    def from_dir(cls, path):
        '''creates a Section from a directory.
        '''
        title = os.path.basename(re.sub('/$', '', path))
        content = ''

        children = []
        for child in os.listdir(path):
            # ignore hidden files
            if child.startswith('.'):
                continue
            child_path = os.path.join(path, child)
            if os.path.isfile(child_path) and \
                    child_path.endswith(cls.VALID_EXT):
                if cls.file_is_markdown(child_path):
                    children.append(cls.from_file(child_path))
            elif os.path.isdir(child_path):
                children.append(cls.from_dir(child_path))
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
        headings = re.findall(pattern='\n#+.*\n|^#+.*\n|^#+.*$',
                              string=md_string)
        counts = [len(re.search('#+', h).group()) for h in headings]
        return(min(counts))

    @staticmethod
    def file_is_markdown(path):
        is_markdown = False
        with open(path, 'r') as file:
            for line in file:
                if line.startswith('#'):
                    is_markdown = True
                    break
        return is_markdown


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--filepath', '-f')
    group.add_argument('--dir', '-d')
    args = parser.parse_args()

    if args.filepath:
        result = Section.from_file(args.filepath)
    elif args.dir:
        result = Section.from_dir(args.dir)

    result = result.to_JSON()
    print(result)
