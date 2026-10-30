import tkinter as tk
from tkinter import ttk, messagebox

from partie2 import ciphers
from database import Database
from login import LoginPage


COLORS = {
    "background": "#EAF3FF",
    "surface": "#FFFFFF",
    "surface_dark": "#F4F8FD",
    "text": "#1D2A3A",
    "muted": "#637083",
    "accent": "#2F75D6",
    "success": "#2DAA68",
    "danger": "#D9534F",
    "border": "#C5D6EA",
    "code_text": "#176B3A",
}

def configure_style(window):
    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure(
        ".",
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
    style.configure("TFrame", background=COLORS["background"])
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"])
    style.configure("Muted.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
    style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("Subtitle.TLabel", foreground=COLORS["muted"])
    style.configure("TLabelframe", background=COLORS["surface"], foreground=COLORS["text"])
    style.configure(
        "TLabelframe.Label",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10, "bold"),
    )
    style.configure("TEntry", fieldbackground=COLORS["surface_dark"], foreground=COLORS["text"])
    style.configure("TCombobox", fieldbackground=COLORS["surface_dark"], foreground=COLORS["text"])
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["surface_dark"])])
    style.configure(
        "Primary.TButton",
        background=COLORS["accent"],
        foreground="white",
        padding=(14, 8),
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
    )
    style.map("Primary.TButton", background=[("active", "#5A96EC")])
    style.configure(
        "Success.TButton",
        background=COLORS["success"],
        foreground="white",
        padding=(14, 8),
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
    )
    style.map("Success.TButton", background=[("active", "#46C980")])
    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground="white",
        padding=(12, 7),
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
    )
    style.configure("TNotebook", background=COLORS["background"], borderwidth=0)
    style.configure(
        "Notifications.Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=34,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Notifications.Treeview.Heading",
        background=COLORS["surface_dark"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 9, "bold"),
        padding=(8, 7),
    )
    style.map("Notifications.Treeview", background=[("selected", COLORS["accent"])])


def make_text_box(parent, height, code=False):
    box = tk.Text(
        parent,
        height=height,
        wrap="word",
        bg=COLORS["surface_dark"] if code else COLORS["surface"],
        fg=COLORS["code_text"] if code else COLORS["text"],
        insertbackground=COLORS["text"],
        selectbackground=COLORS["accent"],
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
        font=("Consolas", 10) if code else ("Segoe UI", 10),
    )
    return box


def set_text(box, text):
    box.config(state="normal")
    box.delete("1.0", "end")
    box.insert("1.0", text)
    box.config(state="disabled")


def get_text(box):
    return box.get("1.0", "end").strip()


class AlertBanner(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, height=76, padx=14, pady=10)
        self.pack_propagate(False)

    def show(self, kind, title, message):
        styles = {
            "error": ("#FDECEC", "#D9534F", "✕"),
            "warning": ("#FFF7DF", "#D99A00", "!"),
            "success": ("#EAF8F0", "#238B54", "✓"),
        }
        background, foreground, icon = styles[kind]
        self.configure(background=background, highlightthickness=1, highlightbackground=foreground)
        for child in self.winfo_children():
            child.destroy()
        self.columnconfigure(1, weight=1)
        tk.Label(
            self,
            text=icon,
            bg=foreground,
            fg="white",
            font=("Segoe UI", 18, "bold"),
            width=2,
        ).grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 12))
        tk.Label(
            self,
            text=title,
            bg=background,
            fg=foreground,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).grid(row=0, column=1, sticky="ew")
        tk.Label(
            self,
            text=message,
            bg=background,
            fg=foreground,
            font=("Segoe UI", 9),
            anchor="w",
        ).grid(row=1, column=1, sticky="ew")
        tk.Button(
            self,
            text="×",
            command=self.hide,
            bg=background,
            fg=foreground,
            activebackground=background,
            activeforeground=foreground,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 14),
        ).grid(row=0, column=2, rowspan=2, padx=(12, 0))
        self.grid()

    def hide(self):
        self.grid_remove()


def read_hill_key(text):
    if "," in text:
        try:
            numbers = [int(value.strip()) for value in text.split(",")]
        except ValueError as error:
            raise ValueError("la clé Hill doit contenir des nombres") from error
        size = int(len(numbers) ** 0.5)
        if size * size != len(numbers):
            raise ValueError("la matrice doit être carrée")
        return [numbers[index * size:(index + 1) * size] for index in range(size)]
    return ciphers.key_from_text(text)


