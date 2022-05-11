from datetime import datetime

from flask import render_template, request

from app import app
from db_connector import *


# returns kisi_id, kisi_ad, kisi_soyad, kiralama_id, kiralama_cikis_tarihi, kiralama_kontrat_no
@app.route('/kiralamalar', methods=['GET', 'POST'])
def api_get_kiralamalar():
    ev = get_ev_id_adres_by_id(request.args.get("ev_id"))
    if request.method == 'GET':
        kiralamalar = get_kiracilar_by_ev_id(request.args.get("ev_id"))
        print(kiralamalar)
        return render_template("kiralamalar.html", adres=ev[1], kiralamalar=kiralamalar)
    if request.method == 'POST':
        kiralama_id = request.form.get("kiralama_id")
        kiralama = get_kiralama_by_id(kiralama_id)
        if (kiralama[0][4] == None):
            return render_template("err.html", err="Güncel kiralama silinemez")
        status = delete_kiralama(kiralama_id)
        if status == 200:
            kiralamalar = get_kiracilar_by_ev_id(request.args.get("ev_id"))
            status_message = ev[1] + "için kiralamalar başarıyla güncellendi"
            return render_template("kiralamalar.html",
                                   adres=ev[1],
                                   kiralamalar=kiralamalar,
                                   success_message=status_message)
        else:
            status_message = status
            return render_template("err.html", err=status_message)
