# app.py
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_httpauth import HTTPBasicAuth
import RPi.GPIO as GPIO
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key'          # <<< CHANGE IN PRODUCTION

# ----------------------------------------------------------------------
# 1. BASIC AUTH
# ----------------------------------------------------------------------
auth = HTTPBasicAuth()
users = {
    "admin": generate_password_hash("password")   # <<< CHANGE USER/PASS
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# ----------------------------------------------------------------------
# 2. GPIO SETUP (gate)
# ----------------------------------------------------------------------
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GATE_PIN = 7
GPIO.setup(GATE_PIN, GPIO.OUT)
GPIO.output(GATE_PIN, GPIO.LOW)

# ----------------------------------------------------------------------
# 3. TEXT-FILE PATHS
# ----------------------------------------------------------------------
FILE1_PATH = '/home/hmd82/parking/phoneOn.txt'   # Phone Name
FILE2_PATH = '/home/hmd82/parking/rfid.txt'      # RFID Name

for p in (FILE1_PATH, FILE2_PATH):
    if not os.path.exists(p):
        open(p, 'w').close()

# ----------------------------------------------------------------------
# 4. TEXT-FILE HELPERS
# ----------------------------------------------------------------------
def read_entries(path):
    entries = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            key, _, name = line.partition(' ')
            entries.append([key, name])
    return entries

def write_entries(path, entries):
    with open(path, 'w') as f:
        for key, name in entries:
            f.write(f"{key} {name}\n")

# ----------------------------------------------------------------------
# 5. ROUTES
# ----------------------------------------------------------------------
@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')

# ---------- Open Gate ----------
@app.route('/open_gate', methods=['POST'])
@auth.login_required
def open_gate():
    GPIO.output(GATE_PIN, GPIO.HIGH)
    import time
    time.sleep(1)
    GPIO.output(GATE_PIN, GPIO.LOW)
    flash('Gate opened!')
    return redirect(url_for('index'))

# ---------- Reboot ----------
@app.route('/reboot', methods=['POST'])
@auth.login_required
def reboot():
    flash('Rebooting Raspberry Pi...')
    os.system('sudo reboot')
    return redirect(url_for('index'))

# ---------- phoneOn.txt CRUD ----------
@app.route('/phoneOn', methods=['GET', 'POST'])
@auth.login_required
def phoneOn():
    entries = read_entries(FILE1_PATH)

    if request.method == 'POST':
        action = request.form.get('action')
        key = request.form.get('key')
        name = request.form.get('name')

        if action == 'add' and key and name:
            entries.append([key, name])
            write_entries(FILE1_PATH, entries)
            flash('Phone entry added')
        elif action == 'delete':
            idx = int(request.form.get('index'))
            if 0 <= idx < len(entries):
                entries.pop(idx)
                write_entries(FILE1_PATH, entries)
                flash('Phone entry deleted')
        elif action == 'update' and key and name:
            idx = int(request.form.get('index'))
            if 0 <= idx < len(entries):
                entries[idx] = [key, name]
                write_entries(FILE1_PATH, entries)
                flash('Phone entry updated')
        return redirect(url_for('phoneOn'))

    return render_template(
        'file.html',
        file_name='phoneOn.txt',
        entries=entries,
        file_route='phoneOn',
        col1_label='Phone',
        col2_label='Name'
    )

# ---------- rfid.txt CRUD ----------
@app.route('/rfid', methods=['GET', 'POST'])
@auth.login_required
def rfid():
    entries = read_entries(FILE2_PATH)

    if request.method == 'POST':
        action = request.form.get('action')
        key = request.form.get('key')
        name = request.form.get('name')

        if action == 'add' and key and name:
            entries.append([key, name])
            write_entries(FILE2_PATH, entries)
            flash('RFID entry added')
        elif action == 'delete':
            idx = int(request.form.get('index'))
            if 0 <= idx < len(entries):
                entries.pop(idx)
                write_entries(FILE2_PATH, entries)
                flash('RFID entry deleted')
        elif action == 'update' and key and name:
            idx = int(request.form.get('index'))
            if 0 <= idx < len(entries):
                entries[idx] = [key, name]
                write_entries(FILE2_PATH, entries)
                flash('RFID entry updated')
        return redirect(url_for('rfid'))

    return render_template(
        'file.html',
        file_name='rfid.txt',
        entries=entries,
        file_route='rfid',
        col1_label='RFID',
        col2_label='Name'
    )

# ----------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)