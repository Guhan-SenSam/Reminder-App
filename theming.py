from kivy.properties import AliasProperty, ColorProperty

class ThemeManager():

    background_color =ColorProperty()

    primary_color = ColorProperty()

    secondary_color = ColorProperty()

    tertiary_color = ColorProperty()

    accent_color = ColorProperty()

    text_color = ColorProperty()

    secondary_text_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [44/255,62/255,80/255, 1]
        self.primary_color = [50/255,49/255,61/255,1]
        self.secondary_color = [70/255,69/255,81/255,1]
        self.tertiary_color = [90/255,89/255,101/255,1]
        self.accent_color = [218/255,68/255,83/255, 1]
        self.text_color = [1,1,1,1]
        self.secondary_text_color = [1,1,1,.5]



    def set_theme(self, name):
        if name == 'Slate':
            self.background_color = [44/255,62/255,80/255, 1]
            self.primary_color = [50/255,49/255,61/255,1]
            self.secondary_color = [70/255,69/255,81/255,1]
            self.tertiary_color = [90/255,89/255,101/255,1]
            self.accent_color = [218/255,68/255,83/255, 1]
            self.text_color = [1,1,1,1]
            self.secondary_text_color = [0,0,0,.5]

        elif name == 'DeadWood':
            self.background_color = [34/255,40/255,49/255, 1]
            self.primary_color = [48/255,71/255,94/255,1]
            self.secondary_color = [68/255,91/255,114/255,1]
            self.tertiary_color = [88/255,121/255,134/255,1]
            self.accent_color = [242/255,163/255,101/255,1]
            self.text_color = [1,1,1,1]
            self.secondary_text_color = [1,1,1,.5]

        elif name == 'SnowWhite':
            self.background_color = [34/255,40/255,49/255, 1]
            self.primary_color = [0.9,0.9,0.9,1]
            self.secondary_color = [0.7,0.7,0.7,1]
            self.tertiary_color = [0.5,0.5,0.5,1]
            self.accent_color = [17/255,153/255,158/255,1]
            self.text_color = [0,0,0.1,1]
            self.secondary_text_color = [0,0,0.1,.5]

        elif name == 'Candy':
            self.background_color = [255/255,182/255,185/255,1]
            self.primary_color = [250/255,227/255,217/255,1]
            self.secondary_color =  [230/255,207/255,197/255,1]
            self.tertiary_color = [210/255,197/255,187/255,1]
            self.accent_color = [97/255,192/255,191/255,1]
            self.text_color = [0,0,0.1,1]
            self.secondary_text_color = [0,0,0.1,.5]

        elif name == 'PureWhite':
            self.background_color = [0.9,0.9,0.9,1]
            self.primary_color = [0.9,0.9,0.9,1]
            self.secondary_color = [0.7,0.7,0.7,1]
            self.tertiary_color = [0.5,0.5,0.5,1]
            self.accent_color = [218/255,68/255,83/255, 1]
            self.text_color = [0,0,0.1,1]
            self.secondary_text_color = [0,0,0.1,.5]

        elif name == 'PureBlack':
            self.background_color = [0,0,0,1]
            self.primary_color = [0.1,0.1,0.1,1]
            self.secondary_color = [0.2,0.2,0.2,1]
            self.tertiary_color = [0.3,0.3,0.3,1]
            self.accent_color = [218/255,68/255,83/255, 1]
            self.text_color = [1,1,1,1]
            self.secondary_text_color = [1,1,1,.5]
    def rgb2hex(self,list):
        return '#%02x%02x%02x' % (int(list[0]*255),int(list[1]*255),int(list[2]*255))
