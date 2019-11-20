from bsddb3 import db

mydb = db.DB()
mydb.open("idx/da.idx", None, db.DB_BTREE, db.DB_RDONLY)
print(mydb.get(b'2000/09/22',0) )