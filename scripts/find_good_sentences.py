#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import ConfigParser, MySQLdb
from MySQLdb.cursors import DictCursor 

PACKET_SIZE = 1000
ADD_THRESHOLD = 0.3

def find_sentences(dbh):
    dbh.execute("SELECT MAX(sent_id) AS sent_max FROM sentences")
    sent_max = dbh.fetchone()['sent_max']
    i = 0
    while i <= sent_max:
        find_sentences_next(dbh, i)
        i += PACKET_SIZE

def find_sentences_next(dbh, start):
    dbh.execute("""SELECT sent_id, rev_text FROM tf_revisions LEFT JOIN text_forms USING(tf_id) LEFT JOIN sentences USING(sent_id) WHERE sent_id >= {0} AND sent_id < {1} AND is_last = 1 AND rev_text NOT LIKE '%"UNKN"%' AND rev_text NOT LIKE '%"PNCT"%' ORDER BY sent_id""".format(start, start + PACKET_SIZE))
    
    last_sent_id = 0
    count_total = 0
    count_hom = 0
    
    words = dbh.fetchall()
    for word in words:
        if last_sent_id > 0 and word['sent_id'] != last_sent_id:
            add_sentence(dbh,last_sent_id, count_total, count_hom)
            count_hom = 0
            count_total = 0

        if is_homonymous(word['rev_text']):
            count_hom += 1
        count_total += 1
        last_sent_id = word['sent_id']

    if count_total > 0:
        add_sentence(dbh, last_sent_id, count_total, count_hom)
def add_sentence(dbh, sent_id, total, hom):
    if float(hom) / total <= ADD_THRESHOLD:
        dbh.execute("INSERT INTO good_sentences VALUES({0}, {1}, {2})".format(sent_id, total, hom))
def is_homonymous(revision):
    var = re.findall('<v>', revision)
    return len(var) > 1
def main():
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])

    hostname = config.get('mysql', 'host')
    dbname   = config.get('mysql', 'dbname')
    username = config.get('mysql', 'user')
    password = config.get('mysql', 'passwd')

    db = MySQLdb.connect(hostname, username, password, dbname, use_unicode=True, charset="utf8")
    dbh = db.cursor(DictCursor)
    dbh.execute('START TRANSACTION')
    dbh.execute('TRUNCATE TABLE good_sentences')
    find_sentences(dbh)

    db.commit()

if __name__ == "__main__":
    main()