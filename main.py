from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView

lines = []

for name in ["typing_extensions", "sqlalchemy", "greenlet", "mako", "pytz", "requests", "urllib3", "certifi"]:
    try:
        __import__(name)
        lines.append("OK   " + name)
    except Exception as e:
        lines.append("FAIL " + name + ": " + str(e)[:80])


class T(MDApp):
    def build(self):
        sv = ScrollView()
        lbl = MDLabel(
            text="IMPORT TEST:\n\n" + "\n".join(lines),
            size_hint_y=None, halign="left", valign="top",
            text_size=(720, None),
        )
        lbl.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))
        sv.add_widget(lbl)
        return sv


T().run()
