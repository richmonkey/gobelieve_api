# -*- coding: utf-8 -*-
import logging

class Group(object):
    @staticmethod
    def create_group(db, appid, master, name, is_super, members):
        db.begin()
        sql = "INSERT INTO `group`(appid, master, name, super) VALUES(%s, %s, %s, %s)"

        s = 1 if is_super else 0
        r = db.execute(sql, (appid, master, name, s))
        group_id = r.lastrowid
        
        for m in members:
            sql = "INSERT INTO group_member(group_id, uid) VALUES(%s, %s)"
            db.execute(sql, (group_id, m))
        
        db.commit()
        return group_id

    @staticmethod
    def update_group_name(db, group_id, name):
        sql = "UPDATE `group` SET name=%s WHERE id=%s"
        r = db.execute(sql, (name, group_id))
        logging.debug("update group rows:%s", r.rowcount)

    @staticmethod
    def disband_group(db, group_id):
        db.begin()
        sql = "DELETE FROM `group` WHERE id=%s"
        r = db.execute(sql, group_id)
        logging.debug("rows:%s", r.rowcount)

        sql = "DELETE FROM group_member WHERE group_id=%s"
        r = db.execute(sql, group_id)
        logging.debug("delete group rows:%s", r.rowcount)
        db.commit()

    @staticmethod
    def add_group_member(db, group_id, member_id):
        sql = "INSERT INTO group_member(group_id, uid) VALUES(%s, %s)"
        r = db.execute(sql, (group_id, member_id))
        logging.debug("insert rows:%s", r.rowcount)

    @staticmethod
    def delete_group_member(db, group_id, member_id):
        sql = "DELETE FROM group_member WHERE group_id=%s AND uid=%s"
        r = db.execute(sql, (group_id, member_id))
        logging.debug("delete group member rows:%s", r.rowcount)

    @staticmethod
    def get_group_members(db, group_id):
        sql = "SELECT uid FROM group_member WHERE group_id=%s"
        r = db.execute(sql, group_id)
        return list(r.fetchall())
        
    @staticmethod
    def get_group_master(db, group_id):
        sql = "SELECT master FROM `group` WHERE id=%s"
        cursor = db.execute(sql, group_id)
        r = cursor.fetchone()
        master = r["master"]
        return master

    @staticmethod
    def get_group(db, group_id):
        sql = "SELECT id, appid, master, super, name FROM `group` WHERE id=%s"
        cursor = db.execute(sql, group_id)
        r = cursor.fetchone()
        return r
        

    #获取用户所在的所有群
    @staticmethod
    def get_groups(db, appid, uid):
        sql = "SELECT g.id, g.appid, g.master, g.super, g.name FROM `group_member`, `group` as g WHERE group_member.uid=%s AND group_member.group_id=g.id AND g.appid=%s"

        cursor = db.execute(sql, (uid, appid))
        return list(cursor.fetchall())
