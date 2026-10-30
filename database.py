import hashlib
import hmac
import json
import os

import mysql.connector


class Database:
    def __init__(self):
        self.config = {
            "host": os.getenv("CRYPTO_DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("CRYPTO_DB_PORT", "3306")),
            "user": os.getenv("CRYPTO_DB_USER", "root"),
            "password": os.getenv("CRYPTO_DB_PASSWORD", ""),
            "database": os.getenv("CRYPTO_DB_NAME", "crypto"),
        }

    def connect(self):
        return mysql.connector.connect(**self.config)

    @staticmethod
    def hash_password(password, salt=None):
        salt = salt or os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 200_000
        )
        return "pbkdf2_sha256$200000$%s$%s" % (
            salt.hex(),
            digest.hex(),
        )

    @staticmethod
    def verify_password(password, stored_hash):
        try:
            algorithm, rounds, salt_hex, digest_hex = stored_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            expected = Database.hash_password(password, bytes.fromhex(salt_hex))
            return hmac.compare_digest(expected, stored_hash)
        except (ValueError, TypeError):
            return False

    def authenticate(self, username, password):
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, pseudo, role, password_hash "
                "FROM users WHERE username = %s",
                (username,),
            )
            user = cursor.fetchone()
            if user is None or not self.verify_password(password, user["password_hash"]):
                return None
            user.pop("password_hash", None)
            return user
        finally:
            connection.close()

    def list_users(self, excluded_id):
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, pseudo FROM users WHERE id <> %s ORDER BY pseudo",
                (excluded_id,),
            )
            return cursor.fetchall()
        finally:
            connection.close()

    def save_message(self, sender_id, receiver_id, channel_message, algorithm, metadata):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO messages "
                "(sender_id, receiver_id, channel_message, algorithm, metadata) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    sender_id,
                    receiver_id,
                    channel_message,
                    algorithm,
                    json.dumps(metadata),
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def received_messages(self, receiver_id):
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT messages.id, messages.channel_message, messages.metadata, "
                "messages.sent_at, users.username AS sender "
                "FROM messages JOIN users ON users.id = messages.sender_id "
                "WHERE messages.receiver_id = %s ORDER BY messages.sent_at DESC",
                (receiver_id,),
            )
            messages = cursor.fetchall()
            for message in messages:
                message["metadata"] = json.loads(message["metadata"])
            return messages
        finally:
            connection.close()

    def create_notification(self, user_id, content):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO notifications (user_id, content) VALUES (%s, %s)",
                (user_id, content),
            )
            connection.commit()
        finally:
            connection.close()

    def user_notifications(self, user_id):
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, content, is_read, created_at "
                "FROM notifications WHERE user_id = %s "
                "ORDER BY created_at DESC, id DESC",
                (user_id,),
            )
            return cursor.fetchall()
        finally:
            connection.close()

    def mark_notifications_read(self, user_id):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE notifications SET is_read = TRUE "
                "WHERE user_id = %s AND is_read = FALSE",
                (user_id,),
            )
            connection.commit()
        finally:
            connection.close()

    def audit_passwords(self, candidates, admin_user_id):
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT role FROM users WHERE id = %s", (admin_user_id,))
            admin = cursor.fetchone()
            if admin is None or admin["role"] != "admin":
                raise PermissionError("seul un administrateur peut lancer cet audit")
            cursor.execute("SELECT id, username, password_hash FROM users")
            users = cursor.fetchall()
            findings = []
            for user in users:
                for candidate in candidates:
                    if self.verify_password(candidate, user["password_hash"]):
                        findings.append({"username": user["username"], "password": candidate})
                        cursor.execute(
                            "INSERT INTO notifications (user_id, content) "
                            "VALUES (%s, %s)",
                            (
                                user["id"],
                                "Votre mot de passe est trop facile à trouver.",
                            ),
                        )
                        break
            connection.commit()
            return findings
        finally:
            connection.close()

    def create_user(self, username, password, pseudo=None, role="user"):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, pseudo, role) "
                    "VALUES (%s, %s, %s, %s)",
                    (username, self.hash_password(password), pseudo or username, role),
                )
                connection.commit()
        finally:
            connection.close()
