import unittest
import memit.markdown_parser.Chunk as ch

single_row = '''This is the prompt
```r
table = data.frame()
```'''

two_rows = '''```python
table = data.frame()
sort(table)
```'''

no_syntax = '''This is the prompt
That has two rows

```
table = data.frame()
sort(table)
```'''


class Code_chunk_test(unittest.TestCase):

    def test_single_row(self):
        chunk = ch.Code_chunk(single_row, 'test')
        self.assertEqual(chunk.get_content(), 'table = data.frame()')
        self.assertEqual(chunk.get_prompt(), 'This is the prompt')
        self.assertEqual(chunk.get_syntax(), 'r')
        self.assertEqual(chunk.get_title(), 'test')

    def test_two_rows(self):
        chunk = ch.Code_chunk(two_rows, 'test')
        self.assertEqual(chunk.get_content(),
                         'table = data.frame()\nsort(table)')
        self.assertEqual(chunk.get_prompt(), None)
        self.assertEqual(chunk.get_syntax(), 'python')

    def test_no_syntax(self):
        chunk = ch.Code_chunk(no_syntax, 'test')
        self.assertEqual(chunk.get_content(),
                         'table = data.frame()\nsort(table)')
        self.assertEqual(chunk.get_prompt(),
                         ('This is the prompt\n'
                          'That has two rows'))
        self.assertEqual(chunk.get_syntax(), None)
