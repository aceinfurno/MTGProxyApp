#!/usr/bin/env python
import os
import os.path
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from PIL import ImageTk, Image
from fpdf import FPDF
import time

class Card(object):
    def __init__(self, fileName):
        self.fileName = fileName
        self.counts = 1

    def getImage(self):
        img = Image.open(self.fileName)
        img = img.resize((240, 336))
        img = ImageTk.PhotoImage(img)
        return img

    def increaseCounts(self):
        self.counts += 1

    def decreaseCounts(self):
        self.counts -= 1

class CardCell(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        self.plusbutton = ttk.Button(self, text='+', command=self.incrementCount)
        self.plusbutton.grid(column=2, columnspan=1, row=1)
        self.minusbutton = ttk.Button(self, text='-', command=self.decrementCount)
        self.minusbutton.grid(column=0, columnspan=1, row=1)
        self.countLabel = None
        self.card = None
        self.img = None
        self.label = None
        options = {'padx' : 5, 'pady' :30}

    def incrementCount(self):
        self.card.increaseCounts()
        self.countLabel.config(text=self.card.counts)

    def decrementCount(self):
        self.card.decreaseCounts()
        self.countLabel.config(text=self.card.counts)
        if self.card.counts <= 0:
            self.destroy()

    def addCard(self, card):
        self.card = card
        self.img = self.card.getImage()
        self.label = ttk.Label(self, image= self.img)
        self.label.grid(column=0, columnspan=3, row=0)
        self.countLabel = ttk.Label(self, text=self.card.counts)
        self.countLabel.grid(column=1, row=1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MTGProxy")
        self.geometry('600x600')

        self.cardCells = []
        self.mainframe = ttk.Frame(self)
        self.mainframe.pack(fill='both', expand=1)

        self.myCanvas = tk.Canvas(self.mainframe)
        self.myCanvas.pack(side='left', fill='both', expand=1)

        self.myScrollbar = ttk.Scrollbar(self.mainframe, orient='vertical', command=self.myCanvas.yview)
        self.myScrollbar.pack(side='right', fill='y')

        self.myCanvas.configure(yscrollcommand=self.myScrollbar.set)
        self.myCanvas.bind('<Configure>', lambda e: self.myCanvas.configure(scrollregion = self.myCanvas.bbox('all')))

        self.secondFrame = ttk.Frame(self.myCanvas)
        self.myCanvas.create_window((0, 0), window=self.secondFrame, anchor='nw')

        self.myCanvas.bind('<MouseWheel>', self._on_mousewheel)
        self.myButton = ttk.Button(self.secondFrame, text="get files")
        self.myButton.grid(column = 0, row=0)
        self.myButton['command'] = self.getFiles
        self.constructButton = ttk.Button(self.secondFrame, text='make pdf')
        self.constructButton.grid(column=1, row=0)
        self.constructButton['command'] = self.constructPdf
        self.bind('<ButtonRelease>', self.buttonPress)
        #grab file button
    def getFiles(self):
        myFiles = tk.filedialog.askopenfilenames(title = "Choose Card Images")
        for each in myFiles:
            if self.noDuplicates(each):
                newCard = Card(each)
                newCardCell = CardCell(self.secondFrame)
                newCardCell.addCard(newCard)
                self.cardCells.append(newCardCell)
        self.update()

    def constructPdf(self):
        card_x = 2.5
        card_y = 3.5
        pdf = FPDF('P', 'in', (8.5, 11))
        pdf.add_page()
        xmargin = .5
        ymargin = .25
        currentx = xmargin
        currenty = ymargin
        for cardprint in self.cardCells:
            count = 0
            img = cardprint.card.fileName
            while True:
                pdf.image(img, currentx, currenty, card_x, card_y)
                currentx += card_x
                if not (8.5 - currentx) < (card_x + xmargin):
                    count+=1
                    if count == cardprint.card.counts:
                        break
                else:
                    currenty += card_y
                    if not (11 - currenty) < (card_y + ymargin):
                        currentx = xmargin
                        count+=1
                        if count == cardprint.card.counts:
                            break
                    else:
                        pdf.add_page()
                        currentx = xmargin
                        currenty = ymargin
                        count+=1
                        if count == cardprint.card.counts:
                            break
        fileName = tk.filedialog.asksaveasfilename(title='MtgProxyPDF', defaultextension="pdf")
        pdf.output(fileName, 'F')

    def noDuplicates(self, cardFile):
        if self.cardCells:
            for each in self.cardCells:
                if cardFile in each.card.fileName:
                    return False
                else:
                    return True
        else:
            return True

    def _on_mousewheel(self, event):
        self.myCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def buttonPress(self, event):
        self.update()

    def update(self, event=None):
        x = 0
        y = 1
        for each in self.cardCells:
            if each.card.counts <= 0:
                self.cardCells.remove(each)
            else:
                each.grid(column = x, row = y, pady=20)
                x += 1
                if x >= 2:
                    x = 0
                    y += 1


if __name__ == "__main__":
    app = App()
    app.update()
    app.mainloop()
