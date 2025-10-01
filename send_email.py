import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = 'samuelosayi70@gmail.com'
GMAIL_PASS = 'ehyg vpxs haab zzbz'  # Gmail uygulama şifresi

def send_email_to_admin(ad, telefon, adres, paket):
    try:
        msg = MIMEMultipart("alternative")
        msg['Subject'] = '📥 Bağlan360 Yeni Başvuru'
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER

        html = f"""
        <html>
          <body>
            <h3>Yeni Başvuru Alındı</h3>
            <p><strong>Ad:</strong> {ad}</p>
            <p><strong>Telefon:</strong> {telefon}</p>
            <p><strong>Adres:</strong> {adres}</p>
            <p><strong>Paket:</strong> {paket}</p>
            <hr>
            <small>Bağlan360 Otomatik Bildirim Sistemi</small>
          </body>
        </html>
        """

        msg.attach(MIMEText(html, "html", _charset="utf-8"))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        print("Yönetici e-postası gönderilemedi:", e)

def send_email_to_customer(email, ad):
    try:
        msg = MIMEMultipart("alternative")
        msg['Subject'] = '✅ Bağlan360 Başvuru Onayı'
        msg['From'] = GMAIL_USER
        msg['To'] = email

        html = f"""
        <html>
          <body>
            <h3>Sayın {ad},</h3>
            <p>Başvurunuz başarıyla alındı. En kısa sürede sizinle iletişime geçeceğiz.</p>
            <p>Herhangi bir sorunuz olursa bu e-posta adresinden bize ulaşabilirsiniz.</p>
            <hr>
            <small>Bağlan360 Destek Ekibi</small>
          </body>
        </html>
        """

        msg.attach(MIMEText(html, "html", _charset="utf-8"))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        print("Müşteri e-postası gönderilemedi:", e)