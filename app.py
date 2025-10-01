from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import sqlite3
import os

# E-posta gönderme modülünüzün içe aktarıldığını varsayıyoruz.
from send_email import send_email_to_admin, send_email_to_customer 

app = Flask(__name__)

# --- GÜVENLİK AYARLARI ---
# Oturumları (Session) kullanmak için gizli bir anahtar şarttır.
# Geliştirme ortamı için basit bir değer kullanıyoruz. Gerçek projede bunu güçlü ve gizli tutun!
app.secret_key = os.environ.get('SECRET_KEY', 'cok-gizli-anahtar-12345')

# Admin Giriş Bilgileri
ADMIN_USER = "admin"
ADMIN_PASSWORD = "cokguclusifre1907" # Lütfen bunu gerçek bir şifre ile değiştirin!

# --- Veritabanı Fonksiyonları ---

def init_db():
    """Uygulama başladığında veritabanı tablolarını oluşturur veya kontrol eder."""
    try:
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        
        # 1. Başvurular Tablosu (email sütunu eklendi)
        c.execute('''CREATE TABLE IF NOT EXISTS basvurular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            telefon TEXT NOT NULL,
            email TEXT,               
            adres TEXT,
            paket TEXT,
            durum TEXT DEFAULT 'Bekliyor',
            tarih TEXT DEFAULT (datetime('now', 'localtime'))
        )''')
        
        # 2. Altyapı Sorgulama Talepleri Tablosu
        c.execute('''CREATE TABLE IF NOT EXISTS altyapi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adres TEXT NOT NULL,
            tarih TEXT DEFAULT (datetime('now', 'localtime')),
            durum TEXT DEFAULT 'Bekliyor'
        )''')

        # 3. Bayilik Başvuruları Tablosu 
        c.execute('''CREATE TABLE IF NOT EXISTS bayilik (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adSoyad TEXT NOT NULL,
            telefon TEXT NOT NULL,
            ePosta TEXT,
            il TEXT,
            mesaj TEXT,
            durum TEXT DEFAULT 'Bekliyor',
            tarih TEXT DEFAULT (datetime('now', 'localtime'))
        )''')
        
        # 4. İletişim Mesajları Tablosu 
        c.execute('''CREATE TABLE IF NOT EXISTS iletisim_mesajlari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            email TEXT NOT NULL,
            konu TEXT,
            mesaj TEXT NOT NULL,
            durum TEXT DEFAULT 'Bekliyor',
            tarih TEXT DEFAULT (datetime('now', 'localtime'))
        )''')
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Veritabanı oluşturma/kontrol hatası: {e}")
    finally:
        if conn:
            conn.close()

# Veritabanını başlat
init_db()

# --- YENİ EKLENEN GÜVENLİK UÇ NOKTALARI ---

@app.route('/login', methods=['POST'])
def login():
    """Admin girişi kontrolü."""
    data = request.form
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('admin'))
    else:
        # Hata mesajı ile admin sayfasına geri yönlendir, ancak hata mesajını session ile taşı
        session['login_error'] = 'Kullanıcı adı veya şifre hatalı!'
        return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    """Admin çıkışı."""
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- API Uç Noktaları (Değişmedi) ---

@app.route('/submit', methods=['POST'])
def submit():
    """Yeni bir müşteri başvurusunu alır ve veritabanına kaydeder. (EMAIL DAHİL)"""
    try:
        data = request.get_json()
        
        ad = data.get('ad')
        telefon = data.get('telefon')
        adres = data.get('adres', 'Belirtilmedi')
        paket = data.get('paket', 'Belirtilmedi') 
        email = data.get('email', '') 

        if not ad or not telefon:
            return jsonify({'success': False, 'message': 'Ad ve telefon alanı zorunludur.'}), 400

        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO basvurular (ad, telefon, email, adres, paket) VALUES (?, ?, ?, ?, ?)", 
                      (ad, telefon, email, adres, paket))
            
        try:
                send_email_to_admin(data)
                if email:
                   send_email_to_customer(email, ad)
                pass
        except Exception as email_e:
              print(f"E-posta gönderme hatası: {email_e}")
        
        return jsonify({'success': True, 'message': 'Başvurunuz başarıyla alındı.'})

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return jsonify({'success': False, 'message': f'Sunucu hatası: {str(e)}'}), 500

