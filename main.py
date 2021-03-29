################################################################################
# Main window via Tkinter
################################################################################

import buxfer

import datetime

from tkinter import *
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox
from tkcalendar import DateEntry

from settings import username, password

token = buxfer.login(username, password)
accounts = buxfer.get_accounts(token)

window = Tk()

window.title("Buxfer client")

menu = Menu(window)
new_item = Menu(menu)
new_item.add_command(label='New')
menu.add_cascade(label='File', menu=new_item)
window.config(menu=menu)

tab_control = ttk.Notebook(window)

tab1 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)

tab_control.add(tab1, text='Info')
tab_control.add(tab3, text='Add transaction')
tab_control.add(tab4, text='Add multiple transactions')

#####################################################################################

lbl = Label(tab1, text="Token: " + token, font=("Arial Bold", 10))
lbl.grid(column=0, row=0)

lbl2 = Label(tab1, text="Tags: [press \'Get tags\' button]", font=("Arial Bold", 10))
lbl2.grid(column=0, row=3)


def clicked():
    res = buxfer.get_tags(token)
    lbl2.configure(text=res, font=("Arial Bold", 10))


btn = Button(tab1, text="Get tags", bg="gray", fg="black", command=clicked)
btn.grid(column=1, row=1)


#####################################################################################
# Tab 3. Add transaction

ttk.Label(tab3, text='Description').grid(column=0, row=1)
ttk.Label(tab3, text='Amount').grid(column=1, row=1)
ttk.Label(tab3, text='Tag').grid(column=2, row=1)
ttk.Label(tab3, text='Account').grid(column=3, row=1)
ttk.Label(tab3, text='Choose date').grid(column=4, row=1)
ttk.Label(tab3, text='Status').grid(column=5, row=1)

descEntry = Entry(tab3, width=10)
descEntry.grid(column=0, row=2)

amountEntry = Entry(tab3, width=8)
amountEntry.grid(column=1, row=2)

tagEntry = Entry(tab3, width=30)
tagEntry.grid(column=2, row=2)

accountCombo = Combobox(tab3, state="readonly")
accountCombo['values'] = (accounts['name'].tolist())
accountCombo.current(6)  # set the selected item
accountCombo.grid(column=3, row=2)

cal = DateEntry(tab3, date_pattern='dd/mm/y',
                width=12, background='darkgray', foreground='white', borderwidth=2)
cal.grid(column=4, row=2)

statusCombo = Combobox(tab3, state="readonly", values=['cleared', 'pending'])
statusCombo.current(0)
statusCombo.grid(column=5, row=2)


def add_transaction_clicked():
    try:
        amount = float(amountEntry.get())
    except ValueError:
        messagebox.showerror("Error", "Amount should be a number")
        return

    account_id = accounts.iloc[accountCombo.current()]['id']
    date_str = datetime.datetime.strptime(cal.get(), "%d/%m/%Y").date().strftime('%Y-%m-%d')

    print(date_str)

    answer = messagebox.askokcancel("Confirm",
                                    "Do you want to add this transaction?\n" +
                                    descEntry.get() + "; " +
                                    "%.2f" % amount + "; " +
                                    tagEntry.get() + "; " +
                                    accountCombo.get() + "; " +
                                    date_str + "; " +
                                    statusCombo.get())
    if answer:
        buxfer.add_transaction(token, descEntry.get(), "%.2f" % amount,
                               "%d" % account_id, date_str, tags=tagEntry.get(), type='expense',
                               status=statusCombo.get())
        print("Transaction sent!")
    else:
        print("Transaction cancelled!")


addTransBtn = Button(tab3, text="Add transaction", bg="gray", fg="black", command=add_transaction_clicked)
addTransBtn.grid(column=3, row=0)

#####################################################################################
# Tab 4. Add multiple transactions

totalSumLbl = Label(tab4, text='Total sum: 0.00')
totalSumLbl.grid(column=4, row=0)

ttk.Label(tab4, text='Account').grid(column=4, row=1)
ttk.Label(tab4, text='Choose date').grid(column=5, row=1)
ttk.Label(tab4, text='Status').grid(column=6, row=1)


def add_item_clicked():
    item = Item(parent=frame)
    items.append(item)


addItemBtn = Button(tab4, text="Add item", bg="gray", fg="black", command=add_item_clicked)
addItemBtn.grid(column=1, row=0)


def remove_item_clicked():
    if len(items) > 1:
        item = items.pop(len(items) - 1)
        item.numLbl.destroy()
        item.descEntry.destroy()
        item.amountEntry.destroy()
        item.tagEntry.destroy()
        Item.row -= 1
    set_total_sum(0, 0, 0)


