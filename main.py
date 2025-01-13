from tkinter import Tk

from mosamatic.controller import AppController


def main():
    root = Tk()
    AppController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
