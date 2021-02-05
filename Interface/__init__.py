from threading import Thread
from tkinter import *
import time
import _tkinter
import os
from datetime import datetime
from Interface.dropmenu import DropMenu
from Interface.entry_popups import Basic3EntryPopup
from pearowseasytools import daemon_and_start


class Game:
    def __init__(self, name, size, no, path="", image_path: str = None, date=datetime.now()):
        self.name = name
        self.size = size
        self.path = path
        self.no = no
        self.expdate = date
        self.compressed = False
        self.light_command = None
        if image_path is not None:
            self.image = PhotoImage(file=image_path)
        else:
            self.image = r"Data/Graphics/No İmage Found.png"
        self.platform = 0

    def start(self):
        if self.compressed:
            self.decompress()
        print(self.name, "başlatılıyor...")

    def delete(self):
        print("Game deleted")

    def rename(self, name):
        self.name = name

    def compress(self):
        print(self.name, "is compressing...")
        if self.light_command is not None:
            self.light_command("Compressing")
        time.sleep(5)
        self.compressed = True
        if self.light_command is not None:
            self.light_command("Compressed")

        print(self.name, "is compressed")

    def decompress(self):
        print(self.name, "is decompressing...")
        if self.light_command is not None:
            self.light_command("Decompressing")
        time.sleep(5)
        self.compressed = False
        if self.light_command is not None:
            self.light_command("Decompressed")

        print(self.name, "is decompressed")


def gif_runner(self, label: Label, gif: str, frame_rate: int):
    gif_list = []
    i = 0
    if not os.path.exists(gif):
        print("File not exists")
        return
    while True:
        try:
            photo = PhotoImage(file=gif, format=f"gif -index {i}")
            gif_list.append(photo)
            i += 1
        except _tkinter.TclError as error:
            print(f'HATA: "{error}" dolayı GIF yürütülemedi')
            break
    while not self.gifstop:
        for frame in gif_list:
            label["image"] = frame
            time.sleep(1 / frame_rate)


class ScrollableFrame(Canvas):

    def __init__(self, master=None, cnf=None, scrollside=RIGHT, scrollsurface=Y, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, **kw, highlightthickness=0)

        self.frame = Frame(self)
        self.scrollbar = Scrollbar(master, orient=VERTICAL, command=self.yview, scrollregion=self.bbox("all"))

        self.frame.bind("<Configure>", self.moving)

        self.create_window((0, 0), window=self.frame)
        self.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=scrollside, fill=scrollsurface)

    def moving(self, _):
        self.configure(scrollregion=self.bbox("all"))

    def on_mousewheel(self, delta: int):
        if self.yview() == (0.0, 1.0):
            self.yview_moveto(0.0)
            self.xview_moveto(1.0)
            return

        if delta == 120:
            self.yview(SCROLL, -4, UNITS)
        else:
            self.yview(SCROLL, 4, UNITS)


