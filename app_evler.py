from datetime import datetime

from flask import render_template, request

from app import app
from db_connector import create_ev, update_ev, evi_bosalt, delete_ev, create_kiralama, \
    get_kiralama_by_id, get_fiyati_artacak_evler, update_kiralama, delete_kiralama, \
    get_bos_evler, get_dolu_evler, get_bos_ev_by_id, get_dolu_ev_by_id, get_kisiler_by_rol_id, get_bos_kiracilar, \
    get_kisi_by_id, get_detay_by_kiralama_id, create_fiyat_tarih, delete_tarih_fiyat, get_tarih_by_fiyat_tarih_id, \
    get_kontrat_tarihi_by_kiralama_id, update_fiyat_tarih


def get_evler_column_names_by_dolu(dolu):
    if dolu == 0:
        return ["Adres", "Ev Sahibi", "Telefon"]
    elif dolu == 1:
        return ["Adres", "Ev Sahibi", " Ev Sahibi Telefon",
                "Kiracı", "Kiracı Telefon", "Kontrat Tarihi", " Güncel Fiyat", "Kontrat No"]
    return ["Adres", "Ev Sahibi", " Ev Sahibi Telefon",
            "Kiracı", "Kiracı Telefon", "Güncelleme Tarihi", " Fiyat", "Kontrat No"]


def get_view_url_by_dolu(dolu):
    if dolu == 0:
        return "/bos_ev?_id="
    return "/dolu_ev?_id="


def get_tip_for_header_by_dolu(dolu):
    if dolu == 0:
        return "Boş Evler"
    elif dolu == 1:
        return "Dolu Evler"
    return "Fiyatı Artacak Evler"


def get_tip_by_dolu(dolu):
    if dolu == 0:
        return "Boş Ev"
    return "Dolu Ev"


def get_page_name_by_dolu(dolu):
    if dolu == 0:
        return "bos_evler.html"
    return "dolu_evler.html"


def get_evler_by_dolu(dolu):
    if dolu == 0:
        return get_bos_evler()
    elif dolu == 1:
        return get_dolu_evler()
    return get_fiyati_artacak_evler()


@app.route('/evler_anasayfa', methods=['GET'])
def web_evler_anasayfa():
    return render_template("evler_anasayfa.html")


def get_evler_page(dolu, success_message):
    column_names = get_evler_column_names_by_dolu(dolu)
    view_url = get_view_url_by_dolu(dolu)
    tip_for_header = get_tip_for_header_by_dolu(dolu)
    page_name = get_page_name_by_dolu(dolu)
    evler = get_evler_by_dolu(dolu)
    tip = get_tip_by_dolu(dolu)
    return render_template(page_name,
                           column_names=column_names,
                           evler=evler,
                           view_url=view_url,
                           tip_for_header=tip_for_header,
                           success_message=success_message,
                           tip=tip
                           )


