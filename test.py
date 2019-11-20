from bsddb3 import db

mydb = db.DB()
mydb.open("idx/da.idx", None, db.DB_BTREE, db.DB_RDONLY)
cursor = mydb.cursor()
result = cursor.set_range("2000/10/01".encode("utf-8"))
while (result != None):
    print(result)
    result = cursor.prev()
mydb.close()