# Eğer oyun adı çok uzunsa ... olsun
class Gamebox(Frame):

    def __init__(self, master, game, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, **kw, height=300, width=200, bg="#292929")
        self.game = game
        self.selected = False
        self.renamemode = False
        self.gifstop = False
        self.rightmenu = DropMenu(self)
        self.game.light_command = self.change_light

        # Her gamebox class'ı için yeni bir resim objesi oluşturulmamalı
        self.lights = [PhotoImage(file=r"Data/Graphics/Işık2_YEŞİL10x10.png"),
                       PhotoImage(file=r"Data/Graphics/Işık_AÇIKMAVİ10x10.png"),
                       PhotoImage(file=r"Data/Graphics/LoopBLUE.png"), PhotoImage(file=r"Data/Graphics/LoopGREEN.png")]
        self.platforms = [PhotoImage(file=r"Data/Graphics/steamicon.png")]
        self.gameimage = PhotoImage(file=game.image)

        name_frame = Frame(self, bg="#292929", height=1, width=25)
        size_frame = Frame(self, bg="#292929", height=1, width=10)
        date_frame = Frame(self, bg="#292929", height=1, width=10)

        self.image = Label(self, image=self.gameimage, borderwidth=0)
        self.Name = Label(name_frame, text=game.name, bg="#292929", fg="#138f00", font=("arial", 11))
        self.size = Label(size_frame, text=f"Boyut: {game.size}", bg="#292929", height=1, width=10, fg="#7d7d7d")
        self.date = Label(date_frame, text=game.expdate.strftime("%d.%m.%Y"), bg="#292929", height=1, width=10,
                          font=("arial", 8), fg="#7d7d7d")
        self.info_light = Label(self, bg="#292929", image=self.lights[self.game.compressed])
        if self.game.platform is not None:
            self.platform_img = Label(self, image=self.platforms[game.platform], borderwidth=0, bg="#292929")
        else:
            self.platform_img = Label(self)

        self.rightmenu.add_command(label="Sil", command=lambda: daemon_and_start(self.remove, "Remove Function"))
        self.rightmenu.add_command(label="Yeniden adlandır", command=self.rename)
        self.rightmenu.add_command(labe="Sıkıştır", command=lambda: daemon_and_start(self.game.compress, "Compressor"))

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.image.place(x=15, y=10)
        name_frame.place(x=5, y=215)
        size_frame.place(x=12, y=240)
        date_frame.place(x=0, y=282)

        self.Name.pack(side=LEFT)
        self.size.pack(side=LEFT)
        self.date.pack(side=LEFT)

        self.info_light.place(x=185, y=2)
        if self.game.platform is not None:
            self.platform_img.place(x=178, y=278)

    def on_enter(self, _):
        back_color = "#323232"

        self.selected = True
        self.bind_all("<Button-1>", self.on_press)
        self.bind_all("<ButtonRelease-1>", self.on_release)
        self.bind_all("<ButtonRelease-3>", self.on_rightclick)

        self["background"] = back_color
        self.Name["background"] = back_color
        self.size["background"] = back_color
        self.date["background"] = back_color
        self.info_light["background"] = back_color
        self.platform_img["background"] = back_color

    def on_leave(self, _):
        back_color = "#292929"

        self.selected = False

        self["background"] = back_color
        self.Name["background"] = back_color
        self.size["background"] = back_color
        self.date["background"] = back_color
        self.info_light["background"] = back_color
        self.platform_img["background"] = back_color

    def on_press(self, _):
        if self.selected:
            back_color = "#464646"

            self["background"] = back_color
            self.Name["background"] = back_color
            self.Name["fg"] = "#1dd900"
            self.size["background"] = back_color
            self.date["background"] = back_color
            self.info_light["background"] = back_color
            self.platform_img["background"] = back_color

    def on_release(self, _):
        if self.selected:
            back_color = "#323232"

            self["background"] = back_color
            self.Name["background"] = back_color
            self.Name["fg"] = "#138f00"
            self.size["background"] = back_color
            self.date["background"] = back_color
            self.info_light["background"] = back_color
            self.platform_img["background"] = back_color

            # Bu threadı kullanarak oyunun açılıp açılmadığına bakılabilir
            daemon_and_start(self.game.start, "Game starter or decompressor")
            self.refresh()

    def on_rightclick(self, event):
        if self.selected:
            self.rightmenu.show(event)

    def rename(self):
        self.Name["text"] = ""
        self.renamemode = True
        self.bind_all("<Key>", self.key_listen)

    def key_listen(self, event):
        if not self.renamemode:
            return
        if event.keysym == "BackSpace":
            self.Name["text"] = self.Name["text"][:-1]

        elif event.keysym == "Return":
            self.unbind("<Key>")
            self.game.rename(self.Name["text"])
            self.renamemode = False
            return

        elif event.keysym == "Escape":
            self.Name["text"] = self.game.name
            self.renamemode = False
            return

        else:
            self.Name["text"] += event.char

    def remove(self):
        self.pack_forget()
        self.master.master.delete_game(self)
        del self

    def refresh(self):
        self.image["image"] = self.gameimage
        self.Name["text"] = self.game.name
        self.size["text"] = f"Boyut: {self.game.size}"
        self.date["text"] = self.game.expdate.strftime("%d.%m.%Y")
        if self.game.platform is not None:
            self.platform_img["image"] = self.platforms[self.game.platform]

    def change_light(self, compress):
        if compress == "Compressing":
            self.info_light["image"] = self.lights[2]

        elif compress == "Decompressing":
            self.info_light["image"] = self.lights[3]

        elif compress == "Compressed":
            self.info_light["image"] = self.lights[1]

        elif compress == "Decompressed":
            self.info_light["image"] = self.lights[0]


