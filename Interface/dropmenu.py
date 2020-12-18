from tkinter import *


class DropMenu(Menu):

    def __init__(self, master):
        Menu.__init__(self, master, tearoff=0)
        self.config(activebackground="grey")

    def show(self, event, x=25, y=10):
        self.tk_popup(event.x_root+x, event.y_root+y, 0)


if __name__ == '__main__':
    window = Tk()

    men = DropMenu(window)
    window.bind("<ButtonRelease-3>", men.show)
    men.add_command(label="Mirhan bir mal", command=lambda: print("Aynen knk"))

    window.mainloop()
