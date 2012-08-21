from config import cfg
from PIL import Image, ImageDraw

class Plot(object):
    segments = []

    def __init__(self, fractal):
        self.fractal = fractal

    def draw(self, seq):
        # (0,150,255) [0x0096ff] -> (42,22,69) [0x45162a]
        def colour_lookup(ratio, shade=False):
            r = 000 + (ratio * (42 - 000))
            g = 150 + (ratio * (22 - 150))
            b = 255 + (ratio * (69 - 255))
            if shade:
                r /= 3.0
                g /= 3.0
                b /= 3.0
            return "rgb({},{},{})".format(int(r), int(g), int(b))

        im = Image.new('RGBA', (cfg.getint('Plot', 'size'), cfg.getint('Plot', 'size')), (10, 4, 27, 255))
        draw = ImageDraw.Draw(im)
        draw.line((
            (cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'margin')),
            (cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'size') - cfg.getint('Plot', 'margin')),
            (cfg.getint('Plot', 'size') - cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'size') - cfg.getint('Plot', 'margin')),
            (cfg.getint('Plot', 'size') - cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'margin')),
            (cfg.getint('Plot', 'margin'), cfg.getint('Plot', 'margin'))),
            fill="rgb(24,12,54)"
        )
        points = self.fractal.point_set()
        # sort by depth so oldest segments are drawn on top
        points.sort(key=lambda p: -p.depth)

        # for point in points:
        #     fill = colour_lookup(float(point.depth) / (points[0].depth + 1), shade=True)
        #     service_x = (point.x // constants.SERVICE_GRID_SPACING) * constants.SERVICE_GRID_SPACING
        #     service_y = (point.y // constants.SERVICE_GRID_SPACING) * constants.SERVICE_GRID_SPACING
        #     draw.rectangle(
        #         (service_x + 1, service_y + 1, service_x + constants.SERVICE_GRID_SPACING - 1, service_y + constants.SERVICE_GRID_SPACING - 1),
        #         fill=fill  # "rgb(25,20,37,20)"
        #     )

        for point in points:
            fill = colour_lookup(float(point.depth) / (points[0].depth + 1))
            for segment in point.segments():
                end = segment.end()
                if end.x >= 0 and end.y >= 0 and end.x <= cfg.get('Plot', 'size') and end.y <= cfg.get('Plot', 'size'):
                    draw.line((point.x, point.y, end.x, end.y), fill=fill)
        im.save("output/out." + str(seq) + ".png", "PNG")