class ListObj(Frame):

    def __init__(self, master, text: str = "", games: list = None, row: int = None, menu=True, cnf=None, **kw):
        if games is None:
            games = []
        if cnf is None:
            cnf = {}
        super().__init__(master.frame, cnf, **kw, bg="#001c00")

        self.games = games
        self.selected = False
        self.renamemode = False
        self.old_name = text
        self.menu = menu
        self.row = row

        self.text = Label(self, text=text, height=2, width=30, bg="#001c00", fg="white")
        self.text.pack(side=LEFT)

        if menu:
            self.rightmenu = DropMenu(self)
            self.rightmenu.add_command(label="Yeniden Adlandır", command=self.rename)
            self.rightmenu.add_command(label="Sil", command=self.delete)
        if self.menu:
            self.save()

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def add(self, game):
        self.games.append(game)
        self.save()

    def remove(self, game):
        try:
            self.games.remove(game)
            if self.menu:
                self.save()
        except ValueError:
            print(f"{game.name} the game could not found")
        self.master.master.refresh()
        if not self.menu:
            game.delete()

    def on_enter(self, _):
        self.selected = True
        self.bind_all("<Button-1>", self.on_click)
        self.bind_all("<ButtonRelease-1>", self.on_release)
        if self.menu:
            self.bind_all("<ButtonRelease-3>", self.on_rightclick)

        if self.master.master.selection != self:
            self.text["bg"] = "#002600"

    def on_leave(self, _):
        self.selected = False
        if self.master.master.selection == self:
            return
        self.text["bg"] = "#001c00"

    def on_click(self, _):
        if self.selected:
            self.text["bg"] = "#003000"

    def on_release(self, _):
        if self.selected:
            self.text["bg"] = "#002600"
            self.master.master.select(self)

    def on_rightclick(self, event):
        if self.selected:
            self.rightmenu.show(event, 60, 10)

    def rename(self):
        self.old_name = self.text["text"]
        self.text["text"] = ""
        self.renamemode = True
        self.bind_all("<Key>", self.key_listen)

    def key_listen(self, event):
        if not self.renamemode:
            return
        if event.keysym == "BackSpace":
            self.text["text"] = self.text["text"][:-1]

        elif event.keysym == "Return":
            self.text.unbind("<Key>")
            self.save()
            self.renamemode = False
            return

        elif event.keysym == "Escape":
            self.text["text"] = self.old_name
            self.text.unbind("<Key>")
            self.renamemode = False
            return

        else:
            self.text["text"] += event.char

    def save(self):
        if not os.path.exists("Data/data.ls"):
            open("Data/data.ls", "w", encoding="utf-8")
        games = []
        for game in self.games:
            games.append(game.no)
        if self.row is None:
            with open("Data/data.ls", "r+") as file:
                self.row = len(file.read().split("\n")) - 1
                file.write(f"{self.text['text']}{games}\n")
        else:
            data = open("Data/data.ls", "r").read().splitlines()
            with open("Data/data.ls", "w", encoding="utf-8") as file:
                data[self.row] = f"{self.text['text']}{games}"
                file.write("\n".join(data) + "\n")

    def delete(self):
        data = open("Data/data.ls", "r").read().splitlines()
        with open("Data/data.ls", "w", encoding="utf-8") as file:
            print(data, self.row) # debug print
            del data[self.row]
            if len(data) > 0:
                file.write("\n".join(data) + "\n")
        self.master.master.remove_list(self)


class AddList(ListObj):

    def __init__(self, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, "+ Liste Ekle", cnf, **kw, row=-1, menu=False)
        self.listbox = master

    def on_release(self, _):
        if self.selected:
            self.text["bg"] = "#002600"
            self.add_list()

    def add_list(self):
        self.listbox.add_list(ListObj(self.listbox, text="Yeni Liste"), True)


