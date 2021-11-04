import streamlit as st

def color_performance(column):
    """
    color values in given column using green/red based on value>0
    Args:
        column:

    Returns:

    """
    color = 'green' if column > 0 else 'red'
    return f'color: {color}'


def money_color(value):
    if value < 0:
        color = 'red'
    elif value > 0:
        color = 'green'
    else:
        color = 'gray'
    return color

