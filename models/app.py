
class App(object):
    @classmethod
    def get_store_id(cls, db, appid):
        sql = "SELECT store_id FROM app WHERE app.id=%s"
        r = db.execute(sql, appid)
        app = r.fetchone()
        if app and "store_id" in app:
            return app["store_id"]
        else:
            return 0
