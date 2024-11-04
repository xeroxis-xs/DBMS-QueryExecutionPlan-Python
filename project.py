from interface import Interface
#from preprocessing import Preprocessing
from whatif import WhatIf


class Project:
    def __init__(self):
        self.interface = Interface()
        #self.preprocessing = Preprocessing()
        self.whatif = WhatIf()

    def run(self):
        self.interface.run()
        #self.preprocessing.run()
        self.whatif.run()


if __name__ == '__main__':
    project = Project()
    project.run()
    print('Project run')