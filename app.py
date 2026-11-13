import gradio as gr
from trans import aktarim_suresi
from get_ip import kullanici_ip


def hesapla(veri, hiz):

    if veri is None or hiz is None:
        return "Please fill in all fields!"

    if veri <= 0 or hiz <= 0:
        return "values must be greater than zero"

    gun, saat, dakika, saniye = aktarim_suresi(veri, hiz)

    return f"{gun} gün {saat} saat {dakika} dakika {saniye} saniye"


with gr.Blocks(
    title="Veri Aktarım Hesaplayıcısı",
    fill_width=False
) as demo:

    gr.HTML(f"""
    <div style="
        position: fixed;
        top: 15px;
        right: 20px;
        z-index: 99999;
        background: #222;
        color: #00ff88;
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: bold;
    ">
        Local IP: {kullanici_ip()}
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=0, min_width=450):

            gr.Markdown("# Data Transfer Calculator")

            veri = gr.Number(label="Data amount (TB)")
            hiz = gr.Number(label="Internet speed (Mbit/s)")

            hesapla_btn = gr.Button("Calculate")

            sonuc = gr.Textbox(label="Transfer time")

            hesapla_btn.click(
                fn=hesapla,
                inputs=[veri, hiz],
                outputs=sonuc
            )


demo.launch(footer_links=[] , share =True)