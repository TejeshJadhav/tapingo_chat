import random


def create_colors_list():
    return [
        'bisque',
        'azure',
        'navy',
        'blue',
        'turquoise',
        'cyan',
        'cadet blue',
        'aquamarine',
        'yellow',
        'gold',
        'salmon',
        'orange',
        'coral',
        'tomato',
        'red',
        'pink',
        'maroon',
        'purple',
        'thistle']


colors_list = create_colors_list()


def get_color():
    color_num = random.randint(0, colors_list.__len__() - 1)
    color = colors_list.pop(color_num)
    if colors_list.__len__() < 1:
        # Refill the list
        colors_list.extend(create_colors_list())
    return color


def get_color_list():
    return colors_list
