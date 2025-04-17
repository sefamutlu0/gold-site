from flask import Flask, request
import requests
from ftplib import FTP
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

@app.route("/altin-guncelle")
def update_html():
    # Token kontrolü
    token = request.args.get("token")
    if token != "gizli123":
        return "❌ Yetkisiz erişim"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        # --- Altın verisi ---
        altin_url = "https://bigpara.hurriyet.com.tr/api/v1/chart/exchangegold/2199/1"
        altin_response = requests.get(altin_url, headers=headers)
        altin_data = altin_response.json()
        altin_listesi = altin_data["data"] if "data" in altin_data else altin_data
        altin_son = altin_listesi[-1]
        altin_fiyat = int(float(altin_son["acilis"]))

        # --- Dolar verisi ---
        dolar_url = "https://bigpara.hurriyet.com.tr/api/v1/chart/exchangegold/1302/1"
        dolar_response = requests.get(dolar_url, headers=headers)
        dolar_data = dolar_response.json()
        dolar_listesi = dolar_data["data"] if "data" in dolar_data else dolar_data
        dolar_son = dolar_listesi[-1]
        dolar_fiyat = round(float(dolar_son["acilis"]), 2)

        crypto_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": "547c960c-9148-4e73-93dd-90eecc17cdcc"
        }

        params = {
            "symbol": "ADA,SOL,XRP",
            "convert": "USD"
        }

        response = requests.get(crypto_url, headers=headers, params=params)
        data = response.json()

        ada_fiyat = round(data["data"]["ADA"]["quote"]["USD"]["price"], 2)
        sol_fiyat = round(data["data"]["SOL"]["quote"]["USD"]["price"], 2)
        xrp_fiyat = round(data["data"]["XRP"]["quote"]["USD"]["price"], 2)


        # --- Güncelleme zamanı (GMT+3) ---
        turkiye_saati = datetime.now(timezone.utc) + timedelta(hours=3)
        simdi = turkiye_saati.strftime("%d-%m-%Y %H:%M:%S")

        # --- HTML ---
        html = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Memooooooo</title>
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
                            <img src="https://i.imgur.com/FQCD10d.png" alt="Dolar" class="icon">
                            <h1 class="price mb-0">{dolar_fiyat} ₺</h1>
                        </div>
                    </div>
                </div>

                <div class="card shadow-lg rounded-4 mb-4">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <img src="https://i.imgur.com/6bqao1V.png" alt="Ada" class="icon">
                            <h1 class="price mb-0">{ada_fiyat} $</h1>
                        </div>
                    </div>
                </div>

                <div class="card shadow-lg rounded-4 mb-4">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <img src="https://i.imgur.com/awXKORw.png" alt="Sol" class="icon">
                            <h1 class="price mb-0">{sol_fiyat} $</h1>
                        </div>
                    </div>
                </div>

                <div class="card shadow-lg rounded-4 mb-4">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <img src="https://i.imgur.com/yiGgpo4.png" alt="Xrp" class="icon">
                            <h1 class="price mb-0">{xrp_fiyat} $</h1>
                        </div>
                    </div>
                </div>

                <p class="text-muted mt-3">Güncelleme Zamanı: {simdi}</p>
            </div>
        </body>
        </html>
        """


        # HTML dosyası oluştur
        local_filename = "index.html"
        remote_filename = "/mehmetmutlu.online/htdocs/index.html"

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
