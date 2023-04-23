import csv
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from os import listdir


WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
icon = "icon.png"


def statistics_page() -> None:
    """Opens tkinter window with game statistics for player"""

    def check_keys(event: tk.Event):
        """Checking if users tries to input or paste text into text fields"""
        if event.char.isalpha() or (event.state & 4 and event.keysym == "v"):
            return "break"

    # creating and setting main window of tkinter
    root = tk.Tk()
    root.geometry(f'{WINDOW_WIDTH + 300}x{WINDOW_HEIGHT}')
    root.resizable(False, False)
    root.title("Game Statistics")
    root.iconbitmap(icon)
    # making scrollbar for text label
    text = tk.Text(root, height=50, width=WINDOW_WIDTH)
    text.grid(row=0, column=0, sticky=tk.EW)
    scrollbar = ttk.Scrollbar(root, orient='vertical', command=text.yview)
    scrollbar.grid(row=0, column=1, sticky=tk.NS)
    text.yscrollcommand = scrollbar.set
    # binding not allowing input and pasting into text fields
    text.bind("<Key>", check_keys)
    # adding text
    with open("game_statistics.csv", "r", encoding="windows-1251") as file:
        reader = csv.reader(file, delimiter=';')
        for index, row in enumerate(reader, 1):
            row_format = "{:^16} | {:^6} | {:^16} | {:^5} | {:^12} | {:^6} | {:^8} | {:^26}\n".format(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            text.insert(float(index), row_format)
    root.mainloop()


def save_statistics(player_name: str, result: str, remaining_health: int, score: int,
                    time_played: str, shots_made: int, accuracy: float) -> None:
    """Saving game statistics after every game of the player into csv file"""
    filename = "game_statistics.csv"
    fields = ["name", "result", "remaining_health", "score", "time_played", "shots", "accuracy", "date"]
    row = {"name": player_name, "result": result, "remaining_health": remaining_health, "score": score,
           "time_played": time_played, "shots": shots_made, "accuracy": accuracy,
           "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
    if filename in listdir():  # file exists and user adds new game statistics row
        with open("game_statistics.csv", 'a', newline='', encoding='windows-1251') as file:
            writer = csv.DictWriter(file, delimiter=';', fieldnames=fields)
            writer.writerow(row)
            file.close()
    else:  # file does not already exist for statistics (first initialization)
        with open("game_statistics.csv", 'w', newline='', encoding='windows-1251') as file:
            writer = csv.DictWriter(file, delimiter=';', fieldnames=fields)
            writer.writeheader()
            writer.writerow(row)
            file.close()
