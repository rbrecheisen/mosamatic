from tkinter import Tk

from mosamatic.controller import Controller


def main():
    root = Tk()
    controller = Controller(root)
    root.mainloop()


if __name__ == "__main__":
    main()