remItemBtn = Button(tab4, text="Remove item", bg="gray", fg="black", command=remove_item_clicked)
remItemBtn.grid(column=2, row=0)

accountMultiCombo = Combobox(tab4, state="readonly")
accountMultiCombo['values'] = (accounts['name'].tolist())
accountMultiCombo.current(6)  # set the selected item
accountMultiCombo.grid(column=4, row=2)

calMulti = DateEntry(tab4, date_pattern='dd/mm/y',
                     width=12, background='darkgray', foreground='white', borderwidth=2)
calMulti.grid(column=5, row=2)

statusMultiCombo = Combobox(tab4, state="readonly", values=['cleared', 'pending'])
statusMultiCombo.current(0)
statusMultiCombo.grid(column=6, row=2)


def add_multiple_transactions_clicked():
    # Do some checks first
    for item in items:
        # Check description
        if len(item.get_desc().get()) == 0:
            messagebox.showerror("Error", "Check item " + "%d" % (item.numLbl['text']) +
                                 ": missing description!")
            return

        # Check amount
        try:
            item.get_amount().get()
        except TclError:
            messagebox.showerror("Error", "Check item " + "%d" % (item.numLbl['text']) +
                                 ": amount should be a number!")
            return

    answer = messagebox.askokcancel("Confirm", "Do you want to add this transaction?")

    for item in items:
        amount = item.get_amount().get()
        account_id = accounts.iloc[accountMultiCombo.current()]['id']
        date_str = datetime.datetime.strptime(calMulti.get(), "%d/%m/%Y").date().strftime('%Y-%m-%d')

        tr_type = 'expense'
        if amount < 0:
            tr_type = 'refund'

        if answer:
            buxfer.add_transaction(token, item.get_desc().get(), "%.2f" % amount,
                                   "%d" % account_id, date_str, tags=item.get_tag().get(), type=tr_type,
                                   status=statusMultiCombo.get())
            print("Transaction sent!")
        else:
            print("Transaction cancelled!")


addMultiTransBtn = Button(tab4, text="Add transaction", bg="gray", fg="black",
                          command=add_multiple_transactions_clicked)
addMultiTransBtn.grid(column=6, row=0)

items = []


def set_total_sum(name, index, mode):
    res = 0.0
    for item in items:
        try:
            dv = item.get_amount()
            res += dv.get()
            item.amountEntry.config(bg="white")
        except TclError:
            item.amountEntry.config(bg="pink")
    totalSumLbl['text'] = 'Total sum: ' + "%.2f" % res


class Item:
    row = 2

    def __init__(self, parent):
        self.numLbl = ttk.Label(parent, text=self.row - 1)
        self.numLbl.grid(column=0, row=self.row)

        self.descEntry = Entry(parent, width=30)
        self.descEntry.grid(column=1, row=self.row)

        self.amountVar = DoubleVar(0)
        self.amountVar.trace('w', set_total_sum)

        self.amountEntry = Entry(parent, width=8, textvariable=self.amountVar)
        self.amountEntry.grid(column=2, row=self.row)

        self.tagEntry = Entry(parent, width=20)
        self.tagEntry.grid(column=3, row=self.row)

        Item.row += 1

    def get_desc(self):
        return self.descEntry

    def get_amount(self):
        return self.amountVar

    def get_tag(self):
        return self.tagEntry


def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"), width=400, height=300)


def _on_mousewheel(event):
    canvas.yview_scroll(-1*(event.delta/120), "units")


myframe=Frame(tab4, relief=GROOVE, width=50, height=100, bd=1) # TODO: check dimensions
myframe.grid(column=0, row=2, rowspan=10, columnspan=3)

canvas = Canvas(myframe)
frame = Frame(canvas)
myscrollbar = Scrollbar(myframe, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=myscrollbar.set)
# canvas.bind_all("<MouseWheel>", _on_mousewheel)

myscrollbar.grid(column=4, row=1, rowspan=10, columnspan=1)
canvas.grid(column=0, row=2, rowspan=10, columnspan=3)
canvas.create_window((0, 0), window=frame, anchor='nw')
frame.bind("<Configure>", myfunction)

ttk.Label(frame, text='Description').grid(column=1, row=0)
ttk.Label(frame, text='Amount').grid(column=2, row=0)
ttk.Label(frame, text='Tag').grid(column=3, row=0)

# item1 = Item(parent=tab4)
item1 = Item(parent=frame)
items.append(item1)




#####################################################################################


tab_control.pack(expand=1, fill='both')
window.geometry('820x400')

window.mainloop()
