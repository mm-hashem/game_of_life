import copy

class Styles:

    # Color palette
    CLR_DEAD_CELL  = [141, 141, 141] # #8d8d8d
    CLR_ALIVE_CELL = [255, 255, 0]   # #ffff00

    CLR_BG         = "#112736" # Background color
    CLR_CLK_BTN    = "#456882" # Clickable button color
    CLR_GREYED_BTN = "#D2C1B6" # Greyed-out button color
    CLR_BTN_BD     = "#234C6A" # Button border
    CLR_TEXT       = "#ffffff" # Text color

    DEFAULT_GREYED_BTN = {
        "bg": CLR_GREYED_BTN,
        "fg": CLR_TEXT,
        "bd": 0,
        "highlightthickness": 2,
        "relief": "flat",
        "highlightbackground": CLR_BTN_BD,
        "activebackground": CLR_BTN_BD,
        "activeforeground": CLR_TEXT,
        "padx": 8,
        "font": ("Segoe UI", 11)
    }

    DEFAULT_CLK_BTN = {
        **DEFAULT_GREYED_BTN,
        "bg": CLR_CLK_BTN
    }

    DEFAULT_SLIDER = {
        "bg": CLR_BG,
        "fg": CLR_TEXT,
        "bg":CLR_BG,
        "highlightbackground": CLR_BG,
        "relief": "flat",
        "sliderrelief": "flat",
        "troughcolor": CLR_CLK_BTN
    }

    DEFAULT_LABEL = {
        "bg": CLR_CLK_BTN,
        "fg": CLR_TEXT,
        "highlightthickness": 0,
        "highlightbackground": None
    }

    DEFAULT_LABEL_ERROR = {
        "bg": CLR_BG,
        "fg": "red"
    }

    DEFAULT_ENTRY = {
        "bg": CLR_CLK_BTN,
        "fg": "#ffffff",
        "relief": "flat",
        "highlightthickness": 2,
        "highlightbackground": CLR_CLK_BTN, 
        "highlightcolor": CLR_BTN_BD,
        "bd": 0,
        "width": 10 
    }

    def __init__(self, size: str, show_label_border: bool, label_background: str):

        self.STYLE_GREYED_BTN  = copy.deepcopy(Styles.DEFAULT_GREYED_BTN)
        self.STYLE_SLIDER      = copy.deepcopy(Styles.DEFAULT_SLIDER)
        self.STYLE_LABEL       = copy.deepcopy(Styles.DEFAULT_LABEL)
        self.STYLE_LABEL_ERROR = copy.deepcopy(Styles.DEFAULT_LABEL_ERROR)
        self.STYLE_ENTRY       = copy.deepcopy(Styles.DEFAULT_ENTRY)

        if show_label_border:
            self.STYLE_LABEL["highlightthickness"]  = 2
            self.STYLE_LABEL["highlightbackground"] = self.CLR_BTN_BD
        else:
            self.STYLE_LABEL["highlightthickness"]  = 0
            self.STYLE_LABEL["highlightbackground"] = None

        if size == "small":
            self.STYLE_GREYED_BTN["font"] = ("Segoe UI", 9)
            self.STYLE_GREYED_BTN["padx"] = 5
        elif size == "medium":
            self.STYLE_GREYED_BTN["font"] = ("Segoe UI", 11)
            self.STYLE_GREYED_BTN["padx"] = 8
        else:
            raise ValueError("Invalid size. Expected 'small' or 'medium'.")
        
        if label_background == "none":
            self.STYLE_LABEL["bg"] = self.CLR_BG
        elif label_background == "light":
            self.STYLE_LABEL["bg"] = self.CLR_CLK_BTN
        else:
            raise ValueError("Invalid label_background. Expected 'none' or 'light'.")
        
        self.STYLE_CLK_BTN = {
            **self.STYLE_GREYED_BTN,
            "bg": self.CLR_CLK_BTN
        }