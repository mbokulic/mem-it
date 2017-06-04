'''functions for parsing markdown files into a structure ready for ingestion by
the memory app
'''

import logging
import re
import json
import memit.markdown_parser.Terminal_node as tn


log = logging.getLogger('memit.markdown_parser')


def parse_markdown(path):
    with open(path, 'r') as file:
        md_string = file.read()

        x = _get_markdown_structure(md_string)
        return json.dumps(_get_markdown_structure(md_string),
                          default=lambda o: o.to_JSON())


def _find_highest_h(md_string):
    '''returns int representing the lowest heading found in the markdown string
    '''
    headings = re.findall(pattern='\n#+.*\n|^#+.*\n', string=md_string)
    counts = [len(re.search('#+', h).group()) for h in headings]
    return(min(counts))


def _get_markdown_structure(md_string):

    result = []
    for heading in split_str:
        title = _get_title(heading)
        content, subh = _split_content(heading)
        if tn.Code_chunk.test(content):
            content = tn.Code_chunk(content)
        else:
            content = None

        heading_data = {
            'title': title if title else None,
            'content': content if content else None,
            'children': _get_markdown_structure(subh) if subh else None
        }

        result.append(heading_data)

    return result


def _get_title(md_string):
    match = re.search('\\n', md_string)
    title = md_string[:match.start()] if match else ''
    return title


def _split_headings(md_string):
    '''splits a markdown string into sections of headings of the highest level
    found. Returns a list of strings representing each section. The newlines
    between sections are stripped.
    '''
    lvl = _find_highest_h(md_string)
    hashtags = '#' + '{' + str(lvl) + '}' + '[^#]*?\\n'
    regexpr = '|'.join(['\\n' + hashtags, '^' + hashtags])

    headings = re.findall(regexpr, md_string)
    content = re.split(regexpr, md_string)[1:]

    result = [re.sub('^\\n', '', h) + c for h, c in zip(headings, content)]

    return result


def _split_content(md_string):
    '''splits a markdown section string into content below a heading, and other
    headings. Input md_string has to start with a hashtag and the first line
    will be treated as the title.

    Returns a dictionary with title, content and rest. Leading and trailing
    whitespace characters will be removed from title and content, and leading
    from rest.
    '''
    if not re.match('#', md_string):
        raise ValueError('Error: input to _split_content() should start with a'
                         ' "#" heading!')

    split = md_string.split('\n', 1)
    title, content = split[0], split[1]
    title = re.sub('#+ *', '', title)

    result = {'title': title}

    regexp = '\\n#+'
    has_headings = re.search(regexp, content)
    if has_headings:
        result['content'] = content[:has_headings.start()]
        result['rest'] = content[has_headings.start():]
        result['rest'] = result['rest'].lstrip()
    else:
        result['content'] = content
        result['rest'] = None

    result['content'] = result['content'].strip()

    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', required=True)
    args = parser.parse_args()

    result = (parse_markdown(args.path))
    print(result)
