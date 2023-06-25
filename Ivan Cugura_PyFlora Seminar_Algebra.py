import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import sqlite3
from PIL import ImageTk, Image
import requests
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime as dt
import os


class App:
    def __init__(self, root):
        #   Setting main window for login

        def callback(event):
            self.button_login_command()
        root.bind('<Return>', callback)

        root.title("PyFlora Log")
        # Setting window size
        width = 242
        height = 126
        screenwidth = root.winfo_screenwidth()  # dohvaća širinu ekrana na kojem se izvršava aplikacija
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)      # Ova linija koda stvara niz znakova (string) koji predstavlja veličinu i poziciju prozora na ekranu. %dx%d označava da će se u taj niz umetnuti vrijednosti width (širina prozora) i height (visina prozora). Izraz (screenwidth - width) / 2 izračunava horizontalnu poziciju prozora tako da se postavi u sredinu ekrana, a (screenheight - height) / 2 izračunava vertikalnu poziciju prozora tako da se postavi u sredinu ekrana.
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        # Username label
        self.label_username = tk.Label(root)
        self.label_username["anchor"] = "w"
        ft = tkFont.Font(family='Times', size=10)
        self.label_username["font"] = ft
        self.label_username["fg"] = "#333333"
        self.label_username["justify"] = "left"
        self.label_username["text"] = "Enter username:"
        self.label_username.place(x=0, y=10, width=101, height=30)

        # Username entry
        self.entry_username = tk.Entry(root)
        self.entry_username["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_username["font"] = ft
        self.entry_username["fg"] = "#333333"
        self.entry_username["justify"] = "center"
        self.entry_username["text"] = "username"
        self.entry_username.focus_set()
        self.entry_username.place(x=110,y=10,width=119,height=30)

        # Password label
        self.label_password = tk.Label(root)
        self.label_password["anchor"] = "w"
        ft = tkFont.Font(family='Times',size=10)
        self.label_password["font"] = ft
        self.label_password["fg"] = "#333333"
        self.label_password["justify"] = "left"
        self.label_password["text"] = "Enter password:"
        self.label_password.place(x=0,y=40,width=92,height=30)

        # Password entry
        self.entry_password = tk.Entry(root)
        self.entry_password["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_password["font"] = ft
        self.entry_password["fg"] = "#333333"
        self.entry_password["justify"] = "center"
        self.entry_password["text"] = "password"
        self.entry_password["show"] = "*"
        self.entry_password.place(x=110,y=50,width=120,height=30)

        # Login button
        self.button_login = tk.Button(root)
        self.button_login["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        self.button_login["font"] = ft
        self.button_login["fg"] = "#000000"
        self.button_login["justify"] = "center"
        self.button_login["text"] = "Log in"
        self.button_login.place(x=10,y=90,width=128,height=30)
        self.button_login["command"] = self.button_login_command

        # show/hide check button
        self.show_hide_var = tk.BooleanVar()
        self.checkbox_show_hide_pass = tk.Checkbutton(root, variable=self.show_hide_var)
        ft = tkFont.Font(family='Times',size=10)
        self.checkbox_show_hide_pass["font"] = ft
        self.checkbox_show_hide_pass["fg"] = "#333333"
        self.checkbox_show_hide_pass["justify"] = "right"
        self.checkbox_show_hide_pass["text"] = "show"
        self.checkbox_show_hide_pass["offvalue"] = "0"
        self.checkbox_show_hide_pass["onvalue"] = "1"
        self.checkbox_show_hide_pass["command"] = self.checkbox_show_hide_command
        self.checkbox_show_hide_pass.place(x=150, y=90, width=70, height=25)

    def button_login_command(self):
        """provjerava ispravnost username i password"""
        username, password = self.get_credentials()
        if self.entry_username.get() == username and \
                self.entry_password.get() == password:
            self.open_new_window()
        else:
            messagebox.showinfo(title="PyFlora Log Error",
                                message="Invalid username or password")
            self.entry_username.delete(0, "end")
            self.entry_password.delete(0, "end")
            self.entry_username.focus_set()

    def get_credentials(self):
        """dobavlja vrijednosti username i password iz baze"""
        with sqlite3.connect("inventory.db") as conn:
            c = conn.cursor()
            c.execute("SELECT username, password FROM login")
            fetch = c.fetchall()[0]
            username = fetch[0]
            password = fetch[1]
        return username, password

    def checkbox_show_hide_command(self):
        """pokazuje ili sakriva karaktere u password entry"""
        if self.show_hide_var.get() == 0:
            self.entry_password.config(show="*")
        else:
            self.entry_password.config(show="")

    def open_new_window(self):
        """glavni prozor -> otvara se nakon logina"""

        def refresh_plant():
            """
            insert plant name in listbox

            uzima iz baze i stavlja u listbox plant
            """
            try:
                with sqlite3.connect("inventory.db") as conn:
                    c = conn.cursor()
                    c.execute("SELECT * FROM plant")
                    rows = c.fetchall()
                    self.listbox_plant.delete(0, END)
                    for row in rows:
                        plant_name = row[0]
                        self.listbox_plant.insert("end", plant_name)

            except Exception as e:
                raise e

        def refresh_pot():
            """insert pot name in listbox

            uzima iz baze i stavlja u listbox pot
            """
            try:
                with sqlite3.connect("inventory.db") as conn:
                    c = conn.cursor()
                    c.execute("SELECT name FROM pot")
                    rows = c.fetchall()
                    self.listbox_pot.delete(0, END)
                    for row in rows:
                        self.listbox_pot.insert("end", row)
            except Exception as e:
                raise e

        def create_plant_command():
            """dodavanje i ažuriranje biljke_osnovni text

            return entry_name, textfield, entry_temp, entry_acid, entry_light, entry_humidity
            """

            add_plant_window = tk.Toplevel()
            add_plant_window.title("Add plant")
            add_plant_window.minsize(600, 600)

            #   plant name
            label_name = tk.Label(add_plant_window, text="New plant")
            label_name.place(x=150, y=20)
            entry_name = tk.Entry(add_plant_window, justify="center")
            entry_name.place(x=250, y=20)

            #   plant humidity
            label_humidity = tk.Label(add_plant_window, text="Plant humidity")
            label_humidity.place(x=150, y=50)
            entry_humidity = tk.Entry(add_plant_window, justify="center")
            entry_humidity.place(x=250, y=50)

            #   plant light
            label_light = tk.Label(add_plant_window, text="Plant light")
            label_light.place(x=150, y=80)
            entry_light = tk.Entry(add_plant_window, justify="center")
            entry_light.place(x=250, y=80)

            #   plant temperature
            label_temp = tk.Label(add_plant_window, text="Plant temperature")
            label_temp.place(x=150, y=110)
            entry_temp = tk.Entry(add_plant_window, justify="center")
            entry_temp.place(x=250, y=110)

            #   plant acidity
            label_acid = tk.Label(add_plant_window, text="Plant acidity")
            label_acid.place(x=150, y=140)
            entry_acid = tk.Entry(add_plant_window, justify="center")
            entry_acid.place(x=250, y=140)

            textfield = ScrolledText(add_plant_window, height=20, width=60)
            textfield.place(x=30, y=200)

            # new plant - dodavanje u bazu
            def get_entry_data():
                """dobavlja podatke iz entry i sprema u bazu"""
                ent_name = entry_name.get()
                ent_textfield = textfield.get("1.0", "end")
                ent_textfield = ent_textfield.rstrip()
                ent_temp = entry_temp.get()
                ent_acid = entry_acid.get()
                ent_light = entry_light.get()
                ent_hum = entry_humidity.get()

                try:
                    with sqlite3.connect("inventory.db") as conn:
                        c = conn.cursor()

                        c.execute("INSERT INTO plant (name, description, temperature, ph, light, humidity)"
                                  "VALUES (?, ?, ?, ?, ?, ?)",
                                  (ent_name, ent_textfield, ent_temp, ent_acid, ent_light, ent_hum))
                        conn.commit()

                except Exception as e:
                    raise e

                refresh_plant()
                add_plant_window.destroy()

                return ent_name, ent_textfield, ent_temp, ent_acid, ent_light, ent_hum

            refresh_plant()
            button_save_new_plant = tk.Button(add_plant_window, text="Save new plant", command=get_entry_data)
            button_save_new_plant.place(x=10, y=550)

        def update_plant_command():
            """ažuriranje biljke"""

            data = selected_item_listbox_plant()
            # dohvaćanje označene biljke koju se želi ažurirati
            for i in self.listbox_plant.curselection():
                name_plant = self.listbox_plant.get(i)

            update_plant_window = tk.Toplevel()
            update_plant_window.title("Update plant info")
            update_plant_window.minsize(400, 400)

            # Update plant info
            label_update_name = tk.Label(update_plant_window, text="Update plant name: ")
            label_update_name.pack()
            entry_update_name = tk.Entry(update_plant_window)
            entry_update_name.pack()
            entry_update_name.focus()
            entry_update_name.insert(0, data[0])

            def delete_name(event):
                entry_update_name.delete(0, END)
            entry_update_name.bind("<Button-1>", delete_name)

            label_update_desc = tk.Label(update_plant_window, text="Update plant description: ")
            label_update_desc.pack()
            entry_update_desc = tk.Entry(update_plant_window)
            entry_update_desc.pack()
            entry_update_desc.insert(0, data[1])

            def delete_desc(event):
                entry_update_desc.delete(0, END)
            entry_update_desc.bind("<Button-1>", delete_desc)

            label_update_temp = tk.Label(update_plant_window, text="Update plant temperature: ")
            label_update_temp.pack()
            entry_update_temp = tk.Entry(update_plant_window)
            entry_update_temp.pack()
            entry_update_temp.insert(0, data[2])

            def delete_temp(event):
                entry_update_temp.delete(0, END)
            entry_update_temp.bind("<Button-1>", delete_temp)

            label_update_ph = tk.Label(update_plant_window, text="Update plant pH: ")
            label_update_ph.pack()
            entry_update_ph = tk.Entry(update_plant_window)
            entry_update_ph.pack()
            entry_update_ph.insert(0, data[3])

            def delete_ph(event):
                entry_update_ph.delete(0, END)
            entry_update_ph.bind("<Button-1>", delete_ph)

            label_update_light = tk.Label(update_plant_window, text="Update plant light: ")
            label_update_light.pack()
            entry_update_light = tk.Entry(update_plant_window)
            entry_update_light.pack()
            entry_update_light.insert(0, data[4])

            def delete_light(event):
                entry_update_light.delete(0, END)
            entry_update_light.bind("<Button-1>", delete_light)

            label_update_humidity = tk.Label(update_plant_window, text="Update plant humidity: ")
            label_update_humidity.pack()
            entry_update_humidity = tk.Entry(update_plant_window)
            entry_update_humidity.pack()
            entry_update_humidity.insert(0, data[5])

            def delete_humidity(event):
                entry_update_humidity.delete(0, END)
            entry_update_humidity.bind("<Button-1>", delete_humidity)

            def update_plant_data():
                """ažurira bazu prema entry"""
                update_name = entry_update_name.get()
                update_desc = entry_update_desc.get()
                update_temp = entry_update_temp.get()
                update_ph = entry_update_ph.get()
                update_light = entry_update_light.get()
                update_humidity = entry_update_humidity.get()

                try:
                    with sqlite3.connect("inventory.db") as conn:
                        c = conn.cursor()
                        c.execute("UPDATE plant SET name=?,description=?,temperature=?,ph=?,light=?,humidity=?"
                                  "WHERE name=?",
                                  (update_name, update_desc, update_temp, update_ph, update_light, update_humidity,
                                   name_plant))
                        conn.commit()
                except Exception as e:
                    raise e
                refresh_plant()
                update_plant_window.destroy()

            # refresh_plant()
            button_save_update = tk.Button(update_plant_window, text="Save changes", command=update_plant_data)
            button_save_update.pack()

        def delete_plant_command():
            for i in self.listbox_plant.curselection():
                name_plant = self.listbox_plant.get(i)
                try:
                    with sqlite3.connect("inventory.db") as conn:
                        c = conn.cursor()
                        c.execute("DELETE FROM plant WHERE name=?", (name_plant,))
                except Exception as e:
                    raise e
            refresh_plant()

        def create_pot_command():
            """dodavanje nove posude"""
            add_pot_window = tk.Toplevel()
            add_pot_window.title("Add new pot")
            add_pot_window.minsize(400, 400)

            #   label, entry i button pot
            label_pot = tk.Label(add_pot_window, text="Add a name")
            label_pot.place(x=20, y=20)
            entry_pot = tk.Entry(add_pot_window)
            entry_pot.place(x=110, y=20)

            label_choose_plant = tk.Label(add_pot_window, text="Choose a plant")
            label_choose_plant.place(x=20, y=50)
            listbox_pot_choose_plant = tk.Listbox(add_pot_window,
                                                  selectmode="single")
            listbox_pot_choose_plant.place(x=110, y=50)

            # odabir imena biljaka iz baze u listbox
            def refresh_plant_in_pot():
                try:
                    with sqlite3.connect("inventory.db") as conn:
                        c = conn.cursor()
                        c.execute("SELECT * FROM plant")
                        rows = c.fetchall()
                        listbox_pot_choose_plant.delete(0, END)
                        for row in rows:
                            plant_name = row[0]
                            listbox_pot_choose_plant.insert("end", plant_name)

                except Exception as e:
                    raise e

            refresh_plant_in_pot()
            refresh_pot()

            label_pot_location = tk.Label(add_pot_window, text="Location")
            label_pot_location.place(x=20, y=300)
            textbox_pot_location = tk.Text(add_pot_window, height=1, width=10)
            textbox_pot_location.place(x=110, y=300)

            def get_pot_data_new():
                new_pot_name = entry_pot.get()
                new_pot_location = textbox_pot_location.get("1.0", "end").strip()

                for i in listbox_pot_choose_plant.curselection():
                    name_plant_pot = listbox_pot_choose_plant.get(i)

                    try:
                        with sqlite3.connect("inventory.db") as conn:
                            c = conn.cursor()
                            c.execute("INSERT INTO pot (name, plant, location)"
                                      "VALUES (?,?,?)", (new_pot_name, name_plant_pot, new_pot_location))
                            conn.commit()
                    except Exception as e:
                        raise e

                refresh_pot()
                add_pot_window.destroy()

            button_save_pot = tk.Button(add_pot_window, text="Save new pot", command=get_pot_data_new)
            button_save_pot.place(x=70, y=350)

        def update_pot_command():
            """azuriranje posude"""
            for i in self.listbox_pot.curselection():
                name_pot_update = self.listbox_pot.get(i)[0]

                update_pot_window = tk.Toplevel()
                update_pot_window.title("Update pot")
                update_pot_window.minsize(400, 400)

                #   label, entry i button pot
                label_pot_update = tk.Label(update_pot_window, text="Update name: ")
                label_pot_update.place(x=20, y=20)
                entry_pot_update = tk.Entry(update_pot_window)
                entry_pot_update.place(x=110, y=20)

                label_choose_plant_update = tk.Label(update_pot_window, text="Choose a plant")
                label_choose_plant_update.place(x=20, y=50)
                listbox_pot_choose_plant_update = tk.Listbox(update_pot_window,
                                                      selectmode="single")
                listbox_pot_choose_plant_update.place(x=110, y=50)

                def refresh_plant_in_pot_update():
                    try:
                        with sqlite3.connect("inventory.db") as conn:
                            c = conn.cursor()
                            c.execute("SELECT * FROM plant")
                            rows = c.fetchall()
                            listbox_pot_choose_plant_update.delete(0, END)
                            for row in rows:
                                plant_name = row[0]
                                listbox_pot_choose_plant_update.insert("end", plant_name)

                    except Exception as e:
                        raise e

                    refresh_pot()

                refresh_plant_in_pot_update()
                refresh_pot()

                label_pot_location_update = tk.Label(update_pot_window, text="Location")
                label_pot_location_update.place(x=20, y=300)
                textbox_pot_location_update = tk.Text(update_pot_window, height=1, width=10)
                textbox_pot_location_update.place(x=110, y=300)
                insert_text = "Zagreb"
                textbox_pot_location_update.insert("end-1c", insert_text)                       # "end" stvara novi red

                def get_pot_data_update():
                    new_pot_name = entry_pot_update.get()
                    new_pot_location = textbox_pot_location_update.get("1.0", "end-1c")         # "end" stvara novi red
                    new_pot_location.strip()

                    for i in listbox_pot_choose_plant_update.curselection():
                        name_plant = listbox_pot_choose_plant_update.get(i)

                        try:
                            with sqlite3.connect("inventory.db") as conn:
                                c = conn.cursor()
                                c.execute("UPDATE pot SET name=?, plant=?, location=? WHERE name=?",
                                          (new_pot_name, name_plant, new_pot_location, name_pot_update))

                                conn.commit()
                        except Exception as e:
                            raise e

                    refresh_pot()
                    update_pot_window.destroy()
                    # refresh_plant_in_pot()

                button_save_pot = tk.Button(update_pot_window, text="Save updated pot", command=get_pot_data_update)
                button_save_pot.place(x=70, y=350)

        def delete_pot_command():
            data_plant_pot = self.listbox_pot.curselection()[0]
            name_plant_pot = self.listbox_pot.get(data_plant_pot)

            try:
                with sqlite3.connect("inventory.db") as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM pot WHERE name=?", name_plant_pot)
            except Exception as e:
                raise e
            refresh_pot()

        def command_button_refresh():
            selection = self.listbox_pot.curselection()
            if selection:
                location = "Zagreb"
                temp, humidity, light, ph = self.plant_temp(location)
                self.insert_meteo_data(location, temp, humidity, light, ph)
                pot_data = selected_item_listbox_pot()
                meteo_data = self.get_meteo_data(pot_data[2].strip())
                load_and_display_image_temp(meteo_data, pot_data)
                update_labels_pot(pot_data, meteo_data)
            else:
                print("Nije ništa označeno")

        new_window = tk.Toplevel(root)
        new_window.title("PyFlora Cugura")

        # Setting window size
        width = 600
        height = 500
        screenwidth = new_window.winfo_screenwidth()
        screenheight = new_window.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        new_window.geometry(alignstr)
        new_window.resizable(width=False, height=False)

        # Plant listbox
        self.listbox_plant = tk.Listbox(new_window)
        self.listbox_plant["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times', size=10)
        self.listbox_plant["font"] = ft
        self.listbox_plant["fg"] = "#333333"
        self.listbox_plant["justify"] = "center"
        self.listbox_plant.place(x=20, y=110, width=80, height=300)
        self.listbox_plant["exportselection"] = "0"
        self.listbox_plant["selectmode"] = "single"

        # Plant listbox select -> plant info
        def plant_selected(event):
            plant_data = selected_item_listbox_plant()
            image_name = f'{plant_data[0]}.jpg'

            if not os.path.exists(image_name):
                image_name = "empty_pot.png"

            load_and_display_image(image_name)
            selected_item_listbox_plant()
            update_labels_plant()
        self.listbox_plant.bind('<<ListboxSelect>>', plant_selected)

        # Plant label
        self.label_plant = tk.Label(new_window)
        ft = tkFont.Font(family='Times', size=10)
        self.label_plant["font"] = ft
        self.label_plant["fg"] = "#333333"
        self.label_plant["justify"] = "center"
        self.label_plant["text"] = "Plant"
        self.label_plant.place(x=25, y=60, width=80, height=25)

        # Pot listbox
        self.listbox_pot = tk.Listbox(new_window)
        self.listbox_pot["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times', size=10)
        self.listbox_pot["font"] = ft
        self.listbox_pot["fg"] = "#333333"
        self.listbox_pot["justify"] = "center"
        self.listbox_pot.place(x=500, y=110, width=80, height=300)
        self.listbox_pot["selectmode"] = "single"

        # Pot listbox select -> plant info
        def pot_selected(event):
            pot_data = selected_item_listbox_pot()
            meteo_data = self.get_meteo_data(pot_data[2].strip())
            load_and_display_image_temp(pot_meteo_data=meteo_data, pot_data=pot_data)
            update_labels_pot(pot_data, meteo_data)
        self.listbox_pot.bind('<<ListboxSelect>>', pot_selected)

        # Pot label
        self.label_pot = tk.Label(new_window)
        ft = tkFont.Font(family='Times', size=10)
        self.label_pot["font"] = ft
        self.label_pot["fg"] = "#333333"
        self.label_pot["justify"] = "center"
        self.label_pot["text"] = "Pot"
        self.label_pot.place(x=500, y=60, width=80, height=25)

        # Plant label -> above buttons
        self.label_plant = tk.Label(new_window)
        self.label_plant["text"] = "Plant"
        self.label_plant.place(x=80, y=430)

        # Plant create button
        self.button_add_plant = tk.Button(new_window)
        self.button_add_plant["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=10)
        self.button_add_plant["font"] = ft
        self.button_add_plant["fg"] = "#000000"
        self.button_add_plant["justify"] = "center"
        self.button_add_plant["text"] = "Create"
        self.button_add_plant.place(x=20, y=450, width=50, height=30)
        self.button_add_plant["command"] = create_plant_command

        # Plant update button
        self.button_update_plant = tk.Button(new_window)
        self.button_update_plant["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=10)
        self.button_update_plant["font"] = ft
        self.button_update_plant["fg"] = "#000000"
        self.button_update_plant["justify"] = "center"
        self.button_update_plant["text"] = "Update"
        self.button_update_plant.place(x=70, y=450, width=50, height=30)
        self.button_update_plant["command"] = update_plant_command

        # Plant delete button
        self.button_delete_plant = tk.Button(new_window)
        self.button_delete_plant["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=10)
        self.button_delete_plant["font"] = ft
        self.button_delete_plant["fg"] = "#000000"
        self.button_delete_plant["justify"] = "center"
        self.button_delete_plant["text"] = "Delete"
        self.button_delete_plant.place(x=120, y=450, width=50, height=30)
        self.button_delete_plant["command"] = delete_plant_command

        # button refresh (očitaj vrijednosti)
        self.button_refresh_meteo = tk.Button(new_window, text="Refresh meteo",
                                              command=command_button_refresh)
        self.button_refresh_meteo.place(x=200, y=450, height=30, width=110)

        # Pot label -> above buttons
        self.label_plant = tk.Label(new_window)
        self.label_plant["text"] = "Pot"
        self.label_plant.place(x=500, y=430)

        # Pot create button
        self.button_add_pot = tk.Button(new_window)
        self.button_add_pot["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=10)
        self.button_add_pot["font"] = ft
        self.button_add_pot["fg"] = "#000000"
        self.button_add_pot["justify"] = "center"
        self.button_add_pot["text"] = "Create"
        self.button_add_pot.place(x=430, y=450, width=50, height=30)
        self.button_add_pot["command"] = create_pot_command

        # Pot update button
        self.button_add_pot = tk.Button(new_window)
        self.button_add_pot["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=10)
        self.button_add_pot["font"] = ft
        self.button_add_pot["fg"] = "#000000"
        self.button_add_pot["justify"] = "center"
        self.button_add_pot["text"] = "Update"
        self.button_add_pot.place(x=480, y=450, width=50, height=30)
        self.button_add_pot["command"] = update_pot_command

        # Pot delete button
        self.button_add_pot = tk.Button(new_window)
        self.button_add_pot["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=10)
        self.button_add_pot["font"] = ft
        self.button_add_pot["fg"] = "#000000"
        self.button_add_pot["justify"] = "center"
        self.button_add_pot["text"] = "Delete"
        self.button_add_pot.place(x=530, y=450, width=50, height=30)
        self.button_add_pot["command"] = delete_pot_command

        # Plant frame -> info
        self.label_frame_plant = tk.Label(new_window, text="Plant info")
        self.label_frame_plant.place(x=120, y=10)
        self.frame_plant = tk.Frame(new_window, width=350, height=190, bg="white", padx=5, pady=5, borderwidth=5)
        self.frame_plant.place(x=125, y=30)

        frameplant_label_name = tk.Label(self.frame_plant, text="PLANT NAME")
        frameplant_label_name.place(x=120, y=1)

        frameplant_label_desc = tk.Label(self.frame_plant, text=f"Description: ")
        frameplant_label_desc.place(x=5, y=20)

        frameplant_label_temp = tk.Label(self.frame_plant, text=f"Desired temp: ")
        frameplant_label_temp.place(x=5, y=40)

        frameplant_label_ph = tk.Label(self.frame_plant, text=f"Desired pH:")
        frameplant_label_ph.place(x=5, y=60)

        frameplant_label_light = tk.Label(self.frame_plant, text=f"Desired light:")
        frameplant_label_light.place(x=5, y=80)

        frameplant_label_humidity = tk.Label(self.frame_plant,
                                             text=f"Desired humidity: ")
        frameplant_label_humidity.place(x=5, y=100)

        # Plant frame -> picture
        frame_picture = tk.Frame(master=self.frame_plant, width=100, height=120)
        frame_picture.place(x=180, y=50)

        pic_label_plant = tk.Label(frame_picture)
        pic_label_plant.place(x=0, y=0)

        def load_and_display_image(image_name):
            """dodavanje slike biljke"""
            image = Image.open(image_name)
            resized_image = image.resize((100, 120), resample=Image.LANCZOS)
            pic = ImageTk.PhotoImage(resized_image)
            pic_label_plant.configure(image=pic)
            pic_label_plant.image = pic

        # Pot frame -> info (real and random values)
        self.label_frame_pot = tk.Label(new_window, text="Pot info")
        self.label_frame_pot.place(x=120, y=230)
        self.frame_pot = tk.Frame(new_window, width=350, height=190, bg="white", padx=5, pady=5)
        self.frame_pot.place(x=125, y=250)

        label_pot_name = tk.Label(self.frame_pot, text=f"Pot name: ")
        label_pot_name.place(x=120, y=1)

        label_pot_plant_name = tk.Label(self.frame_pot, text=f"Plant in pot: ")
        label_pot_plant_name.place(x=5, y=20)

        label_pot_temp = tk.Label(self.frame_pot, text=f"Plant Temp:")
        label_pot_temp.place(x=5, y=40)

        label_pot_ph = tk.Label(self.frame_pot, text=f"Pot pH: ")
        label_pot_ph.place(x=5, y=60)

        label_pot_light = tk.Label(self.frame_pot, text=f"Pot light:")
        label_pot_light.place(x=5, y=80)

        label_pot_humidity = tk.Label(self.frame_pot, text=f"Pot humidity:")
        label_pot_humidity.place(x=5, y=100)

        label_pot_location = tk.Label(self.frame_pot, text=f"Pot spot: ")
        label_pot_location.place(x=5, y=120)

        # Pot frame -> picture (temp, light, water, ph)

        # temp
        frame_picture_temp = tk.Frame(master=self.frame_pot, width=50, height=60)
        frame_picture_temp.place(x=180, y=30)

        pic_label_pot = tk.Label(frame_picture_temp)
        pic_label_pot.place(x=0, y=0)

        # light
        frame_picture_light = tk.Frame(master=self.frame_pot, width=50, height=60)
        frame_picture_light.place(x=250, y=30)

        pic_label_pot_light = tk.Label(frame_picture_light)
        pic_label_pot_light.place(x=0, y=0)

        # water
        frame_picture_water = tk.Frame(master=self.frame_pot, width=50, height=60)
        frame_picture_water.place(x=180, y=100)

        pic_label_pot_water = tk.Label(frame_picture_water)
        pic_label_pot_water.place(x=0, y=0)

        # food
        frame_picture_food = tk.Frame(master=self.frame_pot, width=50, height=60)
        frame_picture_food.place(x=250, y=100)

        pic_label_pot_food = tk.Label(frame_picture_food)
        pic_label_pot_food.place(x=0, y=0)

        def load_and_display_image_temp(pot_meteo_data, pot_data):
            """dodavanje slika za temp, kiselost, svjetlost, vlažnost"""
            plant_name = pot_data[1]

            try:
                with sqlite3.connect("inventory.db") as conn:
                    c = conn.cursor()
                    c.execute("SELECT * FROM plant WHERE name=?", (plant_name,))
                    fetch = c.fetchall()[0]
                    temp_fetch = fetch[2]
                    acid_fetch = fetch[3]
                    light_fetch = fetch[4]
                    humidity_fetch = fetch[5]
            except Exception as e:
                raise e

            # temp
            if float(pot_meteo_data[1]) > float(temp_fetch):
                image_name_pot = "low-temperature.png"
            else:
                image_name_pot = "thermometer.png"

            image_pot = Image.open(image_name_pot)
            resized_image_pot = image_pot.resize((50, 60), resample=Image.LANCZOS)
            pic_pot = ImageTk.PhotoImage(resized_image_pot)
            pic_label_pot.configure(image=pic_pot)
            pic_label_pot.image = pic_pot

            # light
            if float(pot_meteo_data[3]) > float(light_fetch):
                image_name_light = "no-sunlight.png"
            else:
                image_name_light = "sun-shining.png"

            image_pot_light = Image.open(image_name_light)
            resized_image_pot_light = image_pot_light.resize((50, 60), resample=Image.LANCZOS)
            pic_pot_light = ImageTk.PhotoImage(resized_image_pot_light)
            pic_label_pot_light.configure(image=pic_pot_light)
            pic_label_pot_light.image = pic_pot_light

            # water
            if float(pot_meteo_data[4]) > float(humidity_fetch):
                image_name_water = "no-water.png"
            else:
                image_name_water = "watering-plants.png"

            image_pot_water = Image.open(image_name_water)
            resized_image_pot_water = image_pot_water.resize((50, 60), resample=Image.LANCZOS)
            pic_pot_water = ImageTk.PhotoImage(resized_image_pot_water)
            pic_label_pot_water.configure(image=pic_pot_water)
            pic_label_pot_water.image = pic_pot_water

            # food
            if float(pot_meteo_data[2]) > float(acid_fetch):
                image_name_food = "no-medical-treatment.jpg"
            else:
                image_name_food = "suplement_plant.png"

            image_pot_food = Image.open(image_name_food)
            resized_image_pot_food = image_pot_food.resize((50, 60), resample=Image.LANCZOS)
            pic_pot_food = ImageTk.PhotoImage(resized_image_pot_food)
            pic_label_pot_food.configure(image=pic_pot_food)
            pic_label_pot_food.image = pic_pot_food

        # Change username and password button
        self.button_change_login = tk.Button(new_window, text="Change login", command=self.open_user_info_window)
        self.button_change_login.place(x=5, y=5)

        # odabir imena biljaka iz baze u listbox
        refresh_plant()

        #  odabir imena posuda iz baze u listbox
        refresh_pot()

        def selected_item_listbox_plant():
            """ za označenu biljku iz listbox-a dobavlja vrijednosti iz baze

            return name_fetch, desc_fetch, temp_fetch, acid_fetch, light_fetch, humidity_fetch"""
            # selected_index = self.listbox_plant.curselection()
            # name_plant = self.listbox_plant.get(selected_index)
            for i in self.listbox_plant.curselection():
                name_plant = self.listbox_plant.get(i)
                try:
                    with sqlite3.connect("inventory.db") as conn:
                        c = conn.cursor()
                        c.execute("SELECT * FROM plant WHERE name=?", (name_plant,))
                        fetch = c.fetchall()[0]
                        name_fetch = fetch[0]
                        desc_fetch = fetch[1]
                        temp_fetch = fetch[2]
                        acid_fetch = fetch[3]
                        light_fetch = fetch[4]
                        humidity_fetch = fetch[5]
                except Exception as e:
                    raise e
                return name_fetch, desc_fetch, temp_fetch, acid_fetch, light_fetch, humidity_fetch

        def update_labels_plant():
            """ažurira label sa podacima od biljke"""
            plant_data = selected_item_listbox_plant()
            frameplant_label_name.config(text=f"{plant_data[0].upper()}")
            frameplant_label_desc.config(text=f"Description: {plant_data[1]}")
            frameplant_label_temp.config(text=f"Desired temp: {plant_data[2]} °C")
            frameplant_label_ph.config(text=f"Desired pH: {plant_data[3]}")
            frameplant_label_light.config(text=f"Desired light: {plant_data[4]} lx")
            frameplant_label_humidity.config(text=f"Desired humidity: {plant_data[5]} %")

        def selected_item_listbox_pot():
            """za označenu posudu iz listbox-a dobavlja vrijednosti iz baze

            return name_pot_fetch, name_pot_plant_fetch, location"""
            for i in self.listbox_pot.curselection():
                name_pot_listbox = self.listbox_pot.get(i)[0]

                name_pot = ""
                name_pot_plant = ""
                pot_location = ""

                try:
                    with sqlite3.connect("inventory.db") as conn:
                        c = conn.cursor()
                        c.execute("SELECT * FROM pot WHERE name=?", (name_pot_listbox,))
                        rows = c.fetchall()
                        for row in rows:
                            name_pot = row[0]
                            name_pot_plant = row[1]
                            pot_location = row[2]

                except Exception as e:
                    raise e

                return name_pot, name_pot_plant, pot_location

        def update_labels_pot(pot_data, meteo_data):
            """ažurira label-e pot-a u frame-u"""
            label_pot_name.config(text=f"{pot_data[0].upper()}")
            label_pot_plant_name.config(text=f"Plant in pot: {pot_data[1].title()}")
            label_pot_location.config(text=f"Pot spot:\n{pot_data[2].title()}")
            label_pot_temp.config(text=f"Pot temp: {meteo_data[1]} °C")
            label_pot_ph.config(text=f"Pot pH: {meteo_data[2]}")
            label_pot_humidity.config(text=f"Pot humidity: {meteo_data[4]} %")
            label_pot_light.config(text=f"Pot light: {meteo_data[3]} lx")

        def get_4_last_values_by_time(location_def):
            """bira vrijednosti iz baze - zadnje 4 vrijednosti po vremenu

            return time, temp, ph, light, humidity, location"""
            time = []
            temp = []
            ph = []
            light = []
            humidity = []
            location = []
            try:
                with sqlite3.connect("inventory.db") as conn:
                    c = conn.cursor()
                    # c.execute("SELECT * FROM data WHERE location=? ORDER BY time DESC LIMIT 4", (location_def,))
                    c.execute("SELECT * FROM data WHERE location=? ORDER BY ROWID DESC LIMIT 4", (location_def,))
                    rows = c.fetchall()
                    for row in rows:
                        time.append(row[0])
                        temp.append(row[1])
                        ph.append(row[2])
                        light.append(row[3])
                        humidity.append(row[4])
                        location.append(row[5])

            except Exception as e:
                print(f"plant temp error -> ")
                raise e
            time.reverse()
            temp.reverse()
            ph.reverse()
            light.reverse()
            humidity.reverse()
            return time, temp, ph, light, humidity, location

        def graph_pot_window():
            """crtanje grafa"""

            window = tk.Tk()
            window.title("graph window")
            window.minsize(600, 600)

            frame = tk.Frame(window)
            frame.pack()

            location_def = "Zagreb"

            # Podaci za x os -> vrijeme očitanja
            time = get_4_last_values_by_time(location_def)[0]

            # Podaci za y os - temperatura
            temp = get_4_last_values_by_time(location_def)[1]

            # Podaci za y os - kiselost
            pH = get_4_last_values_by_time(location_def)[2]

            # Podaci za y os - svjetlost
            light = get_4_last_values_by_time(location_def)[3]

            # Podaci za y os - vlaga
            humidity = get_4_last_values_by_time(location_def)[4]

            # Stvaranje Matplotlib figure
            fig = Figure(figsize=(5, 4), dpi=100)       # 5x4 inča je instanca objekta Figure, 100 je gustoća piksela za crtanje
            ax = fig.add_subplot(111)                   # 1 red, 1 stupac i 1 indeks -> jedan podgraf cijela figura

            # Stvaranje linijskog dijagrama s dvije linije
            ax.plot(time, temp, label='Temp')
            ax.plot(time, pH, label='pH')
            ax.plot(time, light, label='Light')
            ax.plot(time, humidity, label='Humidity')

            # Dodavanje naslova grafu
            ax.set_title("Dijagram očitanja posude")

            # Dodavanje oznaka osi
            ax.set_xlabel("Vrijeme", fontsize=10)
            ax.set_ylabel("Vrijednosti", fontsize=10)

            # Konfiguriranje veličine fonta vrijednosti osi
            ax.tick_params(axis="x", labelsize=6)
            ax.tick_params(axis='y', labelsize=8)

            # Dodavanje legende
            ax.legend()

            # Stvaranje objekta i dodavanje u frame graph okvir
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # button open window with graph
        button_graph = tk.Button(new_window, text="Open graph", command=graph_pot_window)
        button_graph.place(x=300, y=450, height=30, width=90)

    def open_user_info_window(self):
        """novi prozor s podacima username i password. azuriranje"""
        user_window = tk.Toplevel(root)
        user_window.title("User Info")
        user_window.minsize(250, 150)

        #   prozor za ažuriranje login podataka
        def update_user():
            """ažurira login podatke i sprema ih u bazu"""
            def update_database():
                """ažurira bazu sa username i password"""
                label_username.config(text=f"Username: {username_var.get()}")
                label_password.config(text=f"Password: {password_var.get()}")

                try:
                    with sqlite3.connect("inventory.db") as conn:
                        c = conn.cursor()
                        c.execute(f"UPDATE login SET username=?, password=?", (new_username_entry.get(),
                                                                               new_password_entry.get()))
                        conn.commit()
                except Exception as e:
                    raise e

                root_2.destroy()
                user_window.destroy()

            def callback_update(event):
                update_database()
            user_window.bind('<Return>', callback_update)

            root_2 = tk.Toplevel(user_window)
            root_2.minsize(200, 200)
            ft = tkFont.Font(family='Times', size=10)

            username_label = tk.Label(root_2, text="new username")
            username_label.pack()

            username_var = tk.StringVar()
            new_username_entry = tk.Entry(root_2, font=ft, textvariable=username_var)
            new_username_entry.pack()
            new_username_entry.focus()

            password_label = tk.Label(root_2, text="new password")
            password_label.pack()

            password_var = tk.StringVar()
            new_password_entry = tk.Entry(root_2, font=ft, textvariable=password_var)
            new_password_entry.pack()
            new_password_entry.bind("<Return>", callback_update)    # tek nakon unosa password se moze stisnuti Enter

            ok_button = tk.Button(root_2, text="OK", command=update_database, pady=20)
            ok_button.pack()

            root_2.transient(user_window)   # tranzit -> neće se otvarati u taskbaru i pojaviti će se na vrhu user_window (odnos roditelj-dijete)
            root_2.grab_set()   # postavlja fokusiranost i miš na root_2 prozor (dijete). sprječava interakciju sa parent window dok se root_2 ne zatvori

            user_window.wait_window(root_2) # sprječava izvršavanje user_window (roditelj) dok se root_2 (dijete) ne zatvori

        label_ime = tk.Label(user_window, text=f"Ime: Ivan")
        label_ime.pack()
        label_prezime = tk.Label(user_window, text=f"Prezime: Cugura")
        label_prezime.pack()
        label_username = tk.Label(user_window, text=f"Username: {self.get_credentials()[0]}")
        label_username.pack()
        label_password = tk.Label(user_window, text=f"Password: {self.get_credentials()[1]}")
        label_password.pack()

        # nakon klika se otvara novi prozor za ažuriranje podataka -> update user()
        button_login_update = tk.Button(user_window, text="Update", command=update_user, pady=10)
        button_login_update.pack()

    def plant_temp(self, location):
        """
        dohvaća vrijednosti

        temp, humidity, light i random pH

        sa net-a i vraća ih
        """
        api_key = "65138f7f96591ab4e7283e787e7fa497"
        url_endpoint = "https://api.openweathermap.org/data/2.5/weather"
        plant_params = {
            "q": location,
            "appid": api_key,
            "units": "metric"
        }

        response = requests.get(url_endpoint, params=plant_params)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            light = random.randint(1, 1500)
            ph = random.randint(2, 9)

            return temp, humidity, light, ph
        else:
            temp = random.randint(0, 35)
            humidity = random.randint(10, 80)
            light = random.randint(1, 1500)
            ph = random.randint(2, 9)
            print("Error plant temp")

            return temp, humidity, light, ph

    def insert_meteo_data(self, location, temp, humidity, light, ph):
        """sprema vrijednosti biljke u bazu zajedno sa vremenom"""
        time_now = dt.datetime.now().strftime('%d.%m.%Y. %H:%M:%S')
        try:
            with sqlite3.connect("inventory.db") as conn:
                c = conn.cursor()
                c.execute("INSERT INTO data "
                          "(time, read_value_temp, read_value_pH, read_value_light, read_value_humidity, location)"
                          "VALUES (?, ?, ?, ?, ?, ?)", (time_now, temp, ph, light, humidity, location))
                conn.commit()

        except Exception as e:
            print(f"plant temp error:")
            raise e

    def get_meteo_data(self, location):
        """
        vraća vrijednosti iz baze

        zadnja vrijednost po vremenu (1 red)

        time, temp, ph, light, humidity, location
        """

        try:
            with sqlite3.connect("inventory.db") as conn:
                c = conn.cursor()
                # c.execute("SELECT * FROM data WHERE location=? ORDER BY time DESC LIMIT 1", (location,))
                c.execute("SELECT * FROM data WHERE location=? ORDER BY ROWID DESC LIMIT 1", (location,))
                rows = c.fetchall()
                for row in rows:
                    time = row[0]
                    temp = row[1]
                    ph = row[2]
                    light = row[3]
                    humidity = row[4]
                    location = row[5]

        except Exception as e:
            print(f"plant temp error -> ")
            raise e

        return time, temp, ph, light, humidity, location


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

