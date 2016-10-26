# -*- coding: utf-8 -*-
import logging

class Seller(object):
    @classmethod
    def add_seller(cls, db, name, password, store_id, number=None, checked=1):
        sql = "INSERT INTO seller(name, password, number, store_id, email_checked) VALUES(%s, %s, %s, %s, %s)"
        r = db.execute(sql, (name, password, number, store_id, checked))
        seller_id = r.lastrowid
        return seller_id

    @classmethod
    def delete_seller(cls, db, store_id, seller_id):
        sql = "DELETE FROM seller WHERE id=%s"
        r = db.execute(sql, seller_id)
        logging.debug("delete seller rows:%s", r.rowcount)

    @classmethod
    def set_seller_name(cls, db, store_id, seller_id, name):
        sql = "UPDATE seller SET name=%s WHERE id=%s"
        r = db.execute(sql, (name, seller_id))
        return r.rowcount

    @classmethod
    def set_seller_password(cls, db, store_id, seller_id, password):
        sql = "UPDATE seller SET password=%s WHERE id=%s"
        r = db.execute(sql, (password, seller_id))
        return r.rowcount

    @classmethod
    def get_sellers(cls, db, store_id):
        sql = "SELECT id, name, number FROM seller WHERE store_id=%s"
        r = db.execute(sql, store_id)
        return list(r.fetchall())

    @classmethod
    def get_seller_count(cls, db, store_id):
        sql = "SELECT count(*) as count FROM seller WHERE store_id=%s"
        r = db.execute(sql, store_id)
        obj = r.fetchone()
        return obj['count']

    @classmethod
    def get_page_seller(cls, db, store_id, offset, limit):
        sql = "SELECT id, name, number FROM seller WHERE store_id=%s LIMIT %s, %s"
        r = db.execute(sql, (store_id, offset, limit))
        return list(r.fetchall())
        
