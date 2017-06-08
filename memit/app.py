import npyscreen as nps
import memit.topic_choice as tc
from memit.markdown_parser.Section import Section


def form_factory(title, text):
    form = nps.Form(name=title)
    form.add(nps.Pager, values=text)
    return form


class App(nps.NPSAppManaged):
    STARTING_FORM = 'topic_choice'

    def __init__(self, chunk_type, **kwargs):
        super().__init__(**kwargs)
        self.chunk_type = chunk_type

    def _init_tree(self):
        filepath = 'test/data/test.md'
        section = Section.from_file(filepath)
        tree = tc.Chunk_tree.from_node(section, self.chunk_type)
        return tree

    def onStart(self):
        tree = self._init_tree()
        self.tree_choices = self.addForm(
            'topic_choice', tc.Chunk_choice_form, tree)

    def onInMainLoop(self):
        history = self.getHistory()
        last_form = history[len(history) - 1]
        if last_form == 'topic_choice':
            # this means topic choice is finished
            self.chunks = self.tree_choices.get_values()
            self.show_prompt()
        elif last_form == 'show_prompt':
            self.removeForm('show_prompt')
            self.show_answer()
        elif last_form == 'show_answer':
            self.removeForm('show_answer')
            self.show_prompt()

    def show_prompt(self):
        self.setNextForm('show_prompt')
        try:
            self.next_chunk = self.chunks.pop()
            lines = self.next_chunk.get_prompt().split('\n')
            form = form_factory(title=self.next_chunk.get_title(),
                                text=lines)
            self.registerForm('show_prompt', form)
        except IndexError:
            self.setNextForm(None)

    def show_answer(self):
        self.setNextForm('show_answer')
        lines = self.next_chunk.get_content().split('\n')
        form = form_factory(title=self.next_chunk.get_title(),
                            text=lines)
        self.registerForm('show_answer', form)


if __name__ == '__main__':
    app = App('code').run()