@app.route('/submit-bayilik', methods=['POST'])
def submit_bayilik():
    """Yeni bir bayilik başvurusunu alır ve veritabanına kaydeder."""
    try:
        data = request.get_json()
        
        adSoyad = data.get('adSoyad')
        telefon = data.get('telefon')
        ePosta = data.get('ePosta', 'Belirtilmedi')
        il = data.get('il', 'Belirtilmedi')
        mesaj = data.get('mesaj', '') 

        if not adSoyad or not telefon:
            return jsonify({'success': False, 'message': 'Ad Soyad ve telefon alanı zorunludur.'}), 400

        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO bayilik (adSoyad, telefon, ePosta, il, mesaj) VALUES (?, ?, ?, ?, ?)", 
                      (adSoyad, telefon, ePosta, il, mesaj))
            
        try:
              pass
        except Exception as email_e:
              print(f"Bayilik E-posta gönderme hatası: {email_e}")
        
        return jsonify({'success': True, 'message': 'Bayilik başvurunuz başarıyla alındı.'})

    except Exception as e:
        print(f"Bayilik Başvuru Hatası: {e}")
        return jsonify({'success': False, 'message': f'Sunucu hatası: {str(e)}'}), 500

@app.route('/infra', methods=['POST'])
def infra():
    """Altyapı sorgulamasını simüle eder ve kaydeder."""
    try:
        data = request.get_json()
        adres = data.get('adres')
        
        if not adres:
             return jsonify({"status": "error", "message": "Adres alanı zorunludur."}), 400

        if "Fiber" in adres or "Merkez" in adres or "Bulvar" in adres:
            sonuc = "✅ Fiber altyapı mevcut. 1000 Mbps'e kadar hız destekleniyor."
        else:
            sonuc = "ℹ️ Bu adreste sadece ADSL/VDSL altyapısı mevcut."

        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO altyapi (adres, durum) VALUES (?, ?)",
                      (adres, sonuc))
            
        return jsonify({"status": "ok", "sonuc": sonuc})
    except Exception as e:
        print(f"Altyapı Sorgu Hatası: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    """İletişim formu mesaj kaydetme endpoint'i"""
    try:
        data = request.get_json()
        
        ad = data.get('name')
        email = data.get('email')
        konu = data.get('subject', 'Konu Yok')
        mesaj = data.get('message') 

        if not ad or not email or not mesaj:
            return jsonify({'success': False, 'message': 'Ad, e-posta ve mesaj alanları zorunludur.'}), 400

        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO iletisim_mesajlari (ad, email, konu, mesaj) VALUES (?, ?, ?, ?)", 
                      (ad, email, konu, mesaj))
            
        return jsonify({'success': True, 'message': 'Mesajınız başarıyla alındı.'})

    except Exception as e:
        print(f"İletişim Mesajı Kayıt Hatası: {e}")
        return jsonify({'success': False, 'message': f'Sunucu hatası: {str(e)}'}), 500


# --- Admin API Uç Noktaları (Giriş zorunluluğu eklenmedi, zaten /admin ile korunacak) ---

@app.route('/admin-api/basvurular')
def get_basvurular():
    try:
        with sqlite3.connect('data.db') as conn:
            conn.row_factory = sqlite3.Row 
            c = conn.cursor()
            c.execute("SELECT id, ad, telefon, email, adres, paket, durum, tarih FROM basvurular ORDER BY id DESC")
            basvurular = [dict(row) for row in c.fetchall()]
        return jsonify(basvurular)
    except Exception as e:
        print(f"/admin-api/basvurular Hatası: {e}")
        return jsonify({'error': 'Sunucu Hatası: Başvurular çekilemedi.'}), 500

