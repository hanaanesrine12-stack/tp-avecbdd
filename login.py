import tkinter as tk
from tkinter import ttk, messagebox


DANGER_COLOR = "#D9534F"


class LoginPage(ttk.Frame):
    def __init__(self, parent, database, on_login):
        super().__init__(parent, padding=36)
        self.database = database
        self.on_login = on_login
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        card = ttk.Frame(self, style="Surface.TFrame", padding=28)
        card.grid(row=0, column=0)
        ttk.Label(card, text="CRYPTOLINK", style="Title.TLabel").pack(anchor="w")
        ttk.Label(card, text="Messagerie sécurisée", style="Subtitle.TLabel").pack(
            anchor="w", pady=(2, 22)
        )
        ttk.Label(card, text="Nom d'utilisateur").pack(anchor="w")
        self.username = ttk.Entry(card, width=34)
        self.username.pack(fill="x", pady=(5, 14))
        ttk.Label(card, text="Mot de passe").pack(anchor="w")
        self.password = ttk.Entry(card, width=34, show="*")
        self.password.pack(fill="x", pady=(5, 18))
        ttk.Button(card, text="Se connecter", style="Primary.TButton", command=self.login).pack(
            fill="x"
        )
        self.status = ttk.Label(card, style="Muted.TLabel")
        self.status.pack(anchor="w", pady=(14, 0))
        self.password.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()
        try:
            user = self.database.authenticate(username, password)
        except Exception as error:
            messagebox.showerror("Base de données", str(error))
            return
        if user is None:
            self.status.config(text="Identifiants incorrects", foreground=DANGER_COLOR)
            return
        self.on_login(user)
