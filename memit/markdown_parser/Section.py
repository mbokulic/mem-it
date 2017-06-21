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

    def __init__(self, title, content, children, level):
        self.title = title
        self.content = content
        self.children = children
        self.level = level
        self.id = None

    def get_content(self):
        return self.content

    def get_title(self):
        return self.title

    def get_children(self):
        return self.children

    def get_id(self):
        '''will raise an error if the id is not set. This is to prevent errors
        when you would expect an id but not have one.
        '''
        if self.id is not None:
            return self.id
        else:
            raise ValueError('If you require the id, set it first!')

    def get_level(self):
        return self.level

    def __set_id(self, id):
        self.id = id

    def to_JSON(self):
        return json.dumps(self.to_dict_recursive())

    def to_dict_recursive(self):
        '''returns a dict representation of the section. Will call the function
        recursively for all children
        '''
        if self.children:
            children = [child.to_dict_recursive() for child in self.children]
        else:
            children = None
        dict_repr = {
            'title': self.title,
            'content': self.content,
            'level': self.level,
            'children': children
        }
        return dict_repr

    def to_dict(self):
        '''returns a dict representation of the section
        '''
        result = {
            'title': self.title,
            'content': self.content,
            'level': self.level
        }
        if self.id is not None:
            result['id'] = self.id

        return result

    def get_graph_repr(self):
        '''returns a graph representation of the section and its children, a
        dictionary with
          - nodes: list of all sections, including this one
          - links: list of
        TO DO: setting the id using the __set_id() method seems hacky and I
        feel that the id should be set on initialisation. But since I am only
        using it for links, it is enough for now.
        '''
        nodes = self.get_all_nodes()
        for idx in range(len(nodes)):
            nodes[idx].__set_id(idx)

        links = []
        for node in nodes:
            node_links = node.get_links()
            if node_links:
                links.extend(node_links)

        result = {
            'nodes': [node.to_dict() for node in nodes],
            'links': links
        }
        return result

    def get_all_nodes(self):
        nodes = []

        def append_nodes(node):
            nodes.append(node)
            children = node.get_children()
            if children:
                for child in children:
                    append_nodes(child)
        append_nodes(self)
        return nodes

    def get_links(self):
        children = self.get_children()
        links = None
        if children:
            id = self.get_id()
            level = self.get_level()
            links = [{
                'source': id,
                'target': child.get_id(),
                'source_level': level,
                'target_level': child.get_level()
            } for child in children]

        return links

    @classmethod
    def from_file(cls, filepath, level=1):
        '''creates a Section from a markdown file. Will recursively go through
        sections inside the file and create Sections of them.
        '''
        title = os.path.splitext(
            os.path.basename(filepath))[0]
        with open(filepath, 'r') as file:
            md_string = file.read()
        content, rest = cls._split_content(md_string)
        child_level = level + 1
        children = cls._get_children(rest, child_level)
        return cls(title, content, children, level)

    @classmethod
    def from_markdown_header(cls, md_string, level):
        '''creates a Section from a markdown string. The string should start
        with a header, otherwise use from_file()
        '''
        title, rest = cls._split_title(md_string)
        content, rest = cls._split_content(rest)
        child_level = level + 1
        children = cls._get_children(rest, child_level)
        return cls(title, content, children, level)

    @classmethod
    def from_dir(cls, path, level=1):
        '''creates a Section from a directory.
        '''
        title = os.path.basename(re.sub('/$', '', path))
        content = ''

        children = []
        child_level = level + 1
        for child in os.listdir(path):
            # ignore hidden files
            if child.startswith('.'):
                continue
            child_path = os.path.join(path, child)
            if os.path.isfile(child_path) and \
                    child_path.endswith(cls.VALID_EXT):
                if cls.file_is_markdown(child_path):
                    children.append(cls.from_file(child_path, child_level))
            elif os.path.isdir(child_path):
                children.append(cls.from_dir(child_path, child_level))
        return cls(title, content, children, level)

    @classmethod
    def _get_children(cls, md_string, level):
        if md_string:
            children = []
            subsections = cls._split_sections(md_string)
            for idx in range(len(subsections)):
                child = cls.from_markdown_header(subsections[idx], level)
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

    path = parser.add_mutually_exclusive_group(required=True)
    path.add_argument('--filepath', '-f')
    path.add_argument('--dir', '-d')

    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument('--json', action='store_true')
    output.add_argument('--graph', action='store_true')

    args = parser.parse_args()

    if args.filepath:
        result = Section.from_file(args.filepath)
    elif args.dir:
        result = Section.from_dir(args.dir)

    if args.json:
        result = result.to_JSON()
    if args.graph:
        graph = result.get_graph_repr()
        result = json.dumps(graph, default=lambda x: x.to_dict())

    print(result)
