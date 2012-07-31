import ConfigParser

cfg = ConfigParser.ConfigParser()
cfg.add_section('FitnessTest')
cfg.add_section('Fractal')
cfg.add_section('Plot')
cfg.add_section('Branch')
cfg.add_section('Function')
cfg.add_section('Mutation')
cfg.read('angion/angion.cfg')
