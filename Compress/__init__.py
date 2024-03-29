import gzip
import os
import sys
from threading import Thread
from multiprocessing import Process, Queue
import shutil
from pearowseasytools import daemon_and_start
import tkinter as tk
import _queue
import time


class File:
    def __init__(self, name: str, num: int, compressed: bool = None):
        self.name = name
        self.extension = name.split(".")[-1]
        self.num = num
        self.size = 0
        self.loc = (0, 0)
        self.compressed = compressed
        if self.extension == "pcf":
            self.compressed = 1
            self.banner = 0  # Hataların anlaşılmasını zorlaştırabilir
        elif self.compressed is None:
            self.compressed = 0

        if not self.compressed:
            self.size = os.path.getsize(self.name)

    def compress(self, rgl_file="RGL_compressed"):
        if self.compressed:
            raise TypeError("Can't compress a compressed file")

        try:
            os.mkdir(rgl_file)
        except FileExistsError:
            pass
        self.size = 0
        with open(rgl_file + os.path.sep + str(self.num) + ".pcf", "wb") as cmpresed:
            with open(self.name, "rb") as file:
                data = file.read()
                if data != b"":
                    compdata = gzip.compress(data, 7)
                    self.size += len(compdata)
                    cmpresed.write(b"\n*****\n" + str.encode(self.name) + b"///" + str.encode(str(self.size)) +
                                   b"*****\n" + compdata)
                    self.banner = len(b"\n*****\n" + str.encode(self.name) + b"///" + str.encode(str(self.size)))
                    # os.remove(self.name)  # dosya dosya rarlarken işeyarayabilir ama seçilebilir olmalı

    def decompress(self):
        if not self.compressed:
            raise TypeError("Can't decompress a non-compressed file")
        with open(self.name, "rb") as compfile:
            old_name = self.name
            self.extract(compfile.read(300))  # Yavaşlatıyor ve bannerı bulmaya yarıyor(Malsın amk hiç bir yerde kullanılmamış)
            # __init__e al
            compfile.seek(self.banner)
            with open(self.name, "wb") as file:
                file.write(gzip.decompress(compfile.read(self.size)))
        os.remove(old_name)

    def extract(self, tag):
        if self.compressed == 1:
            tag = tag[7:]
            i = 0
            while i + 6 <= len(tag):
                if tag[i: i + 6] == b"*****\n":
                    self.banner = len(tag[: i + 6]) + 7
                    tag = tag[:i].decode("utf-8", "replace").split("///")
                    break
                i += 1
            if type(tag) == list and len(tag) == 2:
                self.name = tag[0]
                self.size = int(tag[1])
            else:
                print(tag, "there is an error in this file")