class Listbox(ScrollableFrame):

    def __init__(self, master=None, games=None, cnf=None, **kw):
        super().__init__(master, cnf, **kw, width=200, height=700, bg="#001500")
        if games is None:
            games = []
        self.mainlist = ListObj(self, "Tümü", games, -1, False)
        self.lists = [self.mainlist]
        self.selection = None
        self.add_butt = AddList(self)

        self.scan_file()
        self.select(self.mainlist)

    def add_list(self, liste: ListObj, select=False):
        self.lists.append(liste)
        self.show_lists()
        if select:
            self.select(liste)

    def remove_list(self, listobj):
        self.hide_lists()
        if self.selection == listobj:
            self.select(self.mainlist)
        self.lists.remove(listobj)
        self.show_lists()
        Thread(target=self.master.master.set_scroll).start()

    def add_game(self, game):
        self.selection.add(game)
        self.select(self.selection)

    def remove_game(self, game):
        if game in self.selection.games:
            if self.selection == self.mainlist:
                for thelist in self.lists:
                    thelist.remove(game)
            self.selection.remove(game)
        else:
            print(f"There is no game named {game.name} in the selected list")

    def scan_file(self):
        if not os.path.exists("Data/data.ls"):
            open("Data/data.ls", "w", encoding="utf-8")

        with open("Data/data.ls", "r") as lists:
            i = 0
            for prop in lists.read().split("\n"):
                name = prop[:prop.find("[")]
                games = []
                if prop == "":
                    self.show_lists()
                    return
                for listgame in prop[prop.find("[") + 1:prop.find("]")].split(","):
                    if listgame == "":
                        continue
                    for game in self.mainlist.games:
                        if int(listgame.strip()) == game.no:
                            games.append(game)
                            break
                self.add_list(ListObj(self, name, games, i))
                i += 1

    def show_lists(self):
        self.add_butt.pack_forget()
        for liste in self.lists:
            liste.pack()
        self.add_butt.pack()
        self.yview_moveto(0)
        self.xview_moveto(1)

    def hide_lists(self):
        for liste in self.lists:
            liste.pack_forget()

    def select(self, selection):
        self.selection = selection
        for widget in self.lists:
            if widget == selection:
                selection.text["bg"] = "#002600"
            else:
                widget.text["bg"] = "#001c00"  # Neden böyle yapımışım hatırlamıyorum

        self.master.master.load_list(self.selection)

    def refresh(self):
        self.select(self.selection)


class AddGame(Frame):

    def __init__(self, master=None, command=None, main=True, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, **kw, height=300, width=200, bg="#292929")
        self.selected = False
        self.command = command
        self.list = None
        self.listbox = None

        self.Addimg = PhotoImage(file=r"Data/Graphics/Add Game Button.png")
        self.highlighted = PhotoImage(file=r"Data/Graphics/Add Game Button HL.png")
        self.mostlighted = PhotoImage(file=r"Data/Graphics/Add Game Button ML.png")
        self.main = main

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.text = Label(self, image=self.Addimg, borderwidth=0)
        self.text.pack()

    def on_enter(self, _):
        self.selected = True
        self.text["image"] = self.highlighted
        self.bind_all("<Button-1>", self.on_click)
        self.bind_all("<ButtonRelease-1>", self.on_release)

    def on_leave(self, _):
        self.selected = False
        self.text["image"] = self.Addimg

    def on_click(self, _):
        if self.selected:
            self.text["image"] = self.mostlighted

    def on_release(self, event):
        if self.selected:
            self.text["image"] = self.highlighted
            if self.main:
                Basic3EntryPopup(self, "Oyun ekle", "Oyun adı", "Oyun yolu", "Exe yolu", "Kaydet",
                                 self.save)
            elif self.list is not None:
                # Zaten olanları ekleme
                self.listbox = self.list.master.master
                menu = DropMenu(self)
                selected = IntVar()
                selected.set(-1)

                for game in range(len(self.listbox.mainlist.games)):
                    menu.add_radiobutton(label=self.listbox.mainlist.games[game].name,
                                         variable=selected, command=lambda: self.add_to_list(selected), value=game)

                menu.show(event, 70)

    def add_to_list(self, game):
        self.master.master.add_game(self.listbox.mainlist.games[game.get()])

    def save(self, entrys):
        name = entrys.Entry1.get()
        path = entrys.Entry2.get()
        exe = entrys.Entry3.get()

        entrys.destroy()

        if self.command is not None:
            self.command(path, exe, name)
            self.master.master.master.master.list_scroll.select(self.master.master.master.master.list_scroll.selection)
        else:
            self.master.master.add_game(Game(name, "100GB", path))

        print(f"{name} adlı oyun kaydediliyor...")


