import requests
from flask import Flask, Response, request

app = Flask(__name__)

# Yerelde çalışan Gradio uygulamasının hedef adresi (7860 portu)
TARGET_SERVER = "http://127.0.0.1:7860"


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def reverse_proxy(path):
  # Yerel hedef URL
  url = f"{TARGET_SERVER}/{path}"

  # Hop-by-hop header'ları filtrele
  excluded_headers = [
      "content-length",
      "transfer-encoding",
      "connection",
      "host",
  ]
  headers = {
      key: value
      for key, value in request.headers.items()
      if key.lower() not in excluded_headers
  }

  # Alan adı ve host yönlendirme ayarları
  headers["Host"] = "127.0.0.1:7860"
  headers["X-Forwarded-Host"] = "megagigawhat.com"
  headers["X-Forwarded-For"] = request.remote_addr
  headers["X-Forwarded-Proto"] = request.scheme

  try:
    # İsteği yerel Gradio servisine ilet
    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        params=request.args,
        allow_redirects=False,
    )

    # Yanıt header'larını düzenle
    response_headers = [
        (name, value)
        for name, value in resp.raw.headers.items()
        if name.lower() not in ["content-encoding", "transfer-encoding", "connection"]
    ]

    return Response(resp.content, resp.status_code, response_headers)

  except requests.exceptions.RequestException as e:
    return f"Reverse Proxy Hatası: Yerel hedef servise ulaşılamadı. ({e})", 502


if __name__ == "__main__":
  # Eğer doğrudan http://megagigawhat.com şeklinde (port yazmadan) girmek istiyorsan portu 80 yapabilirsin.
  # Standart kullanım için 8080 veya 8880 portunda çalıştırabilirsin.
  app.run(host="0.0.0.0", port=8080, debug=True)