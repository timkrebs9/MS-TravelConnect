#!/bin/sh

# Lade Umgebungsvariablen
export $(cat .env | xargs)

# Starte die Hauptanwendung
exec "$@"
