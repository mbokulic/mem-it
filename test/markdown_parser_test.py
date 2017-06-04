import unittest
import memit.markdown_parser.markdown_parser as parser

headings_1 = \
'''## heading 1
Heading 1 content. One row.

### subheading
Some text.

Other text one row apart.

## heading 2

### subheading 1
Text
'''



class Split_headings_test(unittest.TestCase):

    def test_1(self):

        result = parser._split_headings(headings_1)
        truth = [
            '## heading 1\nHeading 1 content. One row.\n\n### subheading\nSome'
            ' text.\n\nOther text one row apart.\n',
            '## heading 2\n\n### subheading 1\nText\n'
        ]
        self.assertEqual(result, truth)


test1 = ('## heading 1\nHeading 1 content. One row.\n\n### subheading\nSome'
         ' text.\n\nOther text one row apart.\n')


class Split_content_test(unittest.TestCase):

    def test_split(self):
        result = parser._split_content(test1)
        truth = {
            'title': 'heading 1',
            'content': 'Heading 1 content. One row.',
            'rest': '### subheading\nSome text.\n\nOther text one row apart.\n'
        }
        self.assertEqual(result, truth)
