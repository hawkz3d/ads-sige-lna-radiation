import sqlite3, zlib, re

db = sqlite3.connect(r'<ADS_INSTALL>\doc\ads.qch')

for name in ['ael/de_find_pin().html', 'ael/de_break_connection().html',
             'ael/db_get_inst_pin_snap_point().html', 'ael/db_create_inst_pin_iter().html']:
    row = db.execute("SELECT Data FROM FileDataTable WHERE Id IN (SELECT FileId FROM FileNameTable WHERE Name=?)", (name,)).fetchone()
    if row and row[0]:
        data = row[0]
        try:
            decompressed = zlib.decompress(data[4:]).decode('utf-8', errors='ignore')
        except:
            decompressed = data.decode('utf-8', errors='ignore')
        text = re.sub(r'<[^>]+>', ' ', decompressed)
        text = re.sub(r'\s+', ' ', text)
        print(f'\n===== {name.split("/")[1].replace(".html","")} =====')
        print(text[:3000])
    else:
        print(f'{name} NOT FOUND')