@app.route('/evler', methods=['GET', 'POST'])
def web_evler():
    dolu = int(request.args.get("dolu"))
    if request.method == "GET":
        return get_evler_page(dolu, "None")
    ev_sahibi_id = request.form.get("ev_sahibi_id")
    adres = request.form.get("adres")
    ev_id = request.form.get("ev_id")
    status_message = "Hata"
    if 'update' in request.form:
        not_ = request.form.get("ev_not")
        adres_ = request.form.get("adres")
        status_1 = update_ev((not_, adres_, ev_id))
        if dolu == 1:
            kiralama_id = request.form.get("kiralama_id")
            kontrat_tarihi_eski = get_kiralama_by_id(kiralama_id)[0][3]
            status_2 = update_kiralama(
                (
                    request.form.get("kiralama_not"),
                    request.form.get("kontrat"),
                    request.form.get("depozito"),
                    request.form.get("kontrat_no"),
                    kiralama_id
                )
            )
            status_3 = update_fiyat_tarih(
                (
                    request.form.get("kontrat_fiyat"),
                    request.form.get("kontrat"),
                    kiralama_id,
                    kontrat_tarihi_eski

                )
            )
            if status_1 == 200 and status_2 == 200 and status_3 == 200:
                status_message = adres + " başarıyla güncellendi."
            else:
                return render_template("err.html", err=" Notların güncellenmesinde sorun ortaya çıktı.Tekrar deneyin")
        if status_1 == 200:
            status_message = adres + " başarıyla güncellendi."
        else:
            return render_template("err.html", err="Güncellenmede sorun ortaya çıktı. "
                                                   "Bu adreste başka bir evin kayıtlı olup olmadığının kontrol "
                                                   "edilmesi gerekiyor.")
    elif 'delete' in request.form:
        status = delete_ev(ev_id)
        if status == 200:
            status_message = adres + " başarıyla silindi."
        else:
            status_message = status
            return render_template("err.html", err=status_message)
    elif 'create' in request.form:
        yeni_ev_not = request.form.get("yeni_ev_not")
        status = create_ev((ev_sahibi_id, adres, yeni_ev_not))
        if status == 200:
            status_message = adres + " başarıyla eklendi."
        else:
            status_message = status
            return render_template("err.html", err=status_message)
    elif 'cikar' in request.form:
        status = evi_bosalt(ev_id, datetime.today().strftime('%Y-%m-%d'))
        if status == 200:
            status_message = adres + " adresi için kiracı başarıyla çıkarıldı."
        else:
            status_message = status
            return render_template("err.html", err=status_message)
    return get_evler_page(dolu, status_message)


@app.route('/create_ev', methods=['GET'])
def api_create_ev():
    if request.method == 'GET':
        return render_template("ev_ekle.html", ev_sahipleri=get_kisiler_by_rol_id(2))


@app.route('/bos_ev', methods=['GET', 'POST'])
# returns ev_id,ev_sahibi_id,ev_adres,ev_belge,ev_sahibi_ad_ev_sahibi_soyad,ev_sahibi_telefon
def web_get_bos_ev_by_id():
    ev = get_bos_ev_by_id(request.args.get("_id"))
    ev_list = list(ev)
    if ev_list[6] == None: ev_list[6] = ""
    ev_updated = tuple(ev_list)
    print(ev[1])
    return render_template("bos_ev.html", ev=ev_updated, view_url="kisi?_id=")


# sql = '''SELECT E._id,E.adres,
#     Ev_Sahibi.ad,Ev_Sahibi.soyad,Ev_Sahibi.telefon,
#     Kiraci.ad,Kiraci.soyad,Kiraci.telefon,
#     K.kontrat_tarihi,F2.fiyat as kontrat_fiyat,MAX(F.guncelleme_tarihi) as guncelleme_tarihi,
#     F.fiyat as guncel_fiyat,K.depozito,K.kontrat_no,K._id
#     E.'not',K.'not'


@app.route('/dolu_ev', methods=['GET', 'POST'])
# returns ev_id,ev_adres,ev_sahibi_ad,ev_sahibi_soyad,ev_sahibi_telefon,kiraci_ad,kiraci_soyad,kiraci_telefon,kiralama_kontrat_tarihi,kontrat_fiyat,guncelleme_tarihi,kiralama_id
# guncel_fiyat,depozito,kontrat_no,ev_not,kiralama_not,kiralama_id.  18
def web_post_get_dolu_ev_by_id():
    if request.method == 'GET':
        ev = get_dolu_ev_by_id(request.args.get("_id"))
        print(ev)
        ev_list = list(ev)
        if ev_list[15] == None: ev_list[15] = ""
        if ev_list[16] == None: ev_list[16] = ""
        ev_updated = tuple(ev_list)
        print(ev_updated)
        return render_template("dolu_ev.html", ev=ev_updated, success_message='None')
    ev_id = request.args.get("_id")
    ev = get_bos_ev_by_id(ev_id)
    adres = ev[1]
    kiraci_id = request.form.get("kiraci_id")
    kiraci = get_kisi_by_id(kiraci_id)
    status = create_kiralama((kiraci_id, ev_id, request.form.get("kontrat_tarihi")
                              , request.form.get("depozito"),
                              request.form.get("not"),
                              request.form.get("kontrat_no")), request.form.get("kontrat_fiyati"))
    if status == 200:
        status_message = adres + " adresi için kiracı " + kiraci[2] + " " + kiraci[3] + " eklendi."
        return render_template("dolu_ev.html", ev=get_dolu_ev_by_id(ev_id), success_message=status_message)

    else:
        status_message = status
        return render_template("err.html", err=status_message)