class Directory:
    thread_count = 50

    # Sıkıştırılırken ve sıkıştırma açılırken oluşturulması gereken klasörler ayrı ayrı listelensin
    def __init__(self, name: str):
        self.name = name
        self.rgl_file = "RGL_compressed"
        self.contents = []
        self.ready = False
        if name.split(".")[-1] == "pcf":
            self.compression = 1
        else:
            self.compression = 0

        if self.compression:
            self.purename = self.name[:-4]
        else:
            self.purename = self.name

        if not os.path.exists(self.name):
            if self.compression:
                if os.path.exists(self.purename):
                    self.name = self.purename
                    self.compression = 0
                    print("Compression was false and changed")
                else:
                    print("There is no file named", self.name)
                    raise FileNotFoundError
            else:
                if os.path.exists(self.name + ".pcf"):
                    self.name += ".pcf"
                    self.compression = 1
                    print("Compression was false and changed")
                else:
                    print("There is no file named", self.name)
                    raise FileNotFoundError

        self.stop = False
        self.working = False
        daemon_and_start(self.scan, "Scanner")

    def scan(self):
        no = 0
        self.ready = False
        print(self.name, "scaning")
        if not self.compression:
            for before, dirs, files in os.walk(self.name):
                for file in files:
                    self.contents.append(File(f"{before}{os.path.sep}{file}", no, False))
                    no += 1
        elif self.compression:
            a = 0
            with open(self.name, "rb") as mainfile:
                data = mainfile.read(300)
                while data != b"":
                    file = File(str(no), no, True)
                    file.extract(data)
                    size = file.size
                    file.loc = (a + file.banner, file.size)
                    a += size + file.banner
                    self.contents.append(file)
                    mainfile.seek(a)
                    data = mainfile.read(300)
                    no += 1
        print(f"Scanning of {self.name} completed. {len(self.contents)} file exist.")
        self.ready = True

    def list(self):
        for file in self.contents:
            print(file.name, file.size)

    def compress(self):
        if self.compression:
            raise TypeError("Can't compress a compressed directory")
        while not self.ready:
            if self.stop:
                return
            time.sleep(0.1)

        processes = []
        queue = Queue()
        self.working = "Compressing"
        self.set_rglfile()
        for file in self.contents:
            queue.put(file)
        old_size = queue.qsize()
        ti = time.time()
        for i in range(self.thread_count):
            processes.append(Process(target=self.compressor_worker, args=(queue,), name="worker " + str(i)))

        print(self.name, "sıkıştırması başlatılıyor", queue.qsize())
        for process in processes:
            process.start()
            time.sleep(0.005)

        print(queue.qsize(), "tane dosya var")
        while len(processes) > 0:
            for i in processes:
                if not i.is_alive():
                    processes.remove(i)
            if queue.qsize() == 0:
                print(len(processes), "tane thread kaldı")
            else:
                print("%", 100 - int((queue.qsize() * 100 / old_size)))
                time.sleep(0.5)
            if self.stop:
                i = 0
                c = queue.qsize()
                b = time.time()
                while len(processes) > 0:
                    try:
                        a = queue.get_nowait()
                        i += 1
                        time.sleep(0.0001)
                    except _queue.Empty:
                        for pro in processes:
                            if not pro.is_alive():
                                processes.remove(pro)
                        print(len(processes))
                        time.sleep(0.1)
                print(
                    f"Kapatılma bitti. {c} işlem arasından {i} tane işlem iptal edildi. Bu işlem {time.time() - b}"
                    f" saniye sürdü")

        print(time.time() - ti)
        self.working = False
        if old_size > 0 and not self.stop:
            self.compile_compressed()
            print("Sıkıştırma tamamlandı")
        elif self.stop:
            self.stop = False
            print("İşlem iptal edildi")
            shutil.rmtree(self.rgl_file)
        else:
            print("Sıkıştırılacak dosya bulunamadı")

    def compile_compressed(self):
        with open(self.name + ".pcf", "wb") as compfile:
            print("Compiling files")
            for file in os.listdir(self.rgl_file):
                if file.endswith(".pcf"):
                    compfile.write(open(f"{self.rgl_file}{os.path.sep}{file}", "rb").read())
                else:
                    print(f"File named {file} is not ends with .pcf, your file had been deleted")
                safe_delete(f"{self.rgl_file}{os.path.sep}{file}")

        self.compression = 1
        shutil.rmtree(self.name)
        shutil.rmtree(self.rgl_file)
        self.name = self.name + ".pcf"
        self.__init__(self.name)
        print("tamamlandı")

    def set_rglfile(self):
        i = 1
        while True:
            if not os.path.exists(self.rgl_file):
                break
            else:
                self.rgl_file = f"RGL_compressed {i}"
                i += 1

    def decompress_file(self, file: File):
        with open(self.name, "rb") as mainfile:
            mainfile.seek(file.loc[0])
            data = gzip.decompress(mainfile.read(file.loc[1]))

        path = file.name[:-len(file.name.split(os.path.sep)[-1])]
        pathi = self.name[:-4]
        for directory in path.split(os.path.sep)[len(self.name.split(os.path.sep)):]:
            if not os.path.exists(pathi):
                os.mkdir(pathi)
            pathi += os.path.sep + directory
        open(file.name, "wb").write(data)

    def decompress(self):
        if not self.compression:
            raise TypeError("Can't compress a non-compressed directory")
        while not self.ready:
            if self.stop:
                return
            time.sleep(0.1)

        processes = []
        queue = Queue()
        print(self.name, "ayrıştırması başlatılıyor")
        for file in self.contents:
            queue.put((self.decompress_file, file))
        old_size = queue.qsize()
        for i in range(self.thread_count):
            processes.append(Process(target=self.decompressor_worker, args=(queue,), name="worker " + str(i)))
        ti = time.time()
        for process in processes:
            process.start()
            time.sleep(0.005)
        self.working = "Decompressing"
        print(queue.qsize(), "tane dosya var")
        while len(processes) > 0:
            for i in processes:
                if not i.is_alive():
                    processes.remove(i)
            if queue.qsize() == 0:
                print(len(processes), "tane thread kaldı", self.stop)
            else:
                print("%", 100 - int((queue.qsize() * 100 / old_size)), self.stop)

            if self.stop:
                i = 0
                c = queue.qsize()
                b = time.time()
                while len(processes) > 0:
                    try:
                        a = queue.get_nowait()
                        i += 1
                        time.sleep(0.0001)
                    except _queue.Empty:
                        for pro in processes:
                            if not pro.is_alive():
                                processes.remove(pro)
                        print(len(processes))
                        time.sleep(0.1)
                print(f"Kapatılma bitti. {c} işlem arasından {i} tane işlem iptal edildi. Bu işlem"
                      f" {round(time.time() - b)} saniye sürdü")

            time.sleep(1)

        self.working = False
        if self.stop:
            print("İşlem iptal edildi")
            shutil.rmtree(self.purename)
            self.stop = False
        else:
            safe_delete(self.name)
            self.name = self.name[:-4]
            self.compression = 0
            self.__init__(self.name)

        print(time.time() - ti)

    def decompressor_worker(self, queue: Queue):
        while not queue.empty():
            try:
                work = queue.get_nowait()
            except _queue.Empty:
                return
            if type(work) == tuple:
                args = work[1:]
                work = work[0]
                work(*args)
            else:
                work()
            time.sleep(0.1)

    def compressor_worker(self, queue: Queue):
        while not queue.empty():
            try:
                file = queue.get_nowait()
            except _queue.Empty:
                return
            file.compress(self.rgl_file)