@app.route('/admin-api/altyapi')
def get_altyapi():
    try:
        with sqlite3.connect('data.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT id, adres, tarih, durum FROM altyapi ORDER BY id DESC")
            altyapi = [dict(row) for row in c.fetchall()]
        return jsonify(altyapi)
    except Exception as e:
        print(f"/admin-api/altyapi Hatası: {e}")
        return jsonify({'error': 'Sunucu Hatası: Altyapı talepleri çekilemedi.'}), 500

@app.route('/admin-api/bayilik')
def get_bayilik():
    try:
        with sqlite3.connect('data.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT id, adSoyad, telefon, ePosta, il, mesaj, durum, tarih FROM bayilik ORDER BY id DESC")
            bayilik = [dict(row) for row in c.fetchall()]
        return jsonify(bayilik)
    except Exception as e:
        print(f"/admin-api/bayilik Hatası: {e}")
        return jsonify({'error': 'Sunucu Hatası: Bayilik başvuruları çekilemedi.'}), 500

@app.route('/admin-api/iletisim')
def get_iletisim():
    try:
        with sqlite3.connect('data.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT id, ad, email, konu, mesaj, durum, tarih FROM iletisim_mesajlari ORDER BY id DESC")
            mesajlar = [dict(row) for row in c.fetchall()]
        return jsonify(mesajlar)
    except Exception as e:
        print(f"/admin-api/iletisim Hatası: {e}")
        return jsonify({'error': 'Sunucu Hatası: İletişim mesajları çekilemedi.'}), 500
        
@app.route('/admin-api/update-status', methods=['POST'])
def update_status():
    try:
        data = request.get_json()
        item_id = data.get('id')
        item_type = data.get('type') 
        new_status = data.get('durum')

        if not item_id or not item_type or not new_status:
            return jsonify({'success': False, 'message': 'Eksik parametreler (id, type, durum).'}), 400

        if item_type == 'basvuru':
            table_name = 'basvurular'
        elif item_type == 'altyapi':
            table_name = 'altyapi'
        elif item_type == 'bayilik': 
            table_name = 'bayilik'
        elif item_type == 'iletisim': 
            table_name = 'iletisim_mesajlari'
        else:
            return jsonify({'success': False, 'message': 'Geçersiz tip (type).'}), 400
        
        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute(f"UPDATE {table_name} SET durum = ? WHERE id = ?", (new_status, item_id))
            
        return jsonify({'success': True, 'message': f'{table_name} durumu güncellendi.'})
    except Exception as e:
        print(f"Durum Güncelleme Hatası: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# --- Sayfa Yönlendirmeleri (HTML Şablonları) ---

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/admin')
def admin():
    """Admin sayfası, giriş kontrolü eklenmiştir."""
    # Eğer oturumda 'logged_in' True değilse, sadece giriş sayfasını göster
    if not session.get('logged_in'):
        # Session'daki hata mesajını çek ve temizle
        error = session.pop('login_error', None)
        return render_template("admin_login.html", error=error)
    
    # Giriş yapılmışsa, asıl admin panelini göster
    return render_template("admin.html")

# Diğer rotalar aynı kalır
@app.route('/hakkimizda')
def hakkimizda():
    return render_template("hakkimizda.html")

@app.route('/kampanyalar')
def kampanyalar():
    return render_template("kampanyalar.html")

@app.route('/iletisim')
def iletisim():
    return render_template("iletisim.html")

@app.route('/basvuru')
def basvuru():
    return render_template("basvuru.html")

@app.route('/numara-tasima')
def numara_tasima():
    return render_template("numara-tasima.html")

@app.route('/yeni-hat')
def yeni_hat():
    return render_template("yeni-hat.html")

@app.route('/bayilik')
def bayilik():
    return render_template("bayilik.html")

@app.route('/bayilik-programi')
def bayilik_programi():
    return render_template("bayilik-programi.html")

# Operatörler
@app.route('/turktelekom')
def turktelekom():
    return render_template("turktelekom.html")

@app.route('/turkcell')
def turkcell():
    return render_template("turkcell.html")

@app.route('/vodafone')
def vodafone():
    return render_template("vodafone.html")

# Blog
@app.route('/blog/ev-interneti')
def blog_ev_interneti():
    return render_template("blog-ev-interneti.html")

@app.route('/blog/teknoloji')
def blog_teknoloji():
    return render_template("blog-teknoloji.html")

@app.route('/blog/kampanya')
def blog_kampanya():
    return render_template("blog-kampanya.html")

@app.route('/blog/bayilik')
def blog_bayilik():
    return render_template("blog-bayilik.html")

# Yardım
@app.route('/yardim')
def yardim():
    return render_template("yardim.html")

@app.route('/yardim/hiz-test')
def yardim_hiz_test():
    return render_template("yardim-hiz-test.html")

@app.route('/yardim/ping')
def yardim_ping():
    return render_template("yardim-ping.html")

@app.route('/yardim/imei')
def yardim_imei():
    return render_template("yardim-imei.html")

@app.route('/yardim/ip')
def yardim_ip():
    return render_template("yardim-ip.html")

# Hukuki Sayfalar
@app.route('/gizlilik')
def gizlilik():
    return render_template("gizlilik.html")

@app.route('/cerez')
def cerez():
    return render_template("cerez.html")

@app.route('/kullanim')
def kullanim():
    return render_template("kullanim.html")


# --- Uygulama Başlatma ---

if __name__ == '__main__':
    app.run(debug=True)
