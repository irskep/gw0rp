from leveleditorlibs import tool, resources, graphics, draw, level

class PlayerStart(tool.Tool):
    def start_drawing(self, x, y):
        level.player_x = x
        level.player_y = y
    
    def stop_drawing(self, x, y):
        self.start_drawing(x,y)
    
    def keep_drawing(self, x, y, dx, dy):
        level.player_x = x
        level.player_y = y

default = PlayerStart()
priority = 1
group = 'Events'
image = resources.PlayerStart
cursor = graphics.cursor['CURSOR_DEFAULT']
