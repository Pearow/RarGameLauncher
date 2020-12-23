from Compress import Directory
import datetime
import time
import sys
import os
from pearowseasytools import daemon_and_start, addprop, readprop
from random import randint
from Interface import MainInterface, ListObj, Gamebox
from tkinter import Tk, PhotoImage

# If os.exists kullanarak oyun dosyalarının olup olmadığını kontrol et ona göre oyunun oynanabilir olup olmadığını
# göstersin BUG!! bir oyun sıkıştırılırken aynı anda başka bir sıkıştırılmış oyun çalıştırılmaya çalışılırsa dosyalar
# çakışır
rarday = 1
scanrate = 600
breaktime = 60
Version = "pre_alpha 0.0.1"


def create_endday(day):
    return datetime.datetime.now() + datetime.timedelta(days=day)


class Game:
    def __init__(self, fullpath: str, exefile: str, expdate: str, size: int, no: int, name=None, image: str = None,
                 platform: str = None):
        self.fullpath = fullpath
        self.exefile = exefile
        self.no = no
        self.compressor = Directory(fullpath)
        self.compressed = fullpath[-3:] == "pcf"
        expdate = expdate.split(".")
        self.expdate = datetime.datetime(day=int(expdate[0]), month=int(expdate[1]), year=int(expdate[2]))
        self.file = f"library/{self.no}.gm"
        self.bytes = size
        self.light_command = None

        if name is None or name == "" or name == " ":
            name = exefile.split(os.path.sep)[-1]
        self.name = name

        if image is None:
            self.image = r"Data/Graphics/No İmage Found.png"
        else:
            self.image = image

        if platform is not None:
            self.platform = platform
        else:
            self.platform = None

        if size >= 1024 * 1024 * 1024:
            self.size = size / (1024 * 1024 * 1024)
            if self.size >= 10:
                self.size = int(self.size)
            else:
                self.size = int(self.size * 10) / 10
            self.size = str(self.size) + "GB"

        elif size >= 1024 * 1024:
            self.size = size / (1024 * 1024)
            if self.size >= 100:
                self.size = int(self.size)
            elif self.size >= 10:
                self.size = int(self.size * 10) / 10
            else:
                self.size = int(self.size * 100) / 100
            self.size = str(self.size) + "MB"
        else:
            self.size = str(size // 1024) + "KB"

    def compress(self):
        if __name__ == '__main__':  # Gereksizse kaldır
            if not self.compressed:
                print(self.name, "is compressing")
                if self.light_command is not None:
                    self.light_command("Compressing")
                self.compressor.compress()
                self.fullpath = self.compressor.name
                self.compressed = True
                if self.light_command is not None:
                    self.light_command("Compressed")
                self.save()
                print(f"{self.name}'s compression completed")

    def decompress(self):
        if self.compressed:
            print(self.name, "is decompressing")
            if self.light_command is not None:
                self.light_command("Decompressing")
            self.compressor.decompress()
            self.fullpath = self.compressor.name
            self.compressed = False
            if self.light_command is not None:
                self.light_command("Decompressed")
            self.save()
            print(f"{self.name}'s decompression completed")

    def save(self):
        with open(self.file, "w") as file:
            file.write(
                f"name: {self.name}\npath: {self.fullpath}\nexefile: {self.exefile}"
                f"\nexpdate: {self.expdate.strftime('%d.%m.%Y')}\nsize: {self.bytes}")

    def delete(self):
        if self.compressed:
            self.decompress()
        if os.path.exists(self.file):
            os.remove(self.file)

    def start(self):
        if self.compressed:
            self.decompress()
        old_path = os.getcwd()
        game_path = os.path.sep.join(self.exefile.split(os.path.sep)[:-1])
        os.chdir(game_path)
        os.startfile(self.exefile)
        self.expdate = datetime.datetime.now() + datetime.timedelta(days=rarday)
        os.chdir(old_path)
        self.save()

    def rename(self, name):
        self.name = name
        self.save()

    def checkexp(self):
        if not self.compressed and self.expdate < datetime.datetime.now():
            self.compress()
            return True
        else:
            return False

    def show_properties(self):
        print(
            f"""Name: {self.name}
Full path: {self.fullpath}
Exe file: {self.exefile}
No: {self.no}
Compression: {self.compressed}
Expire Date: {self.expdate.strftime("%d.%m.%Y")}
Compressor Name: {self.compressor.name}
"""
        )

    def list(self):
        self.compressor.list()

    def stop_comprocess(self):
        self.compressor.stop = True


class Program:
    def __init__(self):
        if not os.path.exists("library"):
            os.mkdir("library")
        self.stop = False
        self.library = []
        self.window = None
        self.interface = None

        self.game_scan()

    def game_scan(self):
        for filename in os.listdir("library"):
            with open(f"library/{filename}", "r") as file:
                properties = file.read().split("\n")
                if len(properties) != 5 or filename[-3:] != ".gm":
                    print(f"{filename} the game file is damaged or wrong.")
                    continue
                game = Game(properties[1][6:], properties[2][9:], properties[3][9:], int(properties[4][6:]),
                            int(filename[:-3]), properties[0][6:])
                self.library.append(game)

    def add_game(self, path: str, exefile: str, name: str = None):
        nos = list(range(1000, 9999))
        if not os.path.exists(path):
            print("File could not find")
            return
        for game in self.library:
            if game.fullpath == path:
                print("You already added this game")
                return
            nos.remove(game.no)
        no = nos[randint(0, len(nos))]

        if len(nos) < 2:
            print(len(nos), "You reached the maximum accepted game count of RGL. How did you do that?")
        del nos

        size = 0
        for before, dirs, files in os.walk(path):
            for file in files:
                try:
                    size += os.path.getsize(f"{before}{os.path.sep}{file}")
                except FileNotFoundError as err:
                    print(err)
        del before, dirs, files

        expdate = create_endday(rarday).strftime('%d.%m.%Y')
        game = Game(path, exefile, expdate, size, no, name)
        self.library.append(game)
        game.save()
        if name is not None:
            print(name, "kütüphaneye eklendi")
        else:
            print(path, "kütüphaneye eklendi")
        return game

    def list_games(self):
        for game in self.library:
            print(game.fullpath)

    def showlibrary(self):
        for game in self.library:
            print(40 * "_")
            game.show_properties()
            print(40 * "_")

    def exp_scanner(self):
        # Cool down
        time.sleep(10)# Sonrasında daha uzun bir süre olacak
        while not self.stop:
            for game in self.library:
                if game.checkexp():
                    time.sleep(breaktime)
            print(f"All scans completed. Next scan is {scanrate} seconds later")
            time.sleep(scanrate)

    def list(self):
        i = 0
        for game in self.library:
            print(i, game.fullpath)
            i += 1
        self.library[int(input("Oyun seç"))].list()

    def gui_start(self):
        self.window = Tk()
        self.window.title("RarGame Launcher")
        self.interface = MainInterface(self.window, self.library, self.add_game)

        self.interface.pack(fill="both", expand=True)

        self.window.mainloop()
        self.stop = True

    def set_lists(self, master):
        if not os.path.exists("Data/data.ls"):
            open("Data/data.ls", "w", encoding="utf-8")
        listes = []
        with open("Data/data.ls", "r", encoding="utf-8") as lists:
            for prop in lists.read().split("\n"):
                name = prop[:prop.find("[")]
                games = []
                if prop == "":
                    return []
                for listgame in prop[prop.find("[") + 1:prop.find("]")].split(","):
                    for game in self.library:
                        if int(listgame.strip()) == game.no:
                            games.append(game)
                            break
                listes.append(ListObj(master, name, games))
        return listes

    def start(self):
        daemon_and_start(self.exp_scanner, "Date scanner")
        self.gui_start()


if __name__ == '__main__':
    Pro = Program()
    Pro.start()
