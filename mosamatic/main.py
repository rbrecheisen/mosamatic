from tkinter import Tk

from controller import AppController


def main():
    root = Tk()
    app = AppController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
