import npyscreen as nps
import argparse
import memit.topic_choice as tc
from memit.markdown_parser.Section import Section


def form_factory(title, text):
    form = nps.Form(name=title)
    form.add(nps.Pager, values=text, autowrap=True)
    return form


class App(nps.NPSAppManaged):
    STARTING_FORM = 'topic_choice'

    def __init__(self,
                 dirpath=None,
                 filepath=None,
                 nr_chunks=20,
                 chunk_type='code',
                 **kwargs):
        super().__init__(**kwargs)

        self.dirpath = dirpath
        self.filepath = filepath
        self.nr_chunks = nr_chunks
        self.chunk_type = chunk_type

    def onStart(self):
        if self.dirpath:
            section = Section.from_dir(self.dirpath)
        elif self.filepath:
            section = Section.from_file(self.filepath)
        else:
            raise ValueError('App needs a directory or filepath!')

        tree = tc.Chunk_tree.from_node(section, self.chunk_type)
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
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--filepath', '-f', default=None)
    group.add_argument('--dirpath', '-d', default=None)
    args = parser.parse_args()

    if args.filepath:
        content = Section.from_file(args.filepath)
    elif args.dirpath:
        content = Section.from_dir(args.dirpath)

    app = App(args.dirpath, args.filepath).run()