class GameSection(ScrollableFrame):
    # add game / dell game functions
    def __init__(self, master=None, addgamecom=None, cnf=None, scrollside=RIGHT, scrollsurface=Y, **kw):
        super().__init__(master, cnf, scrollside, scrollsurface, **kw, width=650, height=645, bg="black")
        self.horizonalc = 3

        self.add_button = AddGame(self.frame, addgamecom)
        self.widgets = [self.add_button]

        self.frame.configure(bg="black")

    def set_games(self, thelist: ListObj, main: bool):
        self.widgets = []
        for game in thelist.games:
            self.widgets.append(Gamebox(self.frame, game))
        self.add_button.main = main
        self.add_button.list = thelist
        self.widgets.append(self.add_button)

    def show_games(self):
        i = 0
        k = 0
        for game in self.widgets:
            if i == self.horizonalc:
                k += 1
                i = 0
            game.grid(row=k, column=i, padx=10, pady=15)
            i += 1
        self.yview_moveto(0)

    def hide_games(self):
        for widget in self.widgets:
            widget.grid_forget()

    def add_game(self, game):
        self.master.master.list_scroll.add_game(game)

    def delete_game(self, gamebox):
        self.hide_games()
        self.master.master.list_scroll.remove_game(gamebox.game)
        self.show_games()
        self.master.master.list_scroll.refresh()


class Settings(Label):

    def __init__(self, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}

        self.selected = False
        self.image = PhotoImage(file=r"Data/Graphics/CogWheel.png")
        self.highlighted = PhotoImage(file=r"Data/Graphics/CogWheel Highlighted.png")
        self.mostlighted = PhotoImage(file=r"Data/Graphics/CogWheel Mostlighted.png")

        super().__init__(master, cnf, **kw, image=self.image, bg="black")

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, _):
        self.selected = True
        self.bind_all("<Button-1>", self.on_click)
        self.bind_all("<ButtonRelease-1>", self.on_release)

        self.configure(image=self.highlighted)

    def on_leave(self, _):
        self.selected = False
        self.configure(image=self.image)

    def on_click(self, _):
        if self.selected:
            self.configure(image=self.mostlighted)

    def on_release(self, _):
        if self.selected:
            print("Settings opening...")
            self.configure(image=self.highlighted)


def change(dic, obj):
    for a in dic:
        obj[a] = dic[a].get()


def xychn(obj, x, y):
    obj.place(x=x, y=y)


def width_changer(root, widget, name="Nothing", x=0, y=0):
    root = Toplevel(root)
    root.title(name)
    root.geometry("200x110")
    height = Label(root, text="height")
    width = Label(root, text="width")
    iks = Label(root, text="X")
    ye = Label(root, text="Y")
    hentry = Entry(root)
    wentry = Entry(root)
    xentry = Entry(root)
    yentry = Entry(root)

    xychn(widget, x, y)

    hentry.insert(0, widget["height"])
    wentry.insert(0, widget["width"])
    xentry.insert(0, x)
    yentry.insert(0, y)
    dic = {"height": hentry, "width": wentry}

    Button(root, text="widthhe", command=lambda: change(dic, widget)).grid(column=0, row=4)
    Button(root, text="xy", command=lambda: xychn(widget, xentry.get(), yentry.get())).grid(column=1, row=4)

    height.grid(row=0, column=0)
    width.grid(row=1, column=0)
    hentry.grid(row=0, column=1)
    wentry.grid(row=1, column=1)
    iks.grid(row=2, column=0)
    ye.grid(row=3, column=0)
    xentry.grid(row=2, column=1)
    yentry.grid(row=3, column=1)


def game_creator(count=None):
    gamelist = []
    for a, b, c in [["Ark: Survival Evolved", "200GB", 1], ["Grand Thieves Auto V", "180GB", 2],
                    ["Grand Thieves Auto IV", "80GB", 3], ["Paladins", "21GB", 4], ["Portal", "200MB", 5],
                    ["Space Engineers", "24GB", 6], ["Empirion - Galactic Survival", "17GB", 7], ["Portal 2", "5GB", 8],
                    ["Arma 2", "60GB", 9], ["Deceit", "20GB", 10], ["Company of Heroes 2", "24GB", 11],
                    ["Bus Simulator 2018", "5GB", 12]]:
        gamelist.append(Game(a, b, c))
    if count is None:
        return gamelist
    return gamelist[:count]


def set_size(self, height, width):
    self["height"] = int(self["height"]) + height
    self["width"] = int(self["width"]) + width


