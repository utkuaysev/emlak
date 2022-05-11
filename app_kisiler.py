from flask import render_template, request

from app import app
from db_connector import get_kisiler_column_names, get_kisiler_by_rol_id, update_kisi, delete_kisi, create_kisi, \
    get_kiracilar_by_ev_id, get_kisi_by_id


@app.route('/', methods=['GET'])
def api_hello_world():
    return render_template("anasayfa.html")


@app.route('/kisiler_anasayfa', methods=['GET'])
def web_kisiler_anasayfa():
    return render_template("kisiler_anasayfa.html")


@app.route('/create_kisi', methods=['GET'])
def web_create_kisi():
    rol_id = int(request.args.get("rol_id"))
    if rol_id == 1:
        tip_for_header = "Kiraci"
    else:
        tip_for_header = "Ev Sahibi"
    return render_template("kisi_ekle.html", rol_id = rol_id, tip_for_header = tip_for_header )

def get_tip_for_header_by_rol_id(rol_id):
    if rol_id == 1:
        return "Kiracılar"
    return "Ev Sahipleri"

def get_tip_by_rol_id(rol_id):
    if rol_id == 1:
        return "Kiracı"
    return "Ev Sahibi"


def get_rol_specific_info(rol_id):
    print(rol_id)
    if rol_id == 1:
        return ("Kiralanan Evler","/kiralanan_evler?_id")
    return ("Ev Sahibi Olunan Evler","/evler_by_id?_id")


def get_kisiler_page(rol_id,success_message):
        return render_template("kisiler.html",
                    column_names=get_kisiler_column_names(),
                    kisiler=get_kisiler_by_rol_id(rol_id),
                    view_url = "/kisi?_id=",
                    tip_for_header = get_tip_for_header_by_rol_id(rol_id),
                    tip = get_tip_by_rol_id(rol_id),
                    success_message = success_message,
                    rol_id = rol_id)

@app.route('/kisiler', methods = ['GET', 'POST'])
def web_kisiler():
    rol_id = int(request.args.get("rol_id"))
    if request.method == "GET":
        return get_kisiler_page(rol_id,"None")
    ad_soyad = request.form.get("ad") + " " + request.form.get("soyad")
    status_message = "Hata"
    if 'update' in request.form:
        status = update_kisi((request.form.get("ad"), request.form.get("soyad"),
                      request.form.get("telefon"), request.form.get("mail_adres"),
                              request.form.get("adres"), request.form.get("not"), request.form.get("_id")))
        if status == 200:
            status_message = ad_soyad + " başarıyla güncellendi."
        else:
            status_message = status
            return render_template("err.html",err = status_message)
    elif 'delete' in request.form:
        status = delete_kisi(request.form.get("_id"))
        if status == 200:
            status_message = ad_soyad + " başarıyla silindi."
        else:
            status_message = status
            return render_template("err.html",err = status_message)
    elif 'create' in request.form:
        status = create_kisi((request.args.get("rol_id"), request.form.get("ad"), request.form.get("soyad"),
                              request.form.get("telefon"),
                              request.form.get("mail_adres"), request.form.get("adres"),request.form.get("not")))
        if status == 200:
            status_message = ad_soyad + " başarıyla eklendi."
        else:
            status_message = status
            return render_template("err.html", err=status_message)
    return get_kisiler_page(rol_id,status_message)


@app.route('/kisi', methods=['GET', 'POST'])
def web_get_kisi_by_id():
    kisi = get_kisi_by_id(request.args.get("_id"))
    arr = kisi[3].split()
    is_birden_fazla_isim = len(arr) > 1
    if is_birden_fazla_isim:
        isimler = kisi[2]
        for i in range(0, len(arr) - 1):
            isimler += " " + arr[i]
        soyisim = arr[len(arr) - 1]
        kisi = (
            kisi[0],
            kisi[1],
            isimler,
            soyisim,
            kisi[4],
            kisi[5],
            kisi[6],
            kisi[7],
            kisi[8]
        )
    print(kisi[2])
    print(kisi[3])
    return render_template("kisi.html", kisi = kisi, rol_specific_info = get_rol_specific_info(kisi[1]) )

@app.route('/delete_kisi', methods=['GET', 'POST'])
def api_delete_kisi():
    delete_kisi(request.args.get("_id"))
    return "done"
