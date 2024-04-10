import tkinter as tk
from tkinter import ttk


def toggle_button_style():
    style = ttk.Style()
    style.configure('TButton',
                    width=40,
                    height=40,
                    relief='flat',
                    background='#3C414E')
    style.map('TButton',
                background=[('active', '#4C75DD'), ('disabled', '#3C414E')])

    return 'TButton'