# Bütün eklemelerin vb. seçili olan öğeler için yapılmasını sağlayan fonksiyonlar ekle
class MainInterface(Frame):

    def __init__(self, master=None, library=None, addgamecom=None, cnf=None, **kw):
        if library is None:
            library = []
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, **kw, bg="black")
        self.unpackact = False
        self.gamespack = True
        self.listpack = True
        # Görseller buraya koyulabilir

        games_frame = Frame(self)
        list_frame = Frame(self)
        self.sets = Frame(games_frame, bg="black")

        self.games_section = GameSection(games_frame, addgamecom)
        self.list_scroll = Listbox(list_frame, library)
        settim = Settings(self.sets)

        self.games_section.pack(side=LEFT, expand=True, fill=BOTH)
        self.list_scroll.pack(expand=True, fill=Y)
        self.sets.pack(side=RIGHT, fill=Y, expand=True)

        games_frame.grid(row=0, column=1, sticky=NSEW)
        list_frame.grid(row=0, column=0, rowspan=2, sticky=NSEW)
        settim.pack()

        self.bind("<Configure>", self.onmove)
        self.games_section.bind("<Enter>", lambda _: self.set_focuss(0))
        self.list_scroll.bind("<Enter>", lambda _: self.set_focuss(1))

        self.First = True

    def set_scroll(self):
        time.sleep(0.1)
        self.games_section.yview_moveto(0.5)
        self.games_section.yview_moveto(0.0)
        self.list_scroll.yview_moveto(0.0)
        self.games_section.xview_moveto(0.0)

        if self.games_section.yview() == (0.0, 1.0) and self.gamespack:  # elif konusunda düzenleme yap
            self.games_section.yview_moveto(0)
            self.unpackact = True
            self.games_section.scrollbar.pack_forget()
            self.gamespack = False
            time.sleep(0.1)
            self.unpackact = False

        elif not self.gamespack and self.games_section.yview() != (0.0, 1.0):
            self.unpackact = True
            self.sets.pack_forget()
            self.games_section.scrollbar.pack(side=RIGHT, fill=Y)
            self.gamespack = True
            self.sets.pack(side=RIGHT, fill=Y)
            time.sleep(0.1)
            self.unpackact = False

        if self.list_scroll.yview() == (0.0, 1.0) and self.listpack:
            self.list_scroll.yview_moveto(0)
            self.unpackact = True
            self.list_scroll.scrollbar.pack_forget()
            self.listpack = False
            time.sleep(0.1)
            self.unpackact = False

        elif not self.listpack and self.list_scroll.yview() != (0.0, 1.0):
            self.unpackact = True
            self.list_scroll.pack_forget()
            self.list_scroll.scrollbar.pack(side=RIGHT, fill=Y)
            self.list_scroll.pack()
            self.listpack = True
            time.sleep(0.1)
            self.unpackact = False

    def onmove(self, event):
        if self.First:
            self.oldheight = event.height
            self.oldwidth = event.width
            self.First = False
        if not self.unpackact:

            # Boyut ayarlama
            height_diffrence = event.height - self.oldheight
            width_difference = event.width - self.oldwidth

            set_size(self.games_section, height_diffrence, width_difference)
            set_size(self.list_scroll, height_diffrence, 0)

        # Show game kısmı
        show_game = (int(self.games_section["width"]) - 100) // 200
        if show_game > 0:
            self.games_section.horizonalc = show_game
            self.games_section.show_games()

        self.games_section.xview(MOVETO, 0.0)
        Thread(target=self.set_scroll).start()

        self.oldheight = event.height
        self.oldwidth = event.width

    def set_focuss(self, widget: int):
        widgets = [self.games_section, self.list_scroll]
        widgets[widget].bind_all("<MouseWheel>", lambda event: widgets[widget].on_mousewheel(event.delta))
        for i in widgets:
            if i != widgets[widget]:
                i.unbind("<MouseWheel>")

    def load_list(self, liste: ListObj):
        self.games_section.hide_games()
        self.games_section.set_games(liste, not liste.menu)
        self.games_section.show_games()
        Thread(target=self.set_scroll).start()

    def add_list(self, name):
        self.list_scroll.add_list(ListObj(self.list_scroll, text=name))


if __name__ == '__main__':
    os.chdir("..")
    window = Tk()
    window.configure(bg="black")
    window.title("RarGame Launcher -GUI DEBUG-")

    created = game_creator(3)

    Mainwin = MainInterface(window, created)

    Mainwin.pack(fill=BOTH, expand=True)

    window.mainloop()
