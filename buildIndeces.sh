#!/bin/bash

DIR="./idx/"

rm -r ${DIR}

if ! [ -f ${DIR} ]; then
	mkdir ${DIR}
fi

# sort the files, use db_load to create the index
if [ -f "terms.txt" ]; then
	sort terms.txt -u -o terms.txt
	cat terms.txt | ./break.pl | db_load -T -t btree ${DIR}te.idx
fi

if [ -f "recs.txt" ]; then
	sort recs.txt -u -n -o recs.txt
	cat recs.txt | ./break.pl | db_load -c duplicates=1 -T -t hash ${DIR}re.idx
fi

if [ -f "emails.txt" ]; then
	sort emails.txt -u -o emails.txt
	cat emails.txt | ./break.pl | db_load -c duplicates=1 -T -t btree ${DIR}em.idx
fi

if [ -f "dates.txt" ]; then
	sort dates.txt -u -o dates.txt
	cat dates.txt | ./break.pl | db_load -c duplicates=1 -T -t btree ${DIR}da.idx
fi
