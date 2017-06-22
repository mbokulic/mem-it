import npyscreen as nps
import argparse
import random
import memit.topic_choice as tc
from memit.markdown_parser.Section import Section


def form_factory(title, text, callback):
    # form = MuttPager()
    # form.wStatus1.value = title
    # form.wStatus2.value = 'parko'
    # form.wMain.values = text
    # form.wMain.autowrap = True
    # form.add_handlers({
    #     '^N': callback
    # })

    form = CustomForm(next_callback=callback, name=title)
    form.add_widget(nps.Pager, values=text, autowrap=True)
    form.add_handlers({
        '^N': callback
    })

    return form


class CustomForm(nps.ActionFormV2WithMenus):
    class next_button(nps.wgbutton.MiniButtonPress):
        def whenPressed(self):
            return self.parent._on_next()

    class help_button(nps.wgbutton.MiniButtonPress):
        def whenPressed(self):
            return self.parent._on_help()

    def create_control_buttons(self):
        OFFSET_1 = (1, 6)
        OFFSET_2 = (1, 30)

        text = 'next (CTRL-n)'
        self._add_button('next_button',
                         self.__class__.next_button,
                         text,
                         0 - OFFSET_1[0],
                         0 - OFFSET_1[1] - len(text),
                         None)

        text = 'help'
        self._add_button('help_button',
                         self.__class__.help_button,
                         text,
                         0 - OFFSET_2[0],
                         0 - OFFSET_2[1] - len(text),
                         None)

    def __init__(self, next_callback, *args, **keywords):
        super(CustomForm, self).__init__(*args, **keywords)
        self._on_next = next_callback

    def _on_help(self):
        pass


class MuttPager(nps.FormMuttActive):
    '''Mutt-style form with a pager widget in the middle
    '''
    MAIN_WIDGET_CLASS = nps.Pager


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

    def next_form(self):
        '''switches to next form in line. Will call onInMainLoop by itself
        '''
        self.switchFormNow()

    def onInMainLoop(self):
        history = self.getHistory()
        last_form = history[len(history) - 1]
        if last_form == 'topic_choice':
            # this means topic choice is finished
            self.chunks = self.tree_choices.get_values()
            random.shuffle(self.chunks)
            self.chunks = self.chunks[:self.nr_chunks]
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
                                text=lines,
                                callback=self.next_form)
            self.registerForm('show_prompt', form)
        except IndexError:
            self.setNextForm(None)

    def show_answer(self):
        self.setNextForm('show_answer')
        lines = self.next_chunk.get_content().split('\n')
        form = form_factory(title=self.next_chunk.get_title(),
                            text=lines,
                            callback=self.next_form)
        self.registerForm('show_answer', form)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--filepath', '-f', default=None)
    group.add_argument('--dirpath', '-d', default=None)
    parser.add_argument('--nr_chunks', '-n', type=int)
    args = parser.parse_args()

    if args.filepath:
        content = Section.from_file(args.filepath)
    elif args.dirpath:
        content = Section.from_dir(args.dirpath)

    if args.nr_chunks:
        app = App(args.dirpath, args.filepath, nr_chunks=args.nr_chunks).run()
    else:
        app = App(args.dirpath, args.filepath).run()
