from interface import Interface


class Project:
    def __init__(self):
        self.interface = Interface()

    def run(self):
        self.interface.run()


if __name__ == '__main__':
    project = Project()
    project.run()
