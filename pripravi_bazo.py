"""Enkratna skripta: ustvari bazo iz schema.sql. Obstoječe tabele izbriše."""

from app import app
from db import init_db

with app.app_context():
    init_db()

print("Baza je pripravljena.")