def encrypt_message(text, algorithm, key, direction):
    if algorithm == "Caesar":
        try:
            shift = int(key)
        except ValueError as error:
            raise ValueError("la clé César doit être un entier") from error
        if shift % 52 == 0:
            raise ValueError("clé César trop faible")
        letters, mask = ciphers.caesar_prepare(text)
        return ciphers.caesar(letters, shift, direction), {
            "caesar_mask": mask,
        }

    if algorithm == "Hill":
        hill_key = read_hill_key(key)
        letters = ciphers.clean(text)
        positions = ciphers.format_positions(text.upper())
        padding = (-len(letters)) % len(hill_key)
        encrypted = ciphers.hill_encrypt(text, hill_key)
        return encrypted, {
            "hill_format_positions": positions,
            "hill_padding": padding,
        }

    positions = ciphers.format_positions(text.upper())
    padding_positions = ciphers.playfair_prepare(text)[1]
    j_positions = ciphers.playfair_j_positions(text)
    encrypted = ciphers.playfair_encrypt(text, key)
    return encrypted, {
        "playfair_format_positions": positions,
        "playfair_padding_positions": padding_positions,
        "playfair_j_positions": j_positions,
    }


def decrypt_message(channel_message, metadata):
    name, direction, key, _ = ciphers.decode_channel_message(channel_message)
    if name == "Caesar":
        decrypted = ciphers.dechiffrement_automatique(channel_message, key)
        return ciphers.caesar_restore(decrypted, metadata["caesar_mask"])
    if name == "Hill":
        decrypted = ciphers.dechiffrement_automatique(
            channel_message,
            key,
            hill_key=read_hill_key(key),
        )
        padding = metadata["hill_padding"]
        if padding:
            decrypted = decrypted[:-padding]
        return ciphers.restore_format(decrypted, metadata["hill_format_positions"])

    decrypted = ciphers.dechiffrement_automatique(channel_message, key)
    decrypted = ciphers.playfair_strip_padding(
        decrypted,
        metadata["playfair_padding_positions"],
    )
    decrypted = ciphers.playfair_restore_j(
        decrypted,
        metadata["playfair_j_positions"],
    )
    return ciphers.restore_format(decrypted, metadata["playfair_format_positions"])


class SendPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=22)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        ttk.Label(self, text="Envoyer un message", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(self, text="Choisissez un contact et une méthode de chiffrement.", style="Subtitle.TLabel").grid(
            row=1, column=0, sticky="w", pady=(3, 16)
        )

        settings = ttk.LabelFrame(self, text="Paramètres du message", padding=12)
        settings.grid(row=2, column=0, sticky="nsew")
        settings.columnconfigure(1, weight=1)
        ttk.Label(settings, text="Récepteur").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.recipient = ttk.Combobox(settings, state="readonly")
        self.recipient.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(settings, text="Algorithme").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        self.algorithm = ttk.Combobox(
            settings, values=["Caesar", "Hill", "Playfair"], state="readonly"
        )
        self.algorithm.current(0)
        self.algorithm.grid(row=1, column=1, sticky="ew", pady=5)
        self.algorithm.bind("<<ComboboxSelected>>", self.change_algorithm)
        ttk.Label(settings, text="Clé").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        self.key = ttk.Entry(settings)
        self.key.grid(row=2, column=1, sticky="ew", pady=5)
        ttk.Label(settings, text="Sens").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
        self.direction = ttk.Combobox(
            settings, values=["droite", "gauche"], state="readonly", width=12
        )
        self.direction.current(0)
        self.direction.grid(row=3, column=1, sticky="w", pady=5)
        ttk.Label(settings, text="Message").grid(row=4, column=0, sticky="nw", padx=(0, 10), pady=(12, 5))
        self.message = make_text_box(settings, 7)
        self.message.grid(row=4, column=1, sticky="nsew", pady=(12, 5))
        settings.rowconfigure(4, weight=1)
        self.channel = make_text_box(settings, 3, code=True)
        self.channel.grid(row=5, column=1, sticky="nsew", pady=(12, 5))
        self.channel.config(state="disabled")
        ttk.Label(settings, text="Canal").grid(row=5, column=0, sticky="nw", padx=(0, 10), pady=(12, 5))
        self.status = ttk.Label(settings, style="Muted.TLabel")
        self.status.grid(row=6, column=1, sticky="w", pady=(8, 0))
        ttk.Button(
            settings,
            text="🔒 Envoyer le message",
            style="Primary.TButton",
            command=self.send,
        ).grid(row=6, column=1, sticky="e", pady=(8, 0))
        self.change_algorithm()

    def on_show(self):
        self.contacts = self.app.database.list_users(self.app.current_user["id"])
        names = [contact["username"] for contact in self.contacts]
        self.recipient["values"] = names
        if names and not self.recipient.get():
            self.recipient.current(0)

    def change_algorithm(self, event=None):
        settings = {
            "Caesar": ("3", "readonly"),
            "Hill": ("3,3,2,5", "disabled"),
            "Playfair": ("monarchy", "disabled"),
        }
        key, direction_state = settings[self.algorithm.get()]
        self.key.delete(0, "end")
        self.key.insert(0, key)
        self.direction.config(state=direction_state)

    def send(self):
        text = get_text(self.message)
        recipient = self.recipient.get()
        if not ciphers.clean(text):
            self.app.show_alert("error", "Erreur", "Le message doit contenir au moins une lettre.")
            return
        if not self.algorithm.get():
            self.app.show_alert("warning", "Attention", "Sélectionnez un algorithme de chiffrement.")
            return
        if not recipient:
            self.app.show_alert("warning", "Attention", "Sélectionnez un récepteur avant l'envoi.")
            return
        recipient_user = next(
            contact for contact in self.contacts if contact["username"] == recipient
        )
        try:
            encrypted, metadata = encrypt_message(
                text,
                self.algorithm.get(),
                self.key.get().strip(),
                self.direction.get(),
            )
            channel = ciphers.build_channel_message(
                self.algorithm.get(), self.direction.get(), encrypted, self.key.get().strip()
            )
        except ValueError as error:
            self.app.show_alert("error", "Erreur", str(error))
            return
        try:
            self.app.database.save_message(
                self.app.current_user["id"],
                recipient_user["id"],
                channel,
                self.algorithm.get(),
                metadata,
            )
            self.app.database.create_notification(
                recipient_user["id"],
                "Nouveau message reçu de %s." % self.app.current_user["pseudo"],
            )
        except Exception as error:
            self.app.show_alert("error", "Base de données", str(error))
            return
        set_text(self.channel, channel)
        self.app.show_alert("success", "Message envoyé", "Le message a été envoyé avec succès.")
        self.status.config(text="Message envoyé avec succès.", foreground=COLORS["success"])
        self.app.inbox_page.refresh()


class InboxPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=22)
        self.app = app
        self.visible_messages = []
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        ttk.Label(self, text="Boîte de réception", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(self, text="Consultez et déchiffrez vos messages reçus.", style="Subtitle.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(3, 16)
        )
        list_frame = ttk.LabelFrame(self, text="Messages reçus", padding=10)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        self.listbox = tk.Listbox(
            list_frame,
            width=28,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            selectbackground=COLORS["accent"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            font=("Segoe UI", 10),
        )
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.select_message)
        detail = ttk.LabelFrame(self, text="Détail du message", padding=12)
        detail.grid(row=2, column=1, sticky="nsew")
        detail.columnconfigure(1, weight=1)
        detail.rowconfigure(3, weight=1)
        ttk.Label(detail, text="Expéditeur").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=4)
        self.sender = ttk.Label(detail, text="-")
        self.sender.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(detail, text="Détection").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=4)
        self.detected = ttk.Label(detail, text="-")
        self.detected.grid(row=1, column=1, sticky="w", pady=4)
        ttk.Label(detail, text="Canal").grid(row=2, column=0, sticky="nw", padx=(0, 12), pady=4)
        self.channel = make_text_box(detail, 4, code=True)
        self.channel.grid(row=2, column=1, sticky="ew", pady=4)
        self.channel.config(state="disabled")
        ttk.Label(detail, text="Résultat").grid(row=3, column=0, sticky="nw", padx=(0, 12), pady=4)
        self.result = make_text_box(detail, 6, code=True)
        self.result.grid(row=3, column=1, sticky="nsew", pady=4)
        self.result.config(state="disabled")
        self.status = ttk.Label(detail, style="Muted.TLabel")
        self.status.grid(row=4, column=1, sticky="w", pady=(8, 0))
        ttk.Button(detail, text="🔓 Déchiffrer", style="Success.TButton", command=self.decrypt).grid(
            row=4, column=1, sticky="e", pady=(8, 0)
        )

    def refresh(self):
        try:
            self.visible_messages = self.app.database.received_messages(
                self.app.current_user["id"]
            )
        except Exception as error:
            messagebox.showerror("Base de données", str(error))
            self.visible_messages = []
        self.listbox.delete(0, "end")
        for message in self.visible_messages:
            self.listbox.insert("end", "De " + message["sender"])
        if not self.visible_messages:
            set_text(self.channel, "")
            set_text(self.result, "")
            self.sender.config(text="-")
            self.detected.config(text="-")

    def select_message(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        message = self.visible_messages[selection[0]]
        name, direction, key, _ = ciphers.decode_channel_message(message["channel_message"])
        self.sender.config(text=message["sender"])
        direction_text = {"r": "droite", "l": "gauche"}.get(direction, "non applicable")
        self.detected.config(text="%s | %s | clé : %s" % (name, direction_text, key))
        set_text(self.channel, message["channel_message"])
        set_text(self.result, "")
        self.status.config(text="Message sélectionné.", foreground=COLORS["muted"])

    def decrypt(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showerror("Erreur", "Sélectionnez un message.")
            return
        message = self.visible_messages[selection[0]]
        try:
            decrypted = decrypt_message(message["channel_message"], message["metadata"])
        except ValueError as error:
            messagebox.showerror("Erreur", str(error))
            return
        set_text(self.result, decrypted)
        self.status.config(text="Message déchiffré avec succès.", foreground=COLORS["success"])


class NotificationsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=22)
        self.app = app
        self.notifications = []
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        ttk.Label(self, text="Notifications", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            self,
            text="Messages de succès, alertes et notifications de sécurité.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 16))
        panel = ttk.LabelFrame(self, text="Centre de notifications", padding=12)
        panel.grid(row=2, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        table_frame = ttk.Frame(panel, style="Surface.TFrame")
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.notifications_table = ttk.Treeview(
            table_frame,
            columns=("state", "message", "date"),
            show="headings",
            style="Notifications.Treeview",
        )
        self.notifications_table.heading("state", text="État")
        self.notifications_table.heading("message", text="Notification")
        self.notifications_table.heading("date", text="Date")
        self.notifications_table.column("state", width=100, stretch=False)
        self.notifications_table.column("message", width=520, anchor="w")
        self.notifications_table.column("date", width=150, stretch=False)
        self.notifications_table.tag_configure("unread", foreground=COLORS["accent"])
        self.notifications_table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.notifications_table.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.notifications_table.configure(yscrollcommand=scrollbar.set)
        bottom = ttk.Frame(panel)
        bottom.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        self.status = ttk.Label(bottom, style="Muted.TLabel")
        self.status.pack(side="left")
        ttk.Button(
            bottom,
            text="Marquer comme lu",
            style="Success.TButton",
            command=self.mark_read,
        ).pack(side="right")

    def refresh(self):
        try:
            self.notifications = self.app.database.user_notifications(
                self.app.current_user["id"]
            )
        except Exception as error:
            messagebox.showerror("Base de données", str(error))
            self.notifications = []
        for item in self.notifications_table.get_children():
            self.notifications_table.delete(item)
        for notification in self.notifications:
            prefix = "Nouveau" if not notification["is_read"] else "Lu"
            created_at = notification["created_at"]
            date_text = created_at.strftime("%d/%m/%Y %H:%M") if created_at else "-"
            tags = ("unread",) if not notification["is_read"] else ()
            self.notifications_table.insert(
                "", "end", values=(prefix, notification["content"], date_text), tags=tags
            )
        if not self.notifications:
            self.notifications_table.insert("", "end", values=("", "Aucune notification.", "-"))
        self.status.config(text="%d notification(s)" % len(self.notifications))

    def mark_read(self):
        try:
            self.app.database.mark_notifications_read(self.app.current_user["id"])
        except Exception as error:
            messagebox.showerror("Base de données", str(error))
            return
        self.refresh()
        self.status.config(text="Notifications marquées comme lues.", foreground=COLORS["success"])


class BruteForcePage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=22)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        ttk.Label(self, text="Brute Force", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text="Espace réservé à l'administrateur pour auditer les mots de passe.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 16))
        controls = ttk.LabelFrame(self, text="Audit par dictionnaire", padding=12)
        controls.grid(row=2, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Dictionnaire").grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.dictionary = ttk.Entry(controls)
        self.dictionary.grid(row=0, column=1, sticky="ew")
        self.dictionary.insert(0, "123456, password, admin123, alice123, bob123")
        ttk.Button(controls, text="Lancer l'audit", style="Danger.TButton", command=self.scan).grid(
            row=0, column=2, padx=(12, 0)
        )
        self.result = make_text_box(self, 12)
        self.result.grid(row=3, column=0, sticky="nsew", pady=(14, 0))

    def scan(self):
        candidates = [value.strip() for value in self.dictionary.get().split(",") if value.strip()]
        try:
            findings = self.app.database.audit_passwords(
                candidates,
                self.app.current_user["id"],
            )
        except Exception as error:
            messagebox.showerror("Base de données", str(error))
            return
        if findings:
            set_text(
                self.result,
                "\n".join(
                    "Mot de passe faible détecté pour %s : %s"
                    % (finding["username"], finding["password"])
                    for finding in findings
                ),
            )
        else:
            set_text(self.result, "Aucun mot de passe trouvé dans le dictionnaire.")


class AppShell(ttk.Frame):
    def __init__(self, parent, user, database, logout):
        super().__init__(parent)
        self.current_user = user
        self.database = database
        self.logout = logout
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self, style="Surface.TFrame", padding=(20, 14))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="CRYPTOLINK", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=user["pseudo"], style="Subtitle.TLabel").grid(row=0, column=1, padx=14)
        ttk.Button(header, text="Déconnexion", command=logout).grid(row=0, column=2)
        self.alert = AlertBanner(self)
        self.alert.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(12, 0))
        self.alert.grid_remove()
        navigation = ttk.Frame(self, padding=(12, 18))
        navigation.grid(row=2, column=0, sticky="ns")
        self.page_container = ttk.Frame(self)
        self.page_container.grid(row=2, column=1, sticky="nsew")
        self.page_container.columnconfigure(0, weight=1)
        self.page_container.rowconfigure(0, weight=1)
        self.send_page = SendPage(self.page_container, self)
        self.inbox_page = InboxPage(self.page_container, self)
        self.notifications_page = NotificationsPage(self.page_container, self)
        self.pages = {
            "send": self.send_page,
            "inbox": self.inbox_page,
            "notifications": self.notifications_page,
        }
        ttk.Button(navigation, text="Envoyer un message", command=lambda: self.show_page("send")).pack(
            fill="x", pady=4
        )
        ttk.Button(navigation, text="Boîte de réception", command=lambda: self.show_page("inbox")).pack(
            fill="x", pady=4
        )
        ttk.Button(
            navigation,
            text="Notifications",
            command=lambda: self.show_page("notifications"),
        ).pack(fill="x", pady=4)
        if user["role"] == "admin":
            self.brute_page = BruteForcePage(self.page_container, self)
            self.pages["brute"] = self.brute_page
            ttk.Button(navigation, text="Brute Force", style="Danger.TButton", command=lambda: self.show_page("brute")).pack(
                fill="x", pady=4
            )
        self.show_page("send")

    def show_alert(self, kind, title, message):
        self.alert.show(kind, title, message)

    def show_page(self, name):
        for page in self.pages.values():
            page.grid_forget()
        page = self.pages[name]
        page.grid(row=0, column=0, sticky="nsew")
        if hasattr(page, "on_show"):
            page.on_show()
        if name == "inbox":
            self.inbox_page.refresh()
        if name == "notifications":
            self.notifications_page.refresh()


class CryptoBox(tk.Tk):
    def __init__(self):
        super().__init__()
        configure_style(self)
        self.database = Database()
        self.title("CRYPTOLINK")
        self.geometry("1080x760")
        self.minsize(860, 620)
        self.current_view = None
        self.show_login()

    def show_login(self):
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = LoginPage(self, self.database, self.login)
        self.current_view.pack(fill="both", expand=True)

    def login(self, user):
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = AppShell(self, user, self.database, self.show_login)
        self.current_view.pack(fill="both", expand=True)


def main():
    CryptoBox().mainloop()


if __name__ == "__main__":
    main()
