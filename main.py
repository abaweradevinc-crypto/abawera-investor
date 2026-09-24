from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView

msg = ""

try:
    from database import init_db, Session, Stock
    msg += "1. import database OK\n"
    init_db()
    msg += "2. init_db OK\n"
    db = Session()
    stocks = db.query(Stock).all()
    msg += "3. query OK\n"
    msg += "4. stocks: " + str([s.symbol for s in stocks]) + "\n"
    db.close()
except Exception as e:
    import traceback
    msg += "ERROR:\n" + traceback.format_exc()


class TestApp(MDApp):
    def build(self):
        sv = ScrollView()
        lbl = MDLabel(
            text="TEST A - Database\n\n" + msg,
            size_hint_y=None, halign="left", valign="top",
            text_size=(720, None),
        )
        lbl.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))
        sv.add_widget(lbl)
        return sv


TestApp().run()
