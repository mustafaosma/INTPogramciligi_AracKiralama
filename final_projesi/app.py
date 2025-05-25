from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar'

def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS kiralamalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            arac_id INTEGER,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (arac_id) REFERENCES araclar(id)
        )""")
        c.execute("""
         CREATE TABLE IF NOT EXISTS mesajlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS araclar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            resim_yolu TEXT,
            fiyat INTEGER
        )""")
        conn.commit()
        c.execute("SELECT count(*) FROM araclar")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("BMW 3 Serisi", "static/3-serisi-sedan.png", 500))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("Mercedes Benz A-Class", "static/mercedes-benz-a-class-w177-696x392-08-2022.avif", 600))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("Volkswagen Golf", "static/golf.png", 400))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("BMW 1.20 M Sport", "static/enterprisesol_638694172493579582.png", 1200))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("Volvo XC90", "static/volvoxc90.png", 800))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("Mercedes Vito Dizel", "static/mercedesvitosol.png", 1000))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("Volkswagen Caddy", "static/Caddy.png", 400))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("Renault Megane", "static/megane.png", 450))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("Renault Clio", "static/clio.png", 500))
            c.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                      ("Ford Focus", "static/fordf.png", 700))
            conn.commit()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        return_date = request.form.get('return-date')
        return_condition = request.form.get('return-condition')
        return_comments = request.form.get('return-comments')

        return redirect(url_for('iade_basarili'))

    return render_template('index.html')

@app.route('/iade-basarili')
def iade_basarili():
    return render_template('iade_basarili.html')

@app.route('/araclar')
def araclar():
    with sqlite3.connect("database.db") as conn:
        araclar = conn.execute("SELECT * FROM araclar").fetchall()
    return render_template('araclar.html', araclar=araclar)

@app.route('/iletisim', methods=['GET', 'POST'])
def iletisim():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO mesajlar (name, email, message) VALUES (?, ?, ?)", (name, email, message))
            conn.commit()
        
        return redirect(url_for('tesekkur'))

    return render_template('iletisim.html')

@app.route('/fiyatlar')
def fiyatlar():
    return render_template('fiyatlar.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect('/login')
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    cur.execute("""
        SELECT kiralamalar.id, users.username, araclar.isim, kiralamalar.tarih
        FROM kiralamalar
        JOIN users ON kiralamalar.user_id = users.id
        JOIN araclar ON kiralamalar.arac_id = araclar.id
    """)
    kiralamalar = cur.fetchall()

    cur.execute("SELECT * FROM araclar")
    araclar = cur.fetchall()
    cur.execute("SELECT * FROM mesajlar ORDER BY timestamp DESC")
    mesajlar = cur.fetchall()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    con.close()
    return render_template('admin.html', kiralamalar=kiralamalar, araclar=araclar, users=users,mesajlar=mesajlar)

@app.route("/toggle_admin/<int:user_id>", methods=["POST"])
def toggle_admin(user_id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if user:
            new_is_admin = 1 if user[0] == 0 else 0
            c.execute("UPDATE users SET is_admin = ? WHERE id = ?", (new_is_admin, user_id))
            conn.commit()
    return redirect(url_for("admin"))

@app.route("/kirala/<int:arac_id>", methods=["GET", "POST"])
def kirala(arac_id):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM araclar WHERE id = ?", (arac_id,))
        arac = c.fetchone()
        if not arac:
            flash("Araç bulunamadı.", "danger")
            return redirect(url_for("araclar"))

    if request.method == 'POST':
        user_id = session.get('user_id')

        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO kiralamalar (user_id, arac_id) VALUES (?, ?)
            """, (user_id, arac_id))
            conn.commit()

        return redirect(url_for('kiralama_basarili'))

    return render_template("kirala_arac.html", arac=arac)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id, password_hash, is_admin FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            if user and check_password_hash(user[1], password):
                session["user_id"] = user[0]
                session["username"] = username
                session["is_admin"] = bool(user[2])
                return redirect(url_for("admin") if session["is_admin"] else url_for("index"))
            else:
                flash("Geçersiz kullanıcı adı veya şifre", "danger")
    return render_template("login.html")

@app.route('/arac_ekle', methods=['POST'])
def arac_ekle():
    if 'user_id' not in session:
        return redirect('/login')
    isim = request.form.get('isim')
    resim_yolu = request.form.get('resim_yolu')
    fiyat = request.form.get('fiyat')

    if not isim:
        flash("Araç ismi boş olamaz!", "danger")
        return redirect('/admin')

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO araclar (isim, resim_yolu, fiyat) VALUES (?, ?, ?)",
                    (isim, resim_yolu, fiyat))
        con.commit()

    flash("Araç başarıyla eklendi.", "success")
    return redirect('/admin')

@app.route("/arac_sil/<int:arac_id>", methods=["POST"])
def arac_sil(arac_id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    with sqlite3.connect("database.db") as conn:
        conn.execute("DELETE FROM araclar WHERE id = ?", (arac_id,))
        conn.commit()
    flash("Araç başarıyla silindi", "success")
    return redirect(url_for("admin"))

@app.route('/arac_duzenle/<int:id>', methods=['GET', 'POST'])
def arac_duzenle(id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    if request.method == 'POST':
        isim = request.form['isim']
        resim_yolu = request.form['resim_yolu']
        fiyat = request.form['fiyat']
        cur.execute("UPDATE araclar SET isim=?, resim_yolu=?, fiyat=? WHERE id=?", (isim, resim_yolu, fiyat, id))
        con.commit()
        con.close()
        return redirect('/admin')
    else:
        cur.execute("SELECT * FROM araclar WHERE id=?", (id,))
        arac = cur.fetchone()
        con.close()
        return render_template('arac_duzenle.html', arac=arac)

@app.route('/kullanici_sil/<int:id>')
def kullanici_sil(id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect('/admin')

@app.route('/yetki_ver/<int:id>')
def yetki_ver(id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET yetki=1 WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect('/admin')

@app.route('/yetki_al/<int:id>')
def yetki_al(id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET yetki=0 WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('index'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hash_pw = generate_password_hash(password)
        try:
            with sqlite3.connect("database.db") as conn:
                conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_pw))
                conn.commit()
            flash("Kayıt başarılı. Giriş yapabilirsiniz.", "success")
            return redirect(url_for("login"))
        except:
            flash("Kullanıcı adı zaten var.", "danger")
    return render_template("register.html")

@app.route('/tesekkur')
def tesekkur():
 return render_template('tesekkur.html')

@app.route('/kiralama-basarili')
def kiralama_basarili():
    return render_template('kiralama_basarili.html')

@app.route("/kampanyalar")
def kampanyalar():
    return render_template("kampanyalar.html")

@app.route("/kiralama_sil/<int:id>", methods=["POST"])
def kiralama_sil(id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    with sqlite3.connect("database.db") as conn:
        conn.execute("DELETE FROM kiralamalar WHERE id = ?", (id,))
        conn.commit()
    flash("Kiralama kaydı silindi", "success")
    return redirect(url_for("admin"))

#if __name__ == '__main__':
#    with app.app_context():
#        db.create_all()
#    app.run(debug=True)


import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
