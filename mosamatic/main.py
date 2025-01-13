from tkinter import Tk

from mosamatic.controller import AppController
from multiprocessing import set_start_method


def main():
    root = Tk()
    AppController(root)
    root.mainloop()


if __name__ == "__main__":
    set_start_method('spawn')
    main()
