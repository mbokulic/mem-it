import json
import re


def parse_markdown(path):
    with open(path, 'r') as file:
        md_string = file.read()

        x = _get_markdown_structure(md_string)
        return json.dumps(x, default=lambda o: o.to_JSON())


def _get_markdown_structure(md_string):

    result = []
    sections = _split_sections(md_string)

    for section in sections:
        section_content = _split_content(section)

        section_data = {
            'title': section_content['title'],
            'content': section_content['content'],
            'children': _get_markdown_structure(section_content['rest']) if
            section_content['rest'] else None
        }

        result.append(section_data)

    return result


def _find_highest_h(md_string):
    '''returns int representing the lowest heading found in the markdown string
    '''
    headings = re.findall(pattern='\n#+.*\n|^#+.*\n', string=md_string)
    counts = [len(re.search('#+', h).group()) for h in headings]
    return(min(counts))


def _split_sections(md_string):
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