def detay_ev(kiralama_id, adres):
    return render_template("detay.html", guncellemeler=get_detay_by_kiralama_id(kiralama_id), kiralama_id=kiralama_id,
                           adres=adres)


@app.route('/detay', methods=['GET', 'POST'])
def api_detay_ev():
    if request.method == 'GET':
        kiralama_id = request.args.get("kiralama_id")
        adres = request.args.get("adres")
        return detay_ev(kiralama_id, adres)
    kiralama_id = request.form.get("kiralama_id")
    adres = request.form.get("adres")
    if 'update' in request.form:
        guncelleme_tarihi = request.form.get("guncelleme_tarihi")
        yeni_fiyat = request.form.get("yeni_fiyat")
        status = create_fiyat_tarih(kiralama_id, guncelleme_tarihi, yeni_fiyat)
        status_message = adres + " adresi için yeni fiyat " + yeni_fiyat + " eklendi."
    else:
        fiyat_tarih_id = request.form.get("fiyat_tarih_id")
        deleted_tarih = get_tarih_by_fiyat_tarih_id(fiyat_tarih_id)
        kontrat_tarihi = get_kontrat_tarihi_by_kiralama_id(kiralama_id)
        print(kontrat_tarihi)
        print(deleted_tarih)
        if deleted_tarih != kontrat_tarihi:
            status = delete_tarih_fiyat(fiyat_tarih_id)
            status_message = "Fiyat bilgisi başarıyla silindi."
        else:
            status = "Kontrat tarihi silinemez"
    if status == 200:
        return detay_ev(kiralama_id, adres)
    else:
        status_message = status
        return render_template("err.html", err=status_message)


@app.route('/update_ev', methods=['GET', 'POST'])
def api_update_ev():
    update_ev((request.args.get("ev_sahibi_id"), request.args.get("adres"), request.args.get("belge"),
               request.args.get("dolu"), request.args.get("_id")))
    return "done"


@app.route('/evi_bosalt', methods=['GET', 'POST'])
def api_evi_bosalt():
    evi_bosalt(request.args.get("ev_id"), request.args.get("cikis_tarihi"))
    return "done"


@app.route('/delete_ev', methods=['GET', 'POST'])
def api_delete_ev():
    delete_ev(request.args.get("_id"))
    return "done"


@app.route('/kirala', methods=['GET'])
def api_create_kiralama():
    ev_id = request.args.get("ev_id")
    ev = get_bos_ev_by_id(ev_id)
    ev_adres = ev[1]
    ev_sahibi_adi = ev[2] + " " + ev[3]

    if request.method == 'GET':
        bos_kiracilar = get_bos_kiracilar()
        return render_template("kirala.html", bos_kiracilar=bos_kiracilar, ev_adresi=ev_adres,
                               ev_sahibi_adi=ev_sahibi_adi, ev_id=ev_id)


@app.route('/get_kiralama_by_id', methods=['GET', 'POST'])
def api_get_kiralama_by_id():
    return get_kiralama_by_id(request.args.get("_id"))


@app.route('/get_fiyati_artacak_evler', methods=['GET'])
def api_get_fiyati_artacak_evler():
    return get_fiyati_artacak_evler()


@app.route('/update_kiralama', methods=['GET', 'POST'])
def api_update_kiralama():
    update_kiralama((request.args.get("kiraci_id"),
                     request.args.get("ev_id"),
                     request.args.get("kontrat_tarihi"),
                     request.args.get("cikis_tarihi"),
                     request.args.get("fiyat"),
                     request.args.get("depozito"),
                     request.args.get("_id")))
    return "done"


@app.route('/delete_kiralama', methods=['GET', 'POST'])
def api_delete_kiralama():
    delete_kiralama(request.args.get("_id"))
    return "done"
