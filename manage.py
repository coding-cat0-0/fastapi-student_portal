# manage.py
import sys
import subprocess
import random
import string

def random_message(length=8):
    return "migration_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def makemigrations(msg=None):
    if not msg:
        msg = random_message()
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", msg])

def migrate():
    subprocess.run(["alembic", "upgrade", "head"])

def main():
    if len(sys.argv) < 2:
        # No arguments: default behavior (makemigrations + migrate with random name)
        msg = random_message()
        print(f"[INFO] No command provided. Generating migration with message: '{msg}'")
        makemigrations(msg)
        migrate()
        return

    command = sys.argv[1]

    if command == "makemigrations":
        msg = sys.argv[2] if len(sys.argv) > 2 else random_message()
        makemigrations(msg)
    elif command == "migrate":
        migrate()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python manage.py [makemigrations|migrate] [message]")

if __name__ == "__main__":
    main()
