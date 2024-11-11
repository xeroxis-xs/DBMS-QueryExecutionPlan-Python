from interface import Interface
<<<<<<< HEAD
<<<<<<< HEAD
#from preprocessing import Preprocessing
#from whatif import WhatIf
=======
=======
>>>>>>> e9a121c037c897a96cfdeb4a8770c9b1bd77a82d

# from preprocessing import Preprocessing

from whatif import WhatIf
>>>>>>> 777c8ce86c01011e80c9c68680c910b10e7bb198


class Project:
    def __init__(self):
        self.interface = Interface()
<<<<<<< HEAD
<<<<<<< HEAD
        #self.preprocessing = Preprocessing()
        #self.whatif = WhatIf()

    def run(self):
        self.interface.run()
        #self.preprocessing.run()
        #self.whatif.run()
=======
        # self.preprocessing = Preprocessing()

        self.whatif = WhatIf()

    def run(self):
        self.interface.run()
=======
        # self.preprocessing = Preprocessing()

        self.whatif = WhatIf()

    def run(self):
        self.interface.run()
>>>>>>> e9a121c037c897a96cfdeb4a8770c9b1bd77a82d
        # self.preprocessing.run()
        self.whatif.run()
>>>>>>> 777c8ce86c01011e80c9c68680c910b10e7bb198


if __name__ == '__main__':
    project = Project()
    project.run()
    print('Project run')