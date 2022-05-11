import sqlite3
from sqlite3 import Error
from datetime import date


def create_connection(db_file):
    """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
    except Error as e:
        print(e)

    return conn


database = "emlak.db"
# create a database connection
conn = create_connection(database)


def write_query():
    cur = conn.cursor()
    sql = '''SELECT kiralama_id, MAX(guncelleme_tarihi) , fiyat
    FROM Fiyat_Tarih
    GROUP BY kiralama_id
'''
    cur.execute(sql)
    conn.commit()
    print("done")
    return cur.fetchall()


def execute_query(sql, object):
    try:
        cur = conn.cursor()
        cur.execute(sql, object)
        conn.commit()
        cur.close()
        return 200
    except sqlite3.Error as er:
        print(er)
        return er


def execute_get_query(sql):
    cur = conn.cursor()
    cur.execute(sql)
    test = cur.fetchall()
    return test


def execute_and_get_query_by_parameter(sql, object):
    cur = conn.cursor()
    print(object)
    cur.execute(sql, object)
    test = cur.fetchall()
    return test


def create_kisi(kisi):
    """
    Create a new kisi into the Kisi table
    :param kisi:
    :return: kisi id
    """
    sql = ''' INSERT INTO Kisi(rol_id,ad,soyad,telefon,mail_adres,adres,'not')
              VALUES(?,?,?,?,?,?,?) '''
    print(kisi)
    return execute_query(sql, kisi)


def get_kisiler_by_rol_id(rol_id):
    sql = '''SELECT K._id,K.ad,K.soyad,K.telefon from Kisi K where rol_id = ?'''
    return execute_and_get_query_by_parameter(sql, (rol_id,))


def get_kisiler_column_names():
    return ["Ad Soyad", "Telefon"]


# returns kisi_id, kisi_ad, kisi_soyad, kisi_telefon, kiralama_id
def get_kiracilar_by_ev_id(ev_id):
    sql = '''SELECT K._id,K.ad,K.soyad,K1._id, IFNULL(K1.cikis_tarihi, 'ÇIKIŞ YAPILMADI'),K1.kontrat_no FROM Kisi K INNER JOIN Kiralama K1 ON K1.kiraci_id=k._id WHERE K1.ev_id = ?'''
    return execute_and_get_query_by_parameter(sql, (ev_id,))

# returns kisi_id, kisi_rol_id, kisi_ad, kisi_soyad, kisi_telefon
def get_kisi_by_id(_id):
    sql = '''SELECT * from Kisi K where _id = ? '''
    return execute_and_get_query_by_parameter(sql, (_id,))[0]


def get_bos_kiracilar():
    sql = '''SELECT _id,ad,soyad FROM Kisi WHERE rol_id=1 and _id NOT IN (
SELECT kiraci_id FROM Kiralama WHERE cikis_tarihi IS NULL
)'''
    return execute_get_query(sql)


def update_kisi(kisi):
    sql = ''' UPDATE Kisi SET 
                ad = ? ,
                soyad = ?,
                telefon = ?,
                mail_adres = ?,
                adres = ?,
                'not' = ?
               WHERE _id = ?'''
    return execute_query(sql, kisi)


def delete_kisi(kisi_id):
    """
    delete a kisi
    :param kisi_id:
    :return:
    """
    sql = ''' DELETE from Kisi where _id = ? '''
    return execute_query(sql, (kisi_id,))


def create_ev(ev):
    """
    Create a new ev
    :param ev:
    :return: ev id
    """

    sql = ''' INSERT INTO Ev(ev_sahibi_id,adres,dolu,'not')
              VALUES(?,?,0,?) '''
    return execute_query(sql, ev)


# returns ev_id,ev_adres,ev_sahibi_id,ev_sahibi_name,ev_sahibi_surname,ev_sahibi_telefon
def get_bos_evler():
    sql = '''SELECT E._id,E.adres,K._id,K.ad,K.soyad,K.telefon from Ev E 
    INNER JOIN Kisi K ON E.ev_sahibi_id=K._id WHERE dolu = 0'''
    return execute_get_query(sql)


# returns a list of ev_id , ev_adres, ev_sahibi_id, ev_sahibi_ad, ev_sahibi_soyad, ev_sahibi_telefon,
# Kiralama.kontrat_tarihi,Kiralama.güncelleme_tarihi,Kiralama.kontrat_no,
# ev_adres, kiraci_id, kiraci_ad, kiraci_soyad, kiraci_telefon,

def get_dolu_evler():
    sql = '''SELECT E._id,E.adres,
    Ev_Sahibi._id,Ev_Sahibi.ad,Ev_Sahibi.soyad,Ev_Sahibi.telefon,
    Kiraci._id,Kiraci.ad,Kiraci.soyad,Kiraci.telefon,
    K.kontrat_tarihi,F.fiyat,K.kontrat_no 
    from Ev E 
    INNER JOIN Kisi Ev_Sahibi ON E.ev_sahibi_id=Ev_Sahibi._id 
    INNER JOIN Kiralama K ON E._id=K.ev_id
    INNER JOIN Kisi Kiraci ON K.kiraci_id=Kiraci._id 
    INNER JOIN Fiyat_Tarih F ON K._id=F.kiralama_id 
    WHERE E.dolu=1 AND K.cikis_tarihi IS NULL AND F._id IN
    (SELECT F._id
    FROM Fiyat_Tarih F
    INNER JOIN (
    SELECT kiralama_id, MAX(guncelleme_tarihi) as date
    FROM Fiyat_Tarih
    GROUP BY kiralama_id
    ) F1
    ON F.kiralama_id = F1.kiralama_id AND F.guncelleme_tarihi = F1.date)
    '''
    return execute_get_query(sql)


def get_evler_column_names():
    return ["adres", "kiraci adi", "kiraci telefonu"]


def get_bos_ev_by_id(ev_id):
    sql = '''SELECT E._id, E.adres, K.ad, K.soyad, K.telefon, K._id, E.'not' from Ev E INNER JOIN Kisi K ON E.ev_sahibi_id=K._id where E._id=?'''
    return execute_and_get_query_by_parameter(sql, (ev_id,))[0]


def get_dolu_ev_by_id(ev_id):
    print(ev_id)
    sql = '''SELECT E._id,  E.adres, 
    Ev_Sahibi.ad, Ev_Sahibi.soyad, Ev_Sahibi.telefon, 
    Kiraci.ad, Kiraci.soyad, Kiraci.telefon, 
    K.kontrat_tarihi, F2.fiyat as kontrat_fiyat, MAX(F.guncelleme_tarihi) as guncelleme_tarihi, 
    F.fiyat as guncel_fiyat, K.depozito, K.kontrat_no, 
    E.'not', K.'not', K._id
    from Ev E 
    INNER JOIN Kisi Ev_Sahibi ON E.ev_sahibi_id=Ev_Sahibi._id 
    INNER JOIN Kiralama K ON E._id=K.ev_id
    INNER JOIN Kisi Kiraci ON K.kiraci_id=Kiraci._id
    INNER JOIN Fiyat_Tarih F ON F.kiralama_id=K._id   
    INNER JOIN Fiyat_Tarih F2 ON F2.kiralama_id=K._id   
    WHERE E._id=? AND F2.guncelleme_tarihi=K.kontrat_tarihi AND K.cikis_tarihi IS NULL'''
    return execute_and_get_query_by_parameter(sql, (ev_id,))[0]

def get_ev_id_adres_by_id(ev_id):
    sql = '''SELECT _id, adres FROM Ev where _id = ?'''
    print(ev_id)
    return execute_and_get_query_by_parameter(sql, (ev_id,))[0]

def get_detay_by_kiralama_id(kiralama_id):
    sql = '''SELECT guncelleme_tarihi,fiyat,_id from Fiyat_Tarih WHERE kiralama_id=? order by date(guncelleme_tarihi) desc'''
    return execute_and_get_query_by_parameter(sql, (kiralama_id,))


def update_ev(ev):
    sql = ''' UPDATE Ev SET 
                'not' = ?,
                'adres' = ? 
               WHERE _id = ?'''
    return execute_query(sql, ev)


def evi_bosalt(ev_id, cikis_tarihi):
    sql = '''UPDATE Kiralama SET cikis_tarihi=? WHERE ev_id=?;'''
    execute_query(sql, (cikis_tarihi, ev_id))
    sql = ''' UPDATE Ev SET 
                dolu = 0 
               WHERE _id = ?'''
    return execute_query(sql, (ev_id,))


def delete_ev(ev_id):
    """
    delete an ev
    :param ev_id:
    :return:
    """

    sql = ''' DELETE from Ev where _id = ? '''
    return execute_query(sql, (ev_id,))


def create_kiralama(kiralama, fiyat):
    """
    Create a new kiralama into the Kiralama table
    :param conn:
    :param kiralama:
    :return: kiralama id
    """
    try:
        sql = ''' INSERT INTO Kiralama(kiraci_id,ev_id,kontrat_tarihi,depozito,'not',kontrat_no)
                  VALUES(?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, kiralama)
        kiralama_id = cur.lastrowid
        kontrat_tarihi = kiralama[2]
        sql = ''' INSERT INTO Fiyat_Tarih(kiralama_id,guncelleme_tarihi,fiyat)
                  VALUES(?,?,?) '''
        cur.execute(sql, (kiralama_id, kontrat_tarihi, fiyat))
        sql = ''' UPDATE Ev SET 
                    dolu = 1 
                   WHERE _id = ?'''
        cur.execute(sql, (kiralama[1],))
        conn.commit()
        return 200
    except sqlite3.Error as er:
        return er


# return kiralama_id, kiraci_id, ev_id, kontrat, cikis, fiyat, depozito, kiraci_ad, kiraci_soyad, ev_adres, ev_sahibi_ad, ev_sahibi_soyad, ev_sahibi_id, kontrat_tarihi
def get_kiralama_by_id(kiralama_id):
    sql = '''SELECT K.*,
    Kiraci.ad,Kiraci.soyad,
    E.adres,
    Ev_Sahibi.ad,Ev_Sahibi.soyad,Ev_Sahibi._id
    FROM Kiralama K 
    INNER JOIN Kisi Kiraci ON K.kiraci_id=Kiraci._id
    INNER JOIN Ev E ON K.ev_id=E._id
    INNER JOIN Kisi Ev_Sahibi ON E.ev_sahibi_id=Ev_Sahibi._id
    WHERE K._id = ?
    '''
    return execute_and_get_query_by_parameter(sql, (kiralama_id,))


# return kiralama_id, kiraci_id, ev_id, kontrat, cikis, fiyat, depozito, kiraci_ad, kiraci_soyad, ev_adres, ev_sahibi_ad, ev_sahibi_soyad, ev_sahibi_id
def get_fiyati_artacak_evler():
    sql = '''SELECT E._id,E.adres,
    Ev_Sahibi._id,Ev_Sahibi.ad,Ev_Sahibi.soyad,Ev_Sahibi.telefon,
    Kiraci._id,Kiraci.ad,Kiraci.soyad,Kiraci.telefon,
    F.guncelleme_tarihi,F.fiyat,K.kontrat_no 
    from Ev E 
    INNER JOIN Kisi Ev_Sahibi ON E.ev_sahibi_id=Ev_Sahibi._id 
    INNER JOIN Kiralama K ON E._id=K.ev_id
    INNER JOIN Kisi Kiraci ON K.kiraci_id=Kiraci._id 
    INNER JOIN Fiyat_Tarih F ON K._id=F.kiralama_id 
    WHERE E.dolu=1 AND K.cikis_tarihi IS NULL AND F._id IN
    (SELECT F._id
    FROM Fiyat_Tarih F
    INNER JOIN (
    SELECT kiralama_id, MAX(guncelleme_tarihi) as date
    FROM Fiyat_Tarih
    GROUP BY kiralama_id
    HAVING julianday('now') - julianday(guncelleme_tarihi) > 335
    ) F1
    ON F.kiralama_id = F1.kiralama_id AND F.guncelleme_tarihi = F1.date)
    '''

    return execute_get_query(sql)


def update_kiralama(kiralama):
    sql = ''' UPDATE Kiralama SET 
                'not' = ?,
                'kontrat_tarihi' = ?,
                'depozito' = ?,
                'kontrat_no' = ?
               WHERE _id = ?'''
    return execute_query(sql, kiralama)


def update_fiyat_tarih(fiyat_tarih):
    sql = ''' UPDATE Fiyat_Tarih SET 
                'fiyat' = ?,
                'guncelleme_tarihi' = ?
                 WHERE 
                    kiralama_id = ? and 
                    guncelleme_tarihi = ?'''
    return execute_query(sql, fiyat_tarih)


def get_kontrat_tarihi_by_kiralama_id(kiralama_id):
    sql = ''' SELECT kontrat_tarihi from Kiralama where _id = ? '''
    return execute_and_get_query_by_parameter(sql, (kiralama_id,))


def delete_kiralama(kiralama_id):
    """
    delete a kiralama
    :param kiralama_id:
    :return:
    """

    sql = ''' DELETE from Kiralama where _id = ? '''
    return execute_query(sql, (kiralama_id,))


def create_fiyat_tarih(kiralama_id, guncelleme_tarihi, fiyat):
    sql = ''' INSERT INTO Fiyat_Tarih(kiralama_id,guncelleme_tarihi,fiyat)
              VALUES(?,?,?) '''
    return execute_query(sql, (kiralama_id, guncelleme_tarihi, fiyat))


def get_tarih_by_fiyat_tarih_id(fiyat_tarih_id):
    sql = '''SELECT guncelleme_tarihi FROM Fiyat_Tarih WHERE _id = ?'''
    return execute_and_get_query_by_parameter(sql, (fiyat_tarih_id,))


def delete_tarih_fiyat(tarih_fiyat_id):
    """
    delete a tarih_fiyat
    :param tarih_fiyat_id:
    :return:
    """

    sql = ''' DELETE from Fiyat_Tarih where _id = ? '''
    return execute_query(sql, (tarih_fiyat_id,))


def create_test():
    # create a new kiraci
    kiraci = (1, 'ad_3', 'soyad_3', '11134', 'path/to/kimlik');
    kiraci_id = create_kisi(kiraci)
    # create a new ev sahibi
    ev_sahibi = (1, 'ad_4', 'soyad_4', '113456', 'path/to/kimlik');
    ev_sahibi_id = create_kisi(ev_sahibi)

    # create a new ev
    ev = (ev_sahibi_id, 'kubilay 19-11', "path/to/belge", 0)
    ev_id = create_ev(ev)
    ev1 = (ev_sahibi_id, 'kubilay 19-11', "path/to/belge1", 0)
    create_ev(ev1)

    # create a new kiralama
    kiralama = (kiraci_id, ev_id, str(date.today()), None, 900, 1300)
    create_kiralama(kiralama)
    print("created for test successfully")


def delete_test():
    delete_ev(1)
    print("deleted for test successfully")


def get_test():
    print("Kiracilar:", get_kisiler_by_rol_id(1))
    print("Ev Sahipleri:", get_kisiler_by_rol_id(1))
    print("Kiralamalar:", get_dolu_evler())
    print("Kiralama:", get_kiralama_by_id(1))
    print("Fiyati artacak evler:", get_fiyati_artacak_evler())
    print("1 id'li evin kiracilari", get_kiracilar_by_ev_id(1))


def bosalt_test():
    evi_bosalt(1)


def update_test():
    # update_kiralama((1,1,'1010-01-09',None,900,1100,1))
    print(update_kisi(("ad", "soyad", "81", 3,)))


def add_kiraci_test():
    records = [(1, '1', 'Glen', '81', 'kimlik'),
               (1, '1', 0, '91', 'kimlik'),
               (1, '1', 0, '91', 'kimlik'),
               (1, '1', 0, '93', 'kimlik'),
               (1, '1', 0, '94', 'kimlik'),
               (1, '1', 0, '96', 'kimlik'),
               (1, '1', 0, '946', 'kimlik'),
               (1, '1', 0, '947', 'kimlik'),
               (1, '1', 0, '948', 'kimlik'),
               (1, '1', 0, '949', 'kimlik'),
               (1, '1', 0, '941', 'kimlik'),
               (1, '3', 'Bob', '71', 'kimlik')]

    # insert multiple records in a single query
    c = conn.cursor()
    c.executemany('INSERT INTO Kisi(rol_id,ad,soyad,telefon,kimlikler) VALUES(?,?,?,?,?);', records);

    print('We have inserted', c.rowcount, 'records to the table.')

    # commit the changes to db
    conn.commit()
    # close the connection
    conn.close()


def add_ev_test():
    records = [(1, 'kubilay 0/11', 1),
               (1, 'kubilay 19/11', 0),
               (12, 'kubilay 19/31', 0),
               (1, 'kubilay 19/41', 0),
               (1, 'kubilay 19/51', 0),
               (1, 'kubilay 19/61', 0),
               (1, 'kubilay 19/71', 0),
               (1, 'kubilay 19/81', 0),
               (1, 'kubilay 19/91', 0),
               (1, 'kubilay 19/14', 1),
               (1, 'kubilay 19/13', 0)
               ]

    # insert multiple records in a single query
    c = conn.cursor()
    c.executemany('INSERT INTO Ev(ev_sahibi_id,adres,dolu) VALUES(?,?,?);', records);

    print('We have inserted', c.rowcount, 'records to the table.')

    # commit the changes to db
    conn.commit()
    # close the connection
    conn.close()


if __name__ == '__main__':
    # create_test()
    # add_kiraci_test()
    # add_ev_test()
    # get_test()
    print(write_query())
    # delete_test()
    # bosalt_test()
    # update_test()
