import npyscreen as nps
import memit.markdown_parser.Chunk as ch


# maybe I shouldn't build a new tree but re-use the section tree inside the
# MLTreeMultiSelect widget
class Chunk_tree(nps.TreeData):

    @classmethod
    def from_node(cls, node, chunk_type):
        '''node object needs to have a get_content and get_children method
        '''
        chunk = ch.chunk_factory(node.get_content(),
                                 node.get_title(),
                                 chunk_type)
        root = cls(chunk, ignore_root=False, expanded=True)
        cls.initialize_tree(root, node.get_children(), chunk_type)
        return root

    @classmethod
    def initialize_tree(cls, parent, children, chunk_type):
        if not children:
            return
        for child in children:
            chunk = ch.chunk_factory(child.get_content(),
                                     child.get_title(),
                                     chunk_type)
            tree_child = parent.new_child(chunk, expanded=False)
            cls.initialize_tree(tree_child,
                                child.get_children(),
                                chunk_type)

    def get_content_for_display(self):
        return self.get_content().get_title()


class Chunk_choice_form(nps.Form):

    def __init__(self, tree_data, **kwargs):
        self.tree_data = tree_data
        super().__init__(**kwargs)

    def create(self):
        self.tree = self.add(nps.MLTreeMultiSelect,
                             name='select topics',
                             values=self.tree_data)

    def get_values(self):
        selected = self.tree.get_selected_objects(return_node=False)
        selected = list(selected)
        valid = [ch for ch in selected if ch.get_content()]
        return valid
