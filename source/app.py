import json
import requests
import threading
import pandas as pd
from tkinter import *
from bs4 import BeautifulSoup
from tkinter import messagebox
from selenium import webdriver
from tkinter import filedialog
from time import sleep as pause
from tkinter.ttk import Combobox
from selenium.webdriver.common.by import By
from tkinter.filedialog import asksaveasfile
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException



# - > Variables < - #

running = False
researchs = 0
found = 0
not_found = 0
counter = 0
writer = ''



# - > Functions < - #

def copy_records():
    global label_records_text
    frame_right.clipboard_clear()
    frame_right.clipboard_append(label_records_text.cget('text'))
    messagebox.showinfo('Ready', "The content of the records was copied.")

def clear_records():
    global label_records_text
    label_records_text['text'] = ''

def save_records():
    global label_records_text
    file = filedialog.asksaveasfilename(filetypes=[('txt files', '*.txt')], defaultextension='.txt')
    fob = open(file, 'w')
    fob.write(label_records_text.cget('text'))
    fob.close()
    messagebox.showwarning('Successufully', 'File saved successfully')

def clear_eans():
    global text_eans
    text_eans.delete('1.0', 'end')

def cancel(who=''):
    global running
    running = False
    if who == 'app':
        messagebox.showerror('Error', 'Invalid data from EAN')
    else:
        messagebox.showwarning('Canceled Search!', 'You canceled the search.')

