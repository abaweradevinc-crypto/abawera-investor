# main.py - ABAWERA INVESTOR (Mobile Optimized)
# Author: ABAWERADEVSINC

from kivy.config import Config
Config.set('graphics', 'width', '720')
Config.set('graphics', 'height', '1280')
Config.set('graphics', 'resizable', '0')

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

from database import init_db, Session, User, Stock, Holding, Transaction
from mpesa import stk_push, b2c_payout

APP_AUTHOR = "ABAWERADEVSINC"


class LoginScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        outer = MDBoxLayout(orientation="vertical", padding=dp(24), spacing=dp(14))

        outer.add_widget(MDLabel(size_hint_y=0.12))

        outer.add_widget(MDLabel(
            text="ABAWERA\nINVESTOR",
            halign="center",
            font_style="H3",
            theme_text_color="Custom",
            text_color=(0, 0.6, 0.3, 1),
            size_hint_y=None, height=dp(130),
        ))

        outer.add_widget(MDLabel(
            text="Stock Trading  |  Lipa na M-Pesa",
            halign="center",
            font_style="Subtitle1",
            size_hint_y=None, height=dp(40),
        ))

        outer.add_widget(MDLabel(size_hint_y=0.08))

        self.phone = MDTextField(
            hint_text="Phone (07XXXXXXXX)",
            input_filter="int",
            mode="rectangle",
            size_hint_y=None, height=dp(64),
            font_size=dp(18),
        )
        self.full_name = MDTextField(
            hint_text="Full Name",
            mode="rectangle",
            size_hint_y=None, height=dp(64),
            font_size=dp(18),
        )
        outer.add_widget(self.phone)
        outer.add_widget(self.full_name)

        outer.add_widget(MDLabel(size_hint_y=0.06))

        outer.add_widget(MDRaisedButton(
            text="LOGIN / REGISTER",
            size_hint=(1, None), height=dp(56),
            font_size=dp(17),
            on_release=self.login,
        ))

        outer.add_widget(MDLabel(size_hint_y=0.03))

        outer.add_widget(MDFlatButton(
            text="▶  QUICK DEMO LOGIN",
            size_hint=(1, None), height=dp(48),
            font_size=dp(15),
            on_release=self.demo_login,
        ))

        outer.add_widget(MDLabel(size_hint_y=0.08))

        outer.add_widget(MDLabel(
            text=f"© {APP_AUTHOR}",
            halign="center",
            font_style="Caption",
            size_hint_y=None, height=dp(30),
        ))

        self.add_widget(outer)

    def login(self, *a):
        phone = self.phone.text.strip()
        name = self.full_name.text.strip() or "Investor"
        if len(phone) < 10:
            Snackbar(text="Enter a valid phone").open()
            return
        db = Session()
        user = db.query(User).filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone, name=name, balance=100000.0)
            db.add(user); db.commit()
        db.close()
        self.manager.current = "dashboard"
        self.manager.get_screen("dashboard").load_user(phone)

    def demo_login(self, *a):
        phone = "254708374149"
        db = Session()
        user = db.query(User).filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone, name="Demo User", balance=100000.0)
            db.add(user); db.commit()
        db.close()
        self.manager.current = "dashboard"
        self.manager.get_screen("dashboard").load_user(phone)


class DashboardScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.phone = None
        main = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        top_card = MDCard(
            orientation="vertical", padding=dp(18), spacing=dp(4),
            size_hint_y=None, height=dp(120),
            md_bg_color=(0, 0.6, 0.3, 1), radius=[dp(14)],
        )
        self.header = MDLabel(
            text="Welcome", font_style="H6",
            theme_text_color="Custom", text_color=(1, 1, 1, 1),
            size_hint_y=None, height=dp(35),
        )
        self.balance_lbl = MDLabel(
            text="KES 0.00", font_style="H4",
            theme_text_color="Custom", text_color=(1, 1, 1, 1),
        )
        top_card.add_widget(self.header)
        top_card.add_widget(self.balance_lbl)
        main.add_widget(top_card)

        actions = MDBoxLayout(
            orientation="horizontal", size_hint_y=None,
            height=dp(54), spacing=dp(10),
        )
        actions.add_widget(MDRaisedButton(
            text="↓ DEPOSIT", size_hint=(1, 1), font_size=dp(14),
            on_release=self.deposit,
        ))
        actions.add_widget(MDRaisedButton(
            text="↑ WITHDRAW", size_hint=(1, 1), font_size=dp(14),
            on_release=self.withdraw,
        ))
        main.add_widget(actions)

        main.add_widget(MDLabel(
            text="Available Stocks", font_style="Subtitle1",
            size_hint_y=None, height=dp(32),
        ))

        scroll = MDScrollView()
        self.stock_list = MDList()
        scroll.add_widget(self.stock_list)
        main.add_widget(scroll)

        bottom = MDBoxLayout(
            orientation="horizontal", size_hint_y=None,
            height=dp(54), spacing=dp(10),
        )
        bottom.add_widget(MDRaisedButton(
            text="PORTFOLIO", size_hint=(1, 1), font_size=dp(14),
            on_release=lambda x: self.show_portfolio(),
        ))
        bottom.add_widget(MDRaisedButton(
            text="HISTORY", size_hint=(1, 1), font_size=dp(14),
            on_release=lambda x: self.show_history(),
        ))
        main.add_widget(bottom)

        self.add_widget(main)

    def load_user(self, phone):
        self.phone = phone
        db = Session()
        u = db.query(User).filter_by(phone=phone).first()
        if u:
            self.header.text = f"Hello, {u.name}"
            self.balance_lbl.text = f"KES {u.balance:,.2f}"
        self.stock_list.clear_widgets()
        for s in db.query(Stock).all():
            item = TwoLineListItem(
                text=s.symbol,
                secondary_text=f"{s.name}  —  KES {s.price:.2f}",
                on_release=lambda x, sym=s.symbol: self.buy_dialog(sym),
            )
            self.stock_list.add_widget(item)
        db.close()

    def deposit(self, *a):
        self._mpesa_prompt("deposit")

    def withdraw(self, *a):
        self._mpesa_prompt("withdraw")

    def _mpesa_prompt(self, action):
        self.amt_field = MDTextField(
            hint_text="Amount (KES)", input_filter="float",
        )
        self.dialog = MDDialog(
            title=f"M-Pesa {action.title()}",
            type="custom", content_cls=self.amt_field,
            buttons=[
                MDFlatButton(text="CANCEL",
                             on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="CONFIRM",
                               on_release=lambda x: self._confirm_mpesa(action))
            ]
        )
        self.dialog.open()

    def _confirm_mpesa(self, action):
        try:
            amt = float(self.amt_field.text)
        except:
            Snackbar(text="Invalid amount").open(); return
        self.dialog.dismiss()
        if action == "deposit":
            res = stk_push(self.phone, amt)
            if res.get("ResponseCode") == "0":
                db = Session()
                u = db.query(User).filter_by(phone=self.phone).first()
                u.balance += amt
                db.add(Transaction(user_phone=self.phone, type="deposit",
                                   amount=amt, details="M-Pesa STK Push"))
                db.commit(); db.close()
                Snackbar(text=f"STK push sent. KES {amt} pending.").open()
                self.load_user(self.phone)
            else:
                Snackbar(text=f"M-Pesa: {res.get('errorMessage', res)}").open()
        else:
            db = Session()
            u = db.query(User).filter_by(phone=self.phone).first()
            if u.balance < amt:
                Snackbar(text="Insufficient balance").open(); db.close(); return
            res = b2c_payout(self.phone, amt)
            if res.get("ResponseCode") == "0" or "ConversationID" in res:
                u.balance -= amt
                db.add(Transaction(user_phone=self.phone, type="withdraw",
                                   amount=amt, details="M-Pesa B2C Payout"))
                db.commit()
                Snackbar(text=f"Withdrawal of KES {amt} initiated.").open()
                self.load_user(self.phone)
            else:
                Snackbar(text=f"Payout error: {res}").open()
            db.close()

    def buy_dialog(self, symbol):
        db = Session()
        stock = db.query(Stock).filter_by(symbol=symbol).first()
        price = stock.price
        db.close()
        self.shares_field = MDTextField(
            hint_text="Shares", input_filter="float",
        )
        self.dialog = MDDialog(
            title=f"Buy {symbol} @ KES {price:.2f}",
            type="custom", content_cls=self.shares_field,
            buttons=[
                MDFlatButton(text="CANCEL",
                             on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="BUY",
                               on_release=lambda x: self._do_buy(symbol, price))
            ]
        )
        self.dialog.open()

    def _do_buy(self, symbol, price):
        try:
            shares = float(self.shares_field.text)
        except:
            Snackbar(text="Invalid share count").open(); return
        cost = shares * price
        db = Session()
        u = db.query(User).filter_by(phone=self.phone).first()
        if u.balance < cost:
            Snackbar(text="Insufficient funds").open(); db.close(); return
        u.balance -= cost
        h = db.query(Holding).filter_by(user_phone=self.phone, symbol=symbol).first()
        if h:
            total = h.shares + shares
            h.buy_price = ((h.buy_price * h.shares) + cost) / total
            h.shares = total
        else:
            db.add(Holding(user_phone=self.phone, symbol=symbol,
                           shares=shares, buy_price=price))
        db.add(Transaction(user_phone=self.phone, type="buy", amount=cost,
                           details=f"Bought {shares} {symbol} @ {price}"))
        db.commit(); db.close()
        self.dialog.dismiss()
        Snackbar(text=f"Bought {shares} {symbol} for KES {cost:.2f}").open()
        self.load_user(self.phone)

    def show_portfolio(self):
        db = Session()
        holdings = db.query(Holding).filter_by(user_phone=self.phone).all()
        lines = []
        for h in holdings:
            stock = db.query(Stock).filter_by(symbol=h.symbol).first()
            cur = stock.price * h.shares
            pl = cur - (h.buy_price * h.shares)
            lines.append(f"{h.symbol}: {h.shares} @ {h.buy_price:.2f}\n"
                         f"   Now {stock.price:.2f} | P/L {pl:+.2f}")
        db.close()
        self._info("My Portfolio", "\n\n".join(lines) or "No holdings yet.")

    def show_history(self):
        db = Session()
        txns = db.query(Transaction).filter_by(user_phone=self.phone)\
                 .order_by(Transaction.timestamp.desc()).limit(15).all()
        lines = [f"{t.timestamp.strftime('%m-%d %H:%M')}  {t.type.upper()}\n"
                 f"   KES {t.amount:.2f}" for t in txns]
        db.close()
        self._info("Transactions", "\n\n".join(lines) or "No transactions yet.")

    def _info(self, title, text):
        d = MDDialog(
            title=title, text=text,
            buttons=[MDFlatButton(text="OK",
                                  on_release=lambda x: d.dismiss())]
        )
        d.open()



def _auto_demo_login(dt):
    app = AbaweraInvestor.get_running_app()
    sm = app.root
    from database import Session, User
    db = Session()
    u = db.query(User).filter_by(phone="254708374149").first()
    if not u:
        u = User(phone="254708374149", name="Demo User", balance=100000.0)
        db.add(u)
        db.commit()
    db.close()
    sm.current = "dashboard"
    sm.get_screen("dashboard").load_user("254708374149")



class AbaweraInvestor(MDApp):
    def build(self):
        self.title = "ABAWERA INVESTOR"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        init_db()
        sm = MDScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.current = "login"  # will be switched shortly
        Clock.schedule_once(_auto_demo_login, 1.0)
        return sm


if __name__ == "__main__":
    AbaweraInvestor().run()
