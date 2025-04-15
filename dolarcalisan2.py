from flask import Flask, request
import requests
from ftplib import FTP
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

@app.route("/altin-guncelle")
def update_html():
    token = request.args.get("token")
    if token != "gizli123":
        return "❌ Yetkisiz erişim"

    try:
        # --- Altın verisi ---
        altin_url = "https://bigpara.hurriyet.com.tr/api/v1/chart/exchangegold/2199/1"
        headers = {"User-Agent": "Mozilla/5.0"}
        altin_response = requests.get(altin_url, headers=headers)
        altin_data = altin_response.json()

        if isinstance(altin_data, dict) and "data" in altin_data:
            altin_listesi = altin_data["data"]
        elif isinstance(altin_data, list):
            altin_listesi = altin_data
        else:
            return "❌ Altın verisi formatı hatalı"

        altin_son = altin_listesi[-1]
        altin_fiyat_raw = altin_son["acilis"]
        altin_fiyat = str(int(float(altin_fiyat_raw)))  # Noktadan sonrası yok

        # --- Dolar verisi ---
        dolar_url = "https://bigpara.hurriyet.com.tr/api/v1/chart/exchangegold/1302/1"
        dolar_response = requests.get(dolar_url, headers=headers)
        dolar_data = dolar_response.json()

        if isinstance(dolar_data, dict) and "data" in dolar_data:
            dolar_listesi = dolar_data["data"]
        elif isinstance(dolar_data, list):
            dolar_listesi = dolar_data
        else:
            return "❌ Dolar verisi formatı hatalı"

        dolar_son = dolar_listesi[-1]
        dolar_fiyat_raw = dolar_son["acilis"]
        dolar_fiyat = f"{float(dolar_fiyat_raw):.2f}"  # Virgülden sonra 2 basamak

        # --- Türkiye saati (GMT+3) ---
        turkiye_saati = datetime.now(timezone.utc) + timedelta(hours=3)
        simdi = turkiye_saati.strftime("%Y-%m-%d %H:%M:%S")

        # --- HTML oluştur ---
        html = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Altın ve Dolar Fiyatları</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .icon {{
                    width: 64px;
                    height: 64px;
                    object-fit: contain;
                    margin-right: 12px;
                }}
                .card-title {{
                    font-size: 1.5rem;
                }}
                .price {{
                    font-size: 2.5rem;
                }}
                @media (max-width: 768px) {{
                    .price {{
                        font-size: 2rem;
                    }}
                    .icon {{
                        width: 56px;
                        height: 56px;
                    }}
                }}
            </style>
        </head>
        <body class="bg-light">
            <div class="container text-center mt-5 px-3">

                <div class="card shadow-lg rounded-4 mb-4">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <img src="https://i.imgur.com/wc8SRjA.jpeg" alt="Altın" class="icon">
                            <h1 class="price mb-0">{altin_fiyat} ₺</h1>
                        </div>
                    </div>
                </div>

                <div class="card shadow-lg rounded-4 mb-4">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <img src="https://i.imgur.com/RSHC4Hz.png" alt="Dolar" class="icon">
                            <h1 class="price mb-0">{dolar_fiyat} ₺</h1>
                        </div>
                    </div>
                </div>

                <p class="text-muted mt-3">Güncelleme Zamanı: {simdi}</p>
            </div>
        </body>
        </html>
        """

        # Dosya adları
        local_filename = "index.html"
        remote_filename = "/mehmetmutlu.online/htdocs/index.html"

        # HTML dosyasını yaz
        with open(local_filename, "w", encoding="utf-8") as file:
            file.write(html)

        # FTP ile yükle
        FTP_HOST = "ftpupload.net"
        FTP_USER = "if0_38743148"
        FTP_PASS = "01597530S"

        ftp = FTP()
        ftp.connect(FTP_HOST, 21)
        ftp.login(FTP_USER, FTP_PASS)

        with open(local_filename, "rb") as f:
            ftp.storbinary(f"STOR {remote_filename}", f)

        ftp.quit()

        return "✅ HTML başarıyla güncellendi ve yüklendi."

    except Exception as e:
        return f"❌ Hata oluştu: {e}"

# Flask uygulamasını başlat
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
