import sqlite3

conn = sqlite3.connect('emlak.db')
conn.execute("PRAGMA foreign_keys = ON")

print ("Opened database successfully")
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS Rol (
                    _id INTEGER PRIMARY KEY ,
                    ad TEXT NOT NULL UNIQUE);''')
conn.commit()
cur.execute('''CREATE TABLE IF NOT EXISTS Kisi (
                   _id INTEGER PRIMARY KEY ,
                    rol_id INTEGER,
                    ad TEXT NOT NULL,
                    soyad TEXT NOT NULL,
                    telefon TEXT NOT NULL UNIQUE,
                    kimlikler TEXT,
                    'not' TEXT,
                    adres TEXT,
                    mail_adres TEXT,
                    FOREIGN KEY (rol_id) REFERENCES Rol(_id));''')
conn.commit()
cur.execute('''CREATE TABLE IF NOT EXISTS Ev (
                    _id INTEGER PRIMARY KEY,
                    ev_sahibi_id INTEGER,
                    adres TEXT NOT NULL UNIQUE,
                    belge TEXT,
                    dolu INTEGER NOT NULL,
                    'not' TEXT,
                    FOREIGN KEY (ev_sahibi_id) REFERENCES Kisi (_id) ON DELETE CASCADE);''')
conn.commit()
cur.execute('''CREATE TABLE IF NOT EXISTS Kiralama (
                    _id INTEGER PRIMARY KEY,
                    kiraci_id INTEGER,
                    ev_id INTEGER,
                    kontrat_tarihi TEXT NOT NULL,
                    cikis_tarihi TEXT,
                    depozito INTEGER NOT NULL,
                    kontrat_no INTEGER NOT NULL,
                    'not' TEXT,
                    FOREIGN KEY (kiraci_id) REFERENCES Kisi (_id) ON DELETE CASCADE,
                    FOREIGN KEY (ev_id) REFERENCES Ev (_id) ON DELETE CASCADE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Fiyat_Tarih (
                    _id INTEGER PRIMARY KEY,
                    kiralama_id INTEGER,
                    guncelleme_tarihi TEXT NOT NULL,
                    fiyat INTEGER,
                    FOREIGN KEY (kiralama_id) REFERENCES Kiralama (_id) ON DELETE CASCADE)''')
sql = ''' INSERT INTO Rol(ad)
              VALUES('kiraci') '''
cur.execute(sql)
sql = ''' INSERT INTO Rol(ad)
              VALUES('ev_sahibi') '''
cur.execute(sql)
conn.commit()
conn.close()
print("Database closed successfully.")