def safe_delete(path, count=0):
    if count >= 5:
        print(f"Deleting {path} is failed")
        return False
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        return True
    except PermissionError:
        time.sleep(2)
        print(f"Permission error at {path}. Trying again...")
        return safe_delete(path, count + 1)


if __name__ == '__main__':
    debug = Directory(r"D:\TEST\BUFFER1\BUFFER2\BUFFER3\Democracy 4")


    def cancel():
        if debug.working is not False:
            debug.stop = True
            print("Kapatılma başlıyor")
        else:
            print("Çalışan görev yok")


    window = tk.Tk()

    tk.Label(text=debug.name).pack()
    tk.Button(text="Compress", command=lambda: daemon_and_start(debug.compress, "compress")).pack()
    tk.Button(text="Decompress", command=lambda: daemon_and_start(debug.decompress, "decompress")).pack()
    tk.Button(text="List", command=debug.list).pack()
    tk.Button(text="Terminate process", command=cancel).pack()
    tk.Button(text="compile", command=lambda: daemon_and_start(debug.compile_compressed, "compile")).pack()
    tk.Button(text="exit", command=sys.exit).pack()

    window.mainloop()

    """while True:
        print(debug.name)
        command = input("İşlem seçin")
        if command == "Compress" or command == "1":
            debug.compress()
        elif command == "Decompress" or command == "2":
            debug.decompress()
        elif command == "List" or command == "3":
            debug.list()
        elif command == "compile" or command == "4":
            if input("Are you sure Y/N") == "Y":
                debug.compile_Compressed()
        elif command == "exit" or command == "5":
            break"""
