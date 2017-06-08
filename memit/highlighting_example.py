'''
https://groups.google.com/forum/#!msg/npyscreen/qCPCqY-wUbo/eFJ0BJg8mzEJ
https://stackoverflow.com/questions/7851134/syntax-highlighting-colorizing-cat
'''

#!/usr/bin/env python
# encoding: utf-8
import curses
import npyscreen
#npyscreen.disableColor()

class SyntaxTest(npyscreen.Textfield):
    def update_highlighting(self, start, end):
        # highlighting color
        hl_color  = self.parent.theme_manager.findPair(self, 'IMPORTANT')
        hl_colorb = self.parent.theme_manager.findPair(self, 'WARNING')
        hl_colorc = self.parent.theme_manager.findPair(self, 'CRITICAL')
        
        self._highlightingdata = [curses.A_BOLD, 
                        curses.A_BOLD,
                        hl_color,
                        hl_color,
                        hl_color,
                        hl_color,
                        hl_colorb,
                        hl_colorb,
                        hl_colorc,
                        hl_colorc,
                        hl_colorc,
                        hl_colorc,
        ]


class TestApp(npyscreen.NPSApp):
    def main(self):
        F = npyscreen.Form(name = "Welcome to Npyscreen",)
        t = F.add(SyntaxTest, name = "Text:", value="This is just some text")
        t.syntax_highlighting = True
        
        F.edit()


if __name__ == "__main__":
    App = TestApp()
    App.run()   