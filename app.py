import os
import sqlite3
from functools import wraps
from flask import Flask, request, redirect, url_for, session, flash, render_template_string, g
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get("KELAJAK_DB_PATH", os.path.join(BASE_DIR, "kelajak_lideri.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("KELAJAK_SECRET_KEY", "LOCAL-TEST-ONLY-change-before-deploy")
ADMIN_USERNAME = os.environ.get("KELAJAK_ADMIN_USERNAME", "maslahatchi")
ADMIN_PASSWORD = os.environ.get("KELAJAK_ADMIN_PASSWORD", "ChangeMe-2026!")

STYLE = """
<style>
*{box-sizing:border-box}
:root{color-scheme:light;--navy:#142B52;--blue:#3478F6;--ink:#24324a;--muted:#68768c;--surface:#fff;--line:#e4e9f2;--page:#F5F7FB}
html{min-width:320px}
body{margin:0;background:var(--page);color:var(--ink);font:16px/1.6 "Segoe UI",Arial,sans-serif;-webkit-font-smoothing:antialiased}
header{padding:17px max(16px,calc((100% - 1120px)/2));border-bottom:3px solid var(--blue);background:var(--navy);color:var(--surface)}
.header-inner{display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:11px;color:var(--surface);text-decoration:none}
.brand-mark{display:grid;width:42px;height:42px;place-items:center;border:1px solid #ffffff30;border-radius:12px;background:#ffffff12;color:#fff;font-size:23px}
.brand-copy h1{margin:0;font-size:clamp(20px,2.7vw,27px);line-height:1.2;letter-spacing:-.45px}
.brand-copy p{margin:4px 0 0;color:#d4def0;font-size:13px}
nav{display:flex;flex-wrap:wrap;gap:6px}
nav a{padding:6px 10px;border:1px solid #ffffff26;border-radius:7px;background:#ffffff0c;color:var(--surface);font-size:13px;text-decoration:none;transition:background .16s ease,border-color .16s ease}
nav a:hover,nav a:focus-visible{border-color:#ffffff70;background:#ffffff20}
nav a.nav-cta{border-color:#3478f6;background:var(--blue)}
nav a.nav-cta:hover{background:#2464d9}
main{width:min(calc(100% - 32px),1040px);min-height:calc(100vh - 220px);margin:26px auto 38px}
.hero,.card{margin-bottom:15px;padding:21px 23px;border:1px solid var(--line);border-radius:12px;background:var(--surface);box-shadow:0 3px 12px #142b5209}
.hero{position:relative;overflow:hidden;padding:clamp(25px,4.2vw,38px);border:0;border-left:4px solid var(--blue);background:var(--navy);color:var(--surface);box-shadow:0 8px 24px #142b521c}
.hero:after{position:absolute;right:35px;bottom:-74px;color:#ffffff0c;content:"20";font-size:260px;font-weight:800;line-height:1;pointer-events:none}
.hero>*{position:relative;z-index:1}
.hero h2{max-width:680px;margin:15px 0 10px;color:var(--surface);font-size:clamp(28px,4.2vw,40px);line-height:1.18;letter-spacing:-.8px}
.hero p{max-width:650px;margin:0 0 20px;color:#d4def0}
main>h2{margin:25px 0 12px;color:var(--navy);font-size:21px;line-height:1.35}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:13px}
.grid .card{height:100%}
.grid .card:hover{border-color:#d5e1f7;box-shadow:0 7px 19px #142b5210}
.card h2,.card h3{margin:0 0 9px;color:var(--navy);line-height:1.35}
.card h2{font-size:22px}.card h3{font-size:17px}
.card p{margin:8px 0}
.form-card{width:min(100%,680px);margin-right:auto;margin-left:auto}
label{display:block;margin:10px 0 4px;color:var(--navy);font-size:14px;font-weight:600}
input,textarea,select{display:block;width:100%;margin:5px 0 13px;padding:10px 12px;border:1px solid #d5ddea;border-radius:7px;outline:none;background:var(--surface);color:var(--ink);font:inherit;transition:border-color .16s ease,box-shadow .16s ease}
input:focus,textarea:focus,select:focus{border-color:var(--blue);box-shadow:0 0 0 3px #3478f61a}
input::placeholder,textarea::placeholder{color:#8a96a8}
textarea{min-height:100px;resize:vertical}
button,.btn{display:inline-block;border:1px solid var(--blue);border-radius:7px;background:var(--blue);color:var(--surface);padding:9px 14px;font:600 15px/1.4 "Segoe UI",Arial,sans-serif;text-decoration:none;cursor:pointer;transition:background .16s ease,border-color .16s ease}
button:hover,.btn:hover{border-color:#2464d9;background:#2464d9}
.hero .btn{border-color:#fff;background:#fff;color:var(--navy)}
.hero .btn:hover{border-color:#e5edfc;background:#e5edfc}
.hero .btn+.btn{border-color:#ffffff55;background:#ffffff12;color:#fff}
.hero .btn+.btn:hover{border-color:#ffffff95;background:#ffffff22}
button:focus-visible,.btn:focus-visible{outline:3px solid #3478f655;outline-offset:2px}
main a:not(.btn){color:#2464d9}
.muted{color:var(--muted);font-size:14px}
.flash{margin:10px 0 16px;padding:10px 13px;border:1px solid #f0dda7;border-radius:8px;background:#fff8e7;color:#705515}
.tag{display:inline-block;padding:4px 9px;border-radius:20px;background:#edf3ff;color:#2459ad;font-size:12px;font-weight:600}
.hero .tag{border:1px solid #ffffff30;background:#ffffff12;color:#e5edff}
.feature-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:12px 0 24px}
.feature{display:flex;align-items:center;gap:10px;padding:12px 14px;border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--navy);font-size:14px;font-weight:600}
.feature-icon{display:grid;width:32px;height:32px;flex:0 0 32px;place-items:center;border-radius:8px;background:#edf3ff;color:var(--blue);font-size:16px}
.stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:12px 0 20px}
.stat{padding:12px 14px;border:1px solid var(--line);border-radius:9px;background:#f8faff}
.stat strong,.stat span{display:block}
.stat strong{color:var(--navy);font-size:23px;line-height:1.2}
.stat span{margin-top:4px;color:var(--muted);font-size:13px}
footer{padding:17px 16px;border-top:1px solid var(--line);color:var(--muted);text-align:center;font-size:13px}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
table{width:100%;min-width:540px;border-collapse:collapse}
td,th{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#f8faff;color:var(--navy);font-size:14px}
@media(max-width:700px){.header-inner{align-items:flex-start;gap:13px}nav{width:100%}}
@media(max-width:600px){header{padding:16px 14px}.brand-mark{width:38px;height:38px}.brand-copy h1{font-size:20px}.brand-copy p{font-size:12px}nav{gap:6px}nav a{padding:6px 8px;font-size:12px}main{width:calc(100% - 24px);margin:17px auto 28px}.hero,.card{padding:17px;margin-bottom:11px}.hero{padding:22px 18px}.hero:after{right:-20px;bottom:-32px;font-size:150px}.hero h2{font-size:28px}.hero p{font-size:15px}main>h2{font-size:19px;margin-top:21px}.grid{gap:10px}.feature-row{grid-template-columns:1fr;gap:7px;margin:10px 0 20px}.feature{padding:9px 11px}.stats{gap:8px}.stat{padding:10px 11px}button,.btn{padding:9px 12px}table{font-size:14px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important}}
</style>
"""

LAYOUT = """<!doctype html><html lang='uz'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{{ title }} | KELAJAK LIDERI</title>""" + STYLE + """</head><body>
<header><div class='header-inner'><a class='brand' href='{{ url_for("home") }}'><span class='brand-mark' aria-hidden='true'>✦</span><span class='brand-copy'><h1>20-MAKTAB — KELAJAK LIDERI</h1><p>O‘quvchilar tashabbusi va yangi g‘oyalar</p></span></a><nav>
<a href='{{ url_for("home") }}'>Bosh sahifa</a><a href='{{ url_for("ideas_page") }}'>G‘oyalar</a><a href='{{ url_for("events_page") }}'>Tadbirlar</a>
{% if session.get('user_id') %}<a href='{{ url_for("dashboard") }}'>Kabinetim</a><a href='{{ url_for("logout") }}'>Chiqish</a>{% else %}<a href='{{ url_for("login") }}'>Kirish</a><a class='nav-cta' href='{{ url_for("register") }}'>Ro‘yxatdan o‘tish</a>{% endif %}
{% if session.get('is_admin') %}<a class='nav-cta' href='{{ url_for("admin") }}'>Boshqaruv</a>{% else %}<a href='{{ url_for("admin_login") }}'>Maslahatchi</a>{% endif %}
</nav></div></header><main>{% with messages=get_flashed_messages() %}{% for message in messages %}<div class='flash'>{{ message }}</div>{% endfor %}{% endwith %}{{ body|safe }}</main><footer>20-MAKTAB • KELAJAK LIDERI | Birgalikda yangi g‘oyalar sari!</footer></body></html>"""

def page(title, body, **context):
    return render_template_string(LAYOUT, title=title, body=render_template_string(body, **context))

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, class_name TEXT NOT NULL, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS ideas (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))")
        conn.execute("CREATE TABLE IF NOT EXISTS votes (user_id INTEGER NOT NULL, idea_id INTEGER NOT NULL, PRIMARY KEY(user_id, idea_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, event_date TEXT NOT NULL, description TEXT NOT NULL)")
        count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        if count == 0:
            conn.executemany("INSERT INTO events(title,event_date,description) VALUES(?,?,?)", [
                ("Yosh liderlar uchrashuvi", "2026-11-05", "O‘quvchilar tashabbuslari va yetakchilik haqida suhbat."),
                ("Eng yaxshi yangi g‘oya", "2026-11-12", "Maktab hayotini yaxshilaydigan takliflar tanlovi."),
                ("Maktabimiz — yashil makon", "2026-11-20", "Ekologik madaniyat va tabiatni asrash tadbiri.")])

COORDINATORS = [
    ("💻 IT koordinatori", "Raqamli texnologiyalar va innovatsiyalar"),
    ("📚 Ta’lim koordinatori", "Bilim, kitobxonlik va fan olimpiadalari"),
    ("⚽ Sport koordinatori", "Sog‘lom turmush tarzi va sport"),
    ("🎭 Madaniyat koordinatori", "San’at, ijod va milliy qadriyatlar"),
    ("🌱 Ekologiya koordinatori", "Tabiatni asrash va yashil makon"),
    ("🤝 Ijtimoiy tashabbus koordinatori", "Mehr-oqibat va ijtimoiy tashabbuslar"),
    ("👑 Kelajak lideri koordinatori", "Yetakchilik va yangi tashabbuslar"),
    ("🎥 Media koordinatori", "Maktab yangiliklari va media ijod"),
]

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Bu bo‘lim uchun avval tizimga kiring.")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    latest = db().execute("SELECT ideas.*, users.full_name, (SELECT COUNT(*) FROM votes WHERE votes.idea_id=ideas.id) AS vote_count FROM ideas JOIN users ON users.id=ideas.user_id ORDER BY ideas.id DESC LIMIT 3").fetchall()
    body = """
    <section class='hero'><span class='tag'>20-MAKTAB <span aria-hidden='true'>·</span> 2026–2027</span><h2>G‘oyangni bildir. Tashabbus ko‘rsat. Yetakchi bo‘l!</h2><p>Yaxshi g‘oyalar katta o‘zgarishlarning boshlanishi. Taklif ber, maktab hayotiga qo‘shil va tengdoshlaring bilan birga tashabbus ko‘rsat.</p><a class='btn' href='{{ url_for("register") }}'>Platformaga qo‘shilish</a> <a class='btn' href='{{ url_for("ideas_page") }}'>G‘oyalarni ko‘rish</a></section>
    <div class='feature-row'><div class='feature'><span class='feature-icon' aria-hidden='true'>✎</span>O‘quvchilar tashabbusi</div><div class='feature'><span class='feature-icon' aria-hidden='true'>♡</span>G‘oyalarni qo‘llab-quvvatlash</div><div class='feature'><span class='feature-icon' aria-hidden='true'>▦</span>Maktab tadbirlari</div></div>
    <h2>🧭 Koordinatorlar yo‘nalishlari</h2><div class='grid'>{% for name,desc in coordinators %}<section class='card'><h3>{{ name }}</h3><p>{{ desc }}</p></section>{% endfor %}</div>
    <h2>💡 Yangi g‘oyalar</h2><div class='grid'>{% for idea in latest %}<section class='card'><h3>{{ idea['title'] }}</h3><p>{{ idea['description'] }}</p><p class='muted'>Muallif: {{ idea['full_name'] }} · Ovozlar: {{ idea['vote_count'] }}</p></section>{% else %}<section class='card'>Hozircha g‘oyalar yo‘q. Birinchi bo‘lib o‘z taklifingizni yuboring!</section>{% endfor %}</div>
    """
    return page("Bosh sahifa", body, coordinators=COORDINATORS, latest=latest)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        class_name = request.form.get("class_name", "").strip()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        if not all([full_name, class_name, username, password]):
            flash("Barcha maydonlarni to‘ldiring.")
        elif len(username) < 3 or len(password) < 8:
            flash("Login kamida 3 ta, parol esa kamida 8 ta belgidan iborat bo‘lsin.")
        else:
            try:
                db().execute("INSERT INTO users(full_name,class_name,username,password_hash) VALUES(?,?,?,?)", (full_name, class_name, username, generate_password_hash(password)))
                db().commit()
                flash("Ro‘yxatdan o‘tish muvaffaqiyatli! Endi tizimga kiring.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Bu login band. Boshqa login tanlang.")
    body = """<section class='card form-card'><h2>👤 O‘quvchi ro‘yxatdan o‘tishi</h2><form method='post'><label>Ism-familiya</label><input name='full_name' required maxlength='100'><label>Sinf (masalan, 8-A)</label><input name='class_name' required maxlength='20'><label>Login</label><input name='username' required minlength='3' maxlength='40' autocomplete='username'><label>Parol (kamida 8 belgi)</label><input type='password' name='password' required minlength='8' autocomplete='new-password'><button>Ro‘yxatdan o‘tish</button></form><p class='muted'>Haqiqiy o‘quvchilar ma’lumotlarini internetga joylashdan oldin maktab rahbariyati bilan maxfiylik va ruxsat masalasini kelishib oling.</p></section>"""
    return page("Ro‘yxatdan o‘tish", body)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = db().execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear(); session["user_id"] = user["id"]; session["username"] = user["username"]
            flash("Xush kelibsiz!")
            return redirect(url_for("dashboard"))
        flash("Login yoki parol noto‘g‘ri.")
    body = """<section class='card form-card'><h2>🔐 Tizimga kirish</h2><form method='post'><label>Login</label><input name='username' required autocomplete='username'><label>Parol</label><input type='password' name='password' required autocomplete='current-password'><button>Kirish</button></form></section>"""
    return page("Kirish", body)

@app.route("/logout")
def logout():
    session.clear(); flash("Tizimdan chiqdingiz."); return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = db().execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    mine = db().execute("SELECT * FROM ideas WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    body = """<section class='card'><h2>🧑‍🎓 Shaxsiy kabinet</h2><p><b>{{ user['full_name'] }}</b></p><p>Sinf: {{ user['class_name'] }} · Login: {{ user['username'] }}</p><a class='btn' href='{{ url_for("ideas_page") }}'>G‘oya yuborish</a></section><section class='card'><h3>Mening g‘oyalarim</h3>{% for idea in mine %}<p><b>{{ idea['title'] }}</b> — {{ idea['description'] }}</p>{% else %}<p>Hali g‘oya yubormagansiz.</p>{% endfor %}</section>"""
    return page("Shaxsiy kabinet", body, user=user, mine=mine)

@app.route("/ideas")
def ideas_page():
    rows = db().execute("SELECT ideas.*, users.full_name, (SELECT COUNT(*) FROM votes WHERE votes.idea_id=ideas.id) AS vote_count FROM ideas JOIN users ON users.id=ideas.user_id ORDER BY ideas.id DESC").fetchall()
    body = """<section class='card'><h2>💡 G‘oyalar banki</h2>{% if session.get('user_id') %}<form method='post' action='{{ url_for("add_idea") }}'><label>G‘oya nomi</label><input name='title' required maxlength='120'><label>G‘oya tavsifi</label><textarea name='description' required maxlength='1500'></textarea><button>G‘oyani yuborish</button></form>{% else %}<p>G‘oya yuborish uchun <a href='{{ url_for("login") }}'>tizimga kiring</a>.</p>{% endif %}</section><div class='grid'>{% for idea in rows %}<section class='card'><h3>{{ idea['title'] }}</h3><p>{{ idea['description'] }}</p><p class='muted'>Muallif: {{ idea['full_name'] }} · Ovozlar: {{ idea['vote_count'] }}</p>{% if session.get('user_id') %}<form method='post' action='{{ url_for("vote", idea_id=idea["id"]) }}'><button>👍 Ovoz berish</button></form>{% endif %}</section>{% else %}<section class='card'>Birinchi g‘oyani siz yuboring!</section>{% endfor %}</div>"""
    return page("G‘oyalar", body, rows=rows)

@app.route("/idea", methods=["POST"])
@login_required
def add_idea():
    title = request.form.get("title", "").strip(); description = request.form.get("description", "").strip()
    if title and description:
        db().execute("INSERT INTO ideas(user_id,title,description) VALUES(?,?,?)", (session["user_id"], title, description)); db().commit()
        flash("G‘oyangiz saqlandi. Rahmat!")
    else: flash("G‘oya nomi va tavsifini kiriting.")
    return redirect(url_for("ideas_page"))

@app.route("/vote/<int:idea_id>", methods=["POST"])
@login_required
def vote(idea_id):
    exists = db().execute("SELECT id FROM ideas WHERE id=?", (idea_id,)).fetchone()
    if not exists:
        flash("G‘oya topilmadi.")
    else:
        try:
            db().execute("INSERT INTO votes(user_id,idea_id) VALUES(?,?)", (session["user_id"], idea_id)); db().commit(); flash("Ovozingiz qabul qilindi.")
        except sqlite3.IntegrityError:
            flash("Siz bu g‘oyaga oldin ovoz bergansiz.")
    return redirect(url_for("ideas_page"))

@app.route("/events")
def events_page():
    events = db().execute("SELECT * FROM events ORDER BY event_date").fetchall()
    body = """<h2>📅 Tadbirlar taqvimi</h2><div class='grid'>{% for event in events %}<section class='card'><span class='tag'>{{ event['event_date'] }}</span><h3>{{ event['title'] }}</h3><p>{{ event['description'] }}</p></section>{% else %}<section class='card'>Hozircha tadbirlar kiritilmagan.</section>{% endfor %}</div>"""
    return page("Tadbirlar", body, events=events)

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear(); session["is_admin"] = True
            return redirect(url_for("admin"))
        flash("Administrator login yoki paroli noto‘g‘ri.")
    body = """<section class='card form-card'><h2>🛡️ Maslahatchi kirishi</h2><form method='post'><label>Administrator login</label><input name='username' required><label>Parol</label><input type='password' name='password' required><button>Kirish</button></form><p class='muted'>Mahalliy sinov uchun standart sozlama kodda berilgan. Saytni internetga joylashdan oldin administrator paroli va maxfiy kalitni albatta o‘zgartiring.</p></section>"""
    return page("Administrator kirishi", body)

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    if request.method == "POST":
        title = request.form.get("title", "").strip(); event_date = request.form.get("event_date", "").strip(); description = request.form.get("description", "").strip()
        if title and event_date and description:
            db().execute("INSERT INTO events(title,event_date,description) VALUES(?,?,?)", (title,event_date,description)); db().commit(); flash("Tadbir qo‘shildi.")
        else: flash("Tadbirning barcha maydonlarini to‘ldiring.")
        return redirect(url_for("admin"))
    events = db().execute("SELECT * FROM events ORDER BY event_date").fetchall()
    ideas = db().execute("SELECT ideas.*, users.full_name FROM ideas JOIN users ON users.id=ideas.user_id ORDER BY ideas.id DESC").fetchall()
    users_count = db().execute("SELECT COUNT(*) FROM users").fetchone()[0]
    body = """<section class='card'><h2>🛡️ Administrator paneli</h2><div class='stats'><div class='stat'><strong>{{ users_count }}</strong><span>Ro‘yxatdan o‘tgan o‘quvchilar</span></div><div class='stat'><strong>{{ ideas|length }}</strong><span>Yuborilgan g‘oyalar</span></div></div><h3>Yangi tadbir qo‘shish</h3><form method='post'><label>Tadbir nomi</label><input name='title' required><label>Sana</label><input type='date' name='event_date' required><label>Tavsif</label><textarea name='description' required></textarea><button>Tadbirni saqlash</button></form></section><section class='card'><h3>G‘oyalar ro‘yxati</h3><div class='table-wrap'><table><tr><th>G‘oya</th><th>Muallif</th><th>Tavsif</th></tr>{% for idea in ideas %}<tr><td>{{ idea['title'] }}</td><td>{{ idea['full_name'] }}</td><td>{{ idea['description'] }}</td></tr>{% else %}<tr><td colspan='3'>Hozircha g‘oyalar yo‘q.</td></tr>{% endfor %}</table></div></section><section class='card'><h3>Tadbirlar</h3>{% for event in events %}<p><b>{{ event['event_date'] }}</b> — {{ event['title'] }}</p>{% endfor %}</section><p><a class='btn' href='{{ url_for("admin_logout") }}'>Administrator panelidan chiqish</a></p>"""
    return page("Boshqaruv paneli", body, events=events, ideas=ideas, users_count=users_count)

@app.route("/admin-logout")
def admin_logout():
    session.clear(); flash("Administrator panelidan chiqdingiz."); return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    print("KELAJAK LIDERI ishga tushmoqda: http://127.0.0.1:5000")
    print("Mahalliy sinov administrator login: maslahatchi")
    print("Mahalliy sinov administrator paroli: ChangeMe-2026!")
    print("OGOHLANTIRISH: internetga joylashdan oldin KELAJAK_ADMIN_PASSWORD va KELAJAK_SECRET_KEY ni xavfsiz qiymatlarga almashtiring.")
    app.run(debug=False, host="127.0.0.1", port=5000)