def start_():
    global site
    global writer 
    global counter
    global running
    global text_eans
    global label_records_text
    counter = 0
    eans = text_eans.get("1.0", "end").strip()
    if eans == '':
        cancel(who = 'app')
    file = open('ean.txt', 'r+')
    file.truncate(0)
    file.write(f'{eans}\n')
    file.close()
    if label_records_text['text'] == '':
        writer = 'EAN;IMG_1;IMG_2;IMG_3;IMG_4'
        label_records_text['text'] = writer
    while running:
        def init_search(ean):
            options = webdriver.EdgeOptions()
            options.add_argument('--log-level=3')
            driver = webdriver.Edge(options=options)
            driver.maximize_window()
            if site.get() == 'Leroy Merlin':
                website = 'https://www.leroymerlin.com.br/'
            driver.get(website)
            pause(5) 
            driver.find_element(By .CLASS_NAME, 'css-q8aty4-input').send_keys(ean)
            pause(1)
            driver.find_element(By .CLASS_NAME, 'css-1qvo8qb-search__button').click()
            pause(2)
            return driver
        def verification(driver):
            global researchs
            global found
            global not_found
            global label_stats_text
            try:
                div = driver.find_element(By .XPATH, '/html/body/div[6]/div[2]/div/div/div/div/h1')
                html = div.get_attribute('outerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                element = soup.text
                researchs = researchs + 1
                not_found = not_found + 1
                label_stats_text['text'] = label_stats_text['text'] = f'Researchs({researchs})     Found({found})    Not Found({not_found})' 
                return 'N'
            except NoSuchElementException:
                researchs = researchs + 1
                found = found + 1
                label_stats_text['text'] = label_stats_text['text'] = f'Researchs({researchs})     Found({found})    Not Found({not_found})'
                return 'Y'
        def scrapping(url, ean, writer):
            global label_records_text
            writer = label_records_text.cget('text')
            html = requests.get(url)
            soup = BeautifulSoup(html.content, 'html.parser')
            try:
                div = soup.find('div', attrs={'class':'carousel'})
                slides = div['data-items']
                items = json.loads(slides)
                lista = []
                for i in range(4):
                    try:
                        img_ = items[i]['url']
                        lista.append(img_)
                    except IndexError:
                        lista.append('#')
                label_records_text['text'] = f'{writer}\n{ean};{lista[0]};{lista[1]};{lista[2]};{lista[3]}'
            except TypeError:
                writer = label_records_text.cget('text')
                label_records_text['text'] = f'{writer}\n{ean};#;#;#;#'      
        try:
            file = open("ean.txt")
            content = file.readlines()
            content = [x.replace('\n', '') for x in content]
            ean = content[counter]
            counter = counter + 1
        except IndexError:
            messagebox.showinfo('Ready!', 'Action completed successfully!')
            break
        driver = init_search(ean=ean)
        response = verification(driver=driver)
        if response == 'Y':
            scrapping(url=driver.current_url, ean=ean, writer=writer)
        elif response == 'N':
            writer = label_records_text.cget('text')
            label_records_text['text'] = f'{writer}\n{ean};#;#;#;#'
        driver.quit()
    
def task_():
    global running
    task = threading.Thread(target=start_)
    running = True
    task.start()

def clear_stats():
    global researchs
    global found
    global not_found
    global label_stats_text
    researchs = 0
    found = 0 
    not_found = 0
    label_stats_text['text'] = f'Researchs({researchs})     Found({found})    Not Found({not_found})'



app = Tk()
app.config(bg='#ffffff')
app.geometry('1000x600')
app.title('ConstrawlerIMG')
app.resizable(width=False, height=False)
app.iconphoto(False, PhotoImage(file='icone.png'))

frame_left = Frame(app, bg='#ff8400', width=500, height=600)
frame_left.pack(side=LEFT)

frame_right = Frame(app, bg='#ffffff', width=500, height=600)
frame_right.pack(side=RIGHT)

label_constrawler = Label(frame_left, text='Constrawler', fg='#ffffff', bg='#ff8400', font=('Arial', 37, 'bold'), width=10, anchor=E)
label_constrawler.place(x=42, y=30)
label_img = Label(frame_left, text='IMG', fg='red', bg='#ff8400', font=('Arial', 37, 'bold'), width=3, anchor=W)
label_img.place(x=350, y=30)

label_site = Label(frame_left, text='SITE', fg='#ffffff', bg='#ff8400', font=('Arial', 12), width=4, anchor=W)
label_site.place(x=45, y=120)
site = StringVar()
combobox_site = Combobox(frame_left, width=15, font=('Arial', 12), textvariable=site)
combobox_site['values'] = ('Leroy Merlin',)
combobox_site.current(0)
combobox_site.place(x=45, y=155)

label_eans = Label(frame_left, text='EANs', fg='#ffffff', bg='#ff8400', font=('Arial', 12), width=5, anchor=W)
label_eans.place(x=45, y=220)
text_eans = Text(frame_left, relief=FLAT, bg='#ffffff', fg='#000000', width=57, height=9, font=('Arial', 10))
text_eans.place(x=45, y=255)
button_start = Button( frame_left, command=task_, width=22, text='START', fg='#ffffff', bg='#0cc93f', relief=FLAT, font=('Arial', 10), anchor='center')
button_start.place(x=45, y=415)
button_cancel = Button( frame_left, command=cancel, width=22, text='CANCEL', fg='#ffffff', bg='red', relief=FLAT, font=('Arial', 10), anchor='center')
button_cancel.place(x=263, y=415)
button_clear_eans = Button( frame_left, command=clear_eans, width=22, text='CLEAR', fg='#ffffff', bg='#05afe3', relief=FLAT, font=('Arial', 10), anchor='center')
button_clear_eans.place(x=263, y=215)

label_stats_text = Label(frame_left, relief=FLAT, bg='#000000', fg='#ffffff', width=44, height=4, font=('Arial', 12), text=f'Researchs({researchs})     Found({found})    Not Found({not_found})', anchor=CENTER)
label_stats_text.place(x=45, y=455)
button_clear_stats = Button( frame_left, command=clear_stats, width=49, text='CLEAR', fg='#ffffff', bg='#05afe3', relief=FLAT, font=('Arial', 10), anchor='center')
button_clear_stats.place(x=45, y=545)

label_records = Label(frame_right, text='Records', fg='#ff8400', bg='#ffffff', font=('Arial', 37, 'bold'), width=10, anchor=W)
label_records.place(x=32, y=30)
button_save = Button( frame_right, width=24, command=save_records, text='SAVE', fg='#ffffff', bg='#ff8400', relief=FLAT, font=('Arial', 10), anchor='center')
button_save.place(x=260, y=55)
label_records_text = Label(frame_right, relief=FLAT, bg='#000000', fg='#ffffff', width=44, height=22, font=('Arial', 12), text='', anchor=NW, padx=13, pady=13, wraplength=400)
label_records_text.place(x=38, y=95)
button_copy_records = Button( frame_right, command=copy_records, width=23, text='COPY', fg='#ffffff', bg='#04098a', relief=FLAT, font=('Arial', 10), anchor='center')
button_copy_records.place(x=39, y=535)
button_clear_records = Button( frame_right, command=clear_records, width=23, text='CLEAR', fg='#ffffff', bg='#05afe3', relief=FLAT, font=('Arial', 10), anchor='center')
button_clear_records.place(x=270, y=535)
label_ryancruz = Label(frame_right, text='© Ryan Cruz', fg='#ff8400', bg='#ffffff', font=('Arial', 10), width=15, anchor=W)
label_ryancruz.place(x=210, y=576)



# - > Running app < - #

app.mainloop()
