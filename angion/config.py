import ConfigParser


class Config(ConfigParser):

    def __init__(self, arg):
        super(ConfigParser, self).__init(arg)
        self.read('angion.cfg')
        self.add_section([
            'Mutation'
            'Function',
            'Branch',
            'Plot',
            'Fractal',
            'FitnessTest',
        ])
