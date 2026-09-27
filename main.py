from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView

lines = []

try:
    from database import init_db, Session, Stock
    lines.append("OK   import database")
except Exception as e:
    import traceback
    lines.append("FAIL import database:\n" + traceback.format_exc())

try:
    init_db()
    lines.append("OK   init_db")
except Exception as e:
    import traceback
    lines.append("FAIL init_db:\n" + traceback.format_exc())

try:
    db = Session()
    stocks = db.query(Stock).all()
    lines.append("OK   query: " + str([s.symbol for s in stocks]))
    db.close()
except Exception as e:
    import traceback
    lines.append("FAIL query:\n" + traceback.format_exc())

try:
    from mpesa import get_access_token
    lines.append("OK   import mpesa")
except Exception as e:
    import traceback
    lines.append("FAIL import mpesa:\n" + traceback.format_exc())


class T(MDApp):
    def build(self):
        sv = ScrollView()
        lbl = MDLabel(
            text="TEST 3:\n\n" + "\n".join(lines),
            size_hint_y=None, halign="left", valign="top",
            text_size=(720, None),
        )
        lbl.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))
        sv.add_widget(lbl)
        return sv


T().run()
