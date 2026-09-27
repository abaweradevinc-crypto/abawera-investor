# main.py
"""
ABAWERA INVESTOR
Stock Trading App with M-Pesa Lipa na M-Pesa
Author: ABAWERADEVSINC
File: AbaweraDevsInc
"""
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
        box = MDBoxLayout(orientation="vertical", padding=30, spacing=20)
        box.add_widget(MDLabel(text="ABAWERA INVESTOR",
                               halign="center", font_style="H4",
                               theme_text_color="Custom",
                               text_color=(0, 0.6, 0.3, 1)))
        box.add_widget(MDLabel(text="Stock Trading | Lipa na M-Pesa",
                               halign="center", font_style="Subtitle1"))

        self.phone = MDTextField(hint_text="Phone (07XXXXXXXX)",
                                 input_filter="int", mode="rectangle")
        self.full_name = MDTextField(hint_text="Full Name", mode="rectangle")
        box.add_widget(self.phone)
        box.add_widget(self.full_name)

        btn = MDRaisedButton(text="LOGIN / REGISTER",
                             pos_hint={"center_x": 0.5},
                             on_release=self.login)
        box.add_widget(btn)
        box.add_widget(MDLabel(text=f"© {APP_AUTHOR}",
                               halign="center", font_style="Caption"))
        self.add_widget(box)

    def login(self, *a):
        phone = self.phone.text.strip()
        name = self.full_name.text.strip() or "Investor"
        if len(phone) < 10:
            Snackbar(text="Enter a valid phone").open()
            return
        db = Session()
        user = db.query(User).filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone, name=name, balance=100000.0)  # demo bonus
            db.add(user)
            db.commit()
        db.close()
        self.manager.current = "dashboard"
        self.manager.get_screen("dashboard").load_user(phone)


class DashboardScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.phone = None
        self.layout = MDBoxLayout(orientation="vertical", padding=10, spacing=8)
        self.header = MDLabel(text="Welcome", font_style="H6")
        self.balance_lbl = MDLabel(text="Balance: KES 0.00", font_style="H6",
                                   theme_text_color="Custom",
                                   text_color=(0, 0.6, 0.3, 1))
        self.layout.add_widget(self.header)
        self.layout.add_widget(self.balance_lbl)

        row1 = MDBoxLayout(size_hint_y=None, height="50dp", spacing=8)
        row1.add_widget(MDRaisedButton(text="DEPOSIT (M-Pesa)",
                                       on_release=self.deposit))
        row1.add_widget(MDRaisedButton(text="WITHDRAW (M-Pesa)",
                                       on_release=self.withdraw))
        self.layout.add_widget(row1)

        self.layout.add_widget(MDLabel(text="Available Stocks",
                                       font_style="Subtitle1"))

        scroll = MDScrollView()
        self.stock_list = MDList()
        scroll.add_widget(self.stock_list)
        self.layout.add_widget(scroll)

        self.layout.add_widget(MDRaisedButton(
            text="MY PORTFOLIO",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.show_portfolio()))
        self.layout.add_widget(MDRaisedButton(
            text="TRANSACTION HISTORY",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.show_history()))

        self.add_widget(self.layout)

    def load_user(self, phone):
        self.phone = phone
        db = Session()
        u = db.query(User).filter_by(phone=phone).first()
        self.header.text = f"Hello, {u.name}"
        self.balance_lbl.text = f"Balance: KES {u.balance:,.2f}"
        self.stock_list.clear_widgets()
        for s in db.query(Stock).all():
            item = TwoLineListItem(
                text=f"{s.symbol} - {s.name}",
                secondary_text=f"KES {s.price:.2f} per share",
                on_release=lambda x, sym=s.symbol: self.buy_dialog(sym)
            )
            self.stock_list.add_widget(item)
        db.close()

    def deposit(self, *a):
        self._mpesa_prompt("deposit")

    def withdraw(self, *a):
        self._mpesa_prompt("withdraw")

    def _mpesa_prompt(self, action):
        self.amt_field = MDTextField(hint_text="Amount (KES)", input_filter="float")
        self.dialog = MDDialog(
            title=f"M-Pesa {action.title()}",
            type="custom",
            content_cls=self.amt_field,
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
            Snackbar(text="Invalid amount").open()
            return
        self.dialog.dismiss()

        if action == "deposit":
            res = stk_push(self.phone, amt)
            if res.get("ResponseCode") == "0":
                db = Session()
                u = db.query(User).filter_by(phone=self.phone).first()
                u.balance += amt
                db.add(Transaction(user_phone=self.phone, type="deposit",
                                   amount=amt, details="M-Pesa STK Push"))
                db.commit()
                db.close()
                Snackbar(text=f"STK push sent. KES {amt} will reflect soon.").open()
                self.load_user(self.phone)
            else:
                Snackbar(text=f"M-Pesa Error: {res.get('errorMessage', res)}").open()
        else:
            db = Session()
            u = db.query(User).filter_by(phone=self.phone).first()
            if u.balance < amt:
                Snackbar(text="Insufficient balance").open()
                db.close()
                return
            res = b2c_payout(self.phone, amt)
            if res.get("ResponseCode") == "0" or "ConversationID" in res:
                u.balance -= amt
                db.add(Transaction(user_phone=self.phone, type="withdraw",
                                   amount=amt, details="M-Pesa B2C Payout"))
                db.commit()
                Snackbar(text=f"Withdrawal of KES {amt} initiated.").open()
                self.load_user(self.phone)
            else:
                Snackbar(text=f"Payout Error: {res}").open()
            db.close()

    def buy_dialog(self, symbol):
        db = Session()
        stock = db.query(Stock).filter_by(symbol=symbol).first()
        price = stock.price
        db.close()

        self.shares_field = MDTextField(hint_text="Shares", input_filter="float")
        self.dialog = MDDialog(
            title=f"Buy {symbol} @ KES {price:.2f}",
            type="custom",
            content_cls=self.shares_field,
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
            Snackbar(text="Invalid share count").open()
            return
        cost = shares * price
        db = Session()
        u = db.query(User).filter_by(phone=self.phone).first()
        if u.balance < cost:
            Snackbar(text="Insufficient funds").open()
            db.close()
            return
        u.balance -= cost
        h = db.query(Holding).filter_by(user_phone=self.phone, symbol=symbol).first()
        if h:
            total_shares = h.shares + shares
            h.buy_price = ((h.buy_price * h.shares) + cost) / total_shares
            h.shares = total_shares
        else:
            db.add(Holding(user_phone=self.phone, symbol=symbol,
                           shares=shares, buy_price=price))
        db.add(Transaction(user_phone=self.phone, type="buy",
                           amount=cost,
                           details=f"Bought {shares} {symbol} @ {price}"))
        db.commit()
        db.close()
        self.dialog.dismiss()
        Snackbar(text=f"Bought {shares} {symbol} for KES {cost:.2f}").open()
        self.load_user(self.phone)

    def show_portfolio(self):
        db = Session()
        holdings = db.query(Holding).filter_by(user_phone=self.phone).all()
        lines = []
        for h in holdings:
            stock = db.query(Stock).filter_by(symbol=h.symbol).first()
            cur_val = stock.price * h.shares
            pl = cur_val - (h.buy_price * h.shares)
            lines.append(f"{h.symbol}: {h.shares} @ {h.buy_price:.2f} | "
                         f"Now {stock.price:.2f} | P/L KES {pl:+.2f}")
        db.close()
        self._info("My Portfolio", "\n".join(lines) or "No holdings yet.")

    def show_history(self):
        db = Session()
        txns = db.query(Transaction).filter_by(user_phone=self.phone)\
                 .order_by(Transaction.timestamp.desc()).limit(20).all()
        lines = [f"{t.timestamp.strftime('%Y-%m-%d %H:%M')} | {t.type.upper()} "
                 f"KES {t.amount:.2f} | {t.details}" for t in txns]
        db.close()
        self._info("Transactions", "\n".join(lines) or "No transactions yet.")

    def _info(self, title, text):
        d = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK",
                                  on_release=lambda x: d.dismiss())]
        )
        d.open()

class AbaweraInvestor(MDApp):
    def build(self):
        self.title = "ABAWERA INVESTOR"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        init_db()

        sm = MDScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        return sm


if __name__ == "__main__":
    AbaweraInvestor().run()
