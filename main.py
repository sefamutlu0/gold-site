from flask import Flask, request, render_template
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

        # --- Kripto verisi ---
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

        # --- HTML oluştur ---
        html = render_template("index.html",
                               altin_fiyat=altin_fiyat,
                               dolar_fiyat=dolar_fiyat,
                               sol_fiyat=sol_fiyat,
                               ada_fiyat=ada_fiyat,
                               xrp_fiyat=xrp_fiyat,
                               simdi=simdi)

        # HTML dosyasını kaydet
        local_filename = "index.html"
        remote_filename = "/htdocs/index.html"

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
