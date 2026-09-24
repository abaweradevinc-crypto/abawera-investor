import sys, os, traceback

results = []

def _log(m):
    results.append(m)

def try_step(name, fn):
    try:
        fn()
        _log("OK   " + name)
    except Exception as e:
        _log("FAIL " + name + ": " + repr(e))

try_step("import kivy",         lambda: __import__("kivy"))
try_step("import kivymd",       lambda: __import__("kivymd"))
try_step("import sqlalchemy",   lambda: __import__("sqlalchemy"))
try_step("import requests",     lambda: __import__("requests"))
try_step("import kivy.core.window", lambda: __import__("kivy.core.window"))

def _db_test():
    from database import init_db, Session, Stock
    init_db()
    db = Session()
    stocks = db.query(Stock).all()
    syms = [s.symbol for s in stocks]
    db.close()
    _log("   stocks: " + str(syms))

try_step("database init", _db_test)

def _show():
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.uix.scrollview import ScrollView
    class DiagApp(App):
        def build(self):
            sv = ScrollView()
            lbl = Label(
                text="DIAGNOSTICS:

" + "
".join(results),
                size_hint_y=None, halign="left", valign="top",
                font_size="12sp", text_size=(720, None),
            )
            lbl.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))
            sv.add_widget(lbl)
            return sv
    DiagApp().run()

try:
    _show()
except BaseException:
    err = traceback.format_exc()
    _log("FATAL: " + err)
    try:
        _show()
    except:
        pass
