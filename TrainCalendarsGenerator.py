import tkinter
import numpy as np
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
from datetime import datetime, date, timedelta
from createClusters import createClusters
from MCSolver import problem

root = tkinter.Tk()
root.configure(background="white")
root.title('Date Picker')
img = tkinter.Image("photo", file="calendar.gif")
# root.iconphoto(True, img) # you may also want to try this.
root.tk.call('wm', 'iconphoto', root._w, img)

style = ttk.Style(root)
style.theme_use('default')

butText = "Pick Date"
indexes = []
picked_ids = {
    "ids": [],
    "dates": [],
    "indexes": [],
}


def checkProperDate(start, end):
    if end < start:
        messagebox.showerror("Error", "Start date must me smaller than end date!")
        return 0
    if end > date(2021, 12, 31):
        messagebox.showerror("Error", "Selected dates must be from 2021")
        return 0
    elif start < date(2021, 1, 1):
        messagebox.showerror("Error", "Selected dates must be from 2021")
        return 0
    return 1


def open():
    global cal, end_button, pick_button, prev_date, root, startCal, endCal, startDate, endDate, CLUSTERS, CLUSTERS_NAMES, CLUSTERS_DATES, loop
    startDate = startCal.get_date()
    endDate = endCal.get_date()
    switch = True
    if checkProperDate(startDate, endDate) == 0:
        return
    CLUSTERS, CLUSTERS_NAMES, CLUSTERS_DATES = createClusters(startDate.timetuple().tm_yday,
                                                              endDate.timetuple().tm_yday)
    root.destroy()
    root = tkinter.Tk()
    root.configure(background="white")
    root.title('Date Picker')
    img = tkinter.Image("photo", file="calendar.gif")
    root.tk.call('wm', 'iconphoto', root._w, img)

    style = ttk.Style(root)
    style.theme_use('default')
    root.geometry("1000x800")
    my_label = tkinter.Label(root, text="Select a date")
    cal = Calendar(root,
                   selectmode="day", year=2021,
                   disabledbackground="red", headersbackground="slateblue",
                   normalbackground="white", weekendbackground="mediumpurple",
                   selectbackground="salmon", showothermonthdays=False)
    cal.config(background="black")
    cal.pack(pady=20, fill="both", expand=True)
    prev_date = cal.get_date()

    def grab_date():
        global picked_ids
        picked_date = cal.get_date()
        # my_label.config(text="Picked Date " + picked_date)
        if picked_date == "":
            messagebox.showerror("Error", "First select a date!")
            return
        if datetime.strptime(picked_date, "%m/%d/%y") not in picked_ids["dates"]:
            picked_ids["ids"].append(cal.calevent_create(datetime.strptime(picked_date, "%m/%d/%y"), "picked"))
            picked_ids["dates"].append(datetime.strptime(picked_date, "%m/%d/%y"))
            date_index = datetime.strptime(picked_date, "%m/%d/%y").timetuple().tm_yday
            picked_ids["indexes"].append(date_index)
        else:
            idx = picked_ids["dates"].index(datetime.strptime(picked_date, "%m/%d/%y"))
            id = picked_ids["ids"][idx]
            date = cal.calevents[id]['date']
            del cal.calevents[id]
            del cal._calevent_dates[date]
            cal._reset_day(date)
            picked_ids["ids"].pop(idx)
            picked_ids["dates"].pop(idx)
            picked_ids["indexes"].pop(idx)
            my_label.config(text="Selected date: None")
            global prev_date
            prev_date = None
            cal._sel_date = None

    def random_events_button():
        global picked_ids, endDate, startDate,cal, root
        ilosc = endDate.timetuple().tm_yday - startDate.timetuple().tm_yday + 1
        daty = np.unique(np.random.randint(startDate.timetuple().tm_yday, endDate.timetuple().tm_yday + 1,
                                           np.random.randint(1, ilosc + 1)))
        for data in daty:
            datatemp = (datetime(2021, 1, 1) + timedelta(int(data) - 1))
            if datatemp not in picked_ids["dates"]:
                picked_ids["ids"].append(cal.calevent_create(datatemp.date(), "picked"))
                picked_ids["dates"].append(datatemp)
                picked_ids["indexes"].append(data)

    def date_check():
        global prev_date, butText, pick_button, pick_button, startDate, endDate, after2
        if prev_date != cal.get_date():
            if cal.get_date() == "":
                my_label.config(text="Select a date")
            else:
                my_label.config(text="Selected date: " + cal.get_date())
            prev_date = cal.get_date()
        if cal.get_date() == "":
            butText = "Pick Date"
        elif datetime.strptime(cal.get_date(), "%m/%d/%y") in picked_ids["dates"]:
            butText = "Unpick Date"
        else:
            butText = "Pick Date"
        if pick_button.winfo_exists():
            pick_button["text"] = butText
        if cal.get_date() != "":
            calendar_date = datetime.strptime(cal.get_date(), "%m/%d/%y").date()
            if calendar_date > endDate:
                messagebox.showerror("Error",
                                     f"Selected date must be from {startDate.strftime('%d/%m/%Y')} to {endDate.strftime('%d/%m/%Y')}")
                cal.selection_set(endDate)
            elif calendar_date < startDate:
                messagebox.showerror("Error",
                                     f"Selected date must be from {startDate.strftime('%d/%m/%Y')} to {endDate.strftime('%d/%m/%Y')}")
                cal.selection_set(startDate)
        after2 = root.after(100, date_check)

    def stop_selecting():
        global cal, end_button
        cal._remove_selection()
        cal.__setitem__("selectmode", "none")
        pick_button.destroy()
        end_button["text"] = "Show results"
        end_button["command"] = results
        dates = []
        for date in picked_ids["dates"]:
            dates.append(datetime.strftime(date, '%d/%m/%y'))
        dates = str(dates).replace('\'', '').replace(', ', ', ').replace('[', '').replace(']', '')
        my_label.config(text=f"Selected dates: {dates}")

    def results():
        global picked_ids, startDate, endDate, root, switch, img, loop, after2, CLUSTERS, CLUSTERS_NAMES, CLUSTERS_DATES, PRZEROBIONY
        # ustawienia okna
        switch = False
        root.after_cancel(loop)
        root.after_cancel(after2)
        Top = tkinter.Toplevel(root, )
        Top.configure(background="white")
        Top.title('Result')
        Top.grab_set()
        img = tkinter.Image("photo", file="calendar.gif")
        # root.tk.call('wm', 'iconphoto', root._w, img)
        style = ttk.Style(Top)
        style.theme_use('default')
        # # wyliczamy długość tablicy
        PERIODICITY = np.zeros((endDate.timetuple().tm_yday - startDate.timetuple().tm_yday + 1), int)
        for i in range(PERIODICITY.shape[0]):
            PERIODICITY[i] = 0 if i + startDate.timetuple().tm_yday in picked_ids[
                "indexes"] else i + startDate.timetuple().tm_yday  # UNIVERSE
        PERIODICITY = PERIODICITY[PERIODICITY[:] != 0]
        PRZEROBIONY = np.multiply(CLUSTERS, CLUSTERS_DATES).tolist()
        NPRZEROBIONY = []
        NNAZWY = []
        for i in range(len(PRZEROBIONY)):
            NNAZWY.append(CLUSTERS_NAMES[i])
            NPRZEROBIONY.append(set(filter((0).__ne__, PRZEROBIONY[i])))
        print("OKRES: ", PERIODICITY)
        # print("prze",NPRZEROBIONY)
        wyniki = problem(set(PERIODICITY.copy()), NPRZEROBIONY.copy(), )
        msg = ""
        przerywnik = "," if len(wyniki) > 2 else "plus"
        exception = ""
        exceptionplus = ""
        res = set([])
        for wynik in wyniki:
            idx = NPRZEROBIONY.index(wynik)
            # print(idx)
            if msg == "" and NNAZWY[idx][0] != "f":
                msg += "'" + NNAZWY[idx] + "'"
            elif msg == "" and NNAZWY[idx][0] == "f":
                msg += NNAZWY[idx][:5] + "'" + NNAZWY[idx][5:] + "'"
            elif NNAZWY[idx][0] == "f":
                msg += przerywnik + " " + NNAZWY[idx][:5] + "'" + NNAZWY[idx][5:] + "'"
            else:
                msg += f" {przerywnik} '{NNAZWY[idx]}'"
            res = res | wynik
        if len(res - set(PERIODICITY)) > 0 or len(set(PERIODICITY) - res) > 0:
            diffs = []
            diffsplus = []
            if len(res - set(PERIODICITY)) > 0:
                diffs = sorted(res - set(PERIODICITY))
                difftxt = "with the exception of "
            if len(set(PERIODICITY) - res) > 0:
                # print("X")
                diffsplus = sorted(set(PERIODICITY) - res)
                diffplus = "plus on "
            for diff in diffs:
                datetemp = (datetime(2021, 1, 1) + timedelta(int(diff) - 1)).strftime('%d/%m/%Y')
                exception += f"{datetemp}" if exception == "" else f", {datetemp}"
            for diff in diffsplus:
                datetemp = (datetime(2021, 1, 1) + timedelta(int(diff) - 1)).strftime('%d/%m/%Y')
                exceptionplus += f"{datetemp}" if exceptionplus == "" else f", {datetemp}"
        if PERIODICITY.shape[0] != 0:
            exceptionplus = diffplus + exceptionplus if exceptionplus != "" else ""
            exception = difftxt + exception if exception != "" else ""
            preposition = "on" if msg[0] != 'f' else ""
            lbl = tkinter.Label(Top,
                                text=f"The service is provided {preposition} {msg} from {startDate.strftime('%d/%m/%Y')} to {endDate.strftime('%d/%m/%Y')} {exceptionplus} {exception}",
                                wraplength=300, justify="center").pack(padx=10, pady=10)
        else:
            lbl = tkinter.Label(Top,
                                text=f"The service is not provided from {startDate.strftime('%d/%m/%Y')} to {endDate.strftime('%d/%m/%Y')}",
                                wraplength=300, justify="center").pack(padx=10, pady=10)

    pick_button = tkinter.Button(root, text=butText, command=grab_date)
    random_button = tkinter.Button(root, text="Select random dates", command=random_events_button)
    end_button = tkinter.Button(root, text="Finish", command=stop_selecting)
    if switch:
        loop = root.after(100, date_check)
    else:
        print("[ERROR]")
        root.after_cancel(loop)
        loop = None
    my_label.pack(pady=10)
    pick_button.pack(pady=10)
    random_button.pack(pady=10)
    end_button.pack(padx=100)


startCal = DateEntry(root, width=12, year=2021, month=1, day=1, background='darkblue', foreground='white',
                     borderwidth=2)
endCal = DateEntry(root, width=12, year=2021, month=1, day=1, background='darkblue', foreground='white', borderwidth=2)
startLab = tkinter.Label(root, text="Select start date: ").pack(padx=10)
startCal.pack(padx=10, pady=10)
endLab = tkinter.Label(root, text="Select end date: ").pack(padx=10)
endCal.pack(padx=10, pady=10)
next_button = tkinter.Button(root, text="Proceed", command=open).pack()
# Top.grab_set()
root.mainloop()
