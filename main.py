from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
import json
import os

# Load scrollable edit form layout
Builder.load_string("""
<EditLoanContent>:
    orientation: "vertical"
    spacing: "10dp"
    padding: "12dp"
    size_hint_y: None
    height: self.minimum_height

    MDTextField:
        id: name
        hint_text: "Name"

    MDTextField:
        id: email
        hint_text: "Email"

    MDTextField:
        id: phone
        hint_text: "Phone"

    MDTextField:
        id: amount
        hint_text: "Amount"

    MDTextField:
        id: type
        hint_text: "Type"

    MDTextField:
        id: tenure
        hint_text: "Tenure"
""")


class EditLoanContent(BoxLayout):
    pass

DATA_FILE = "loans.json"

class LoanManager(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_kv_post(self, base_widget):
        self.load_loans()

    def submit_loan(self):
        name = self.ids.name.text.strip()
        email = self.ids.email.text.strip()
        phone = self.ids.phone.text.strip()
        amount = self.ids.amount.text.strip()
        loan_type = self.ids.loan_type.text.strip()
        tenure = self.ids.tenure.text.strip()

        # Validation: Check if any field is empty
        if not all([name, amount]):
            self.dialog = MDDialog(
                title="Missing Fields",
                text="Please fill in all the fields before submitting.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ],
            )
            self.dialog.open()
            return

        loan = {
            "name": name,
            "email": email,
            "phone": phone,
            "amount": amount,
            "type": loan_type,
            "tenure": tenure
        }
        loans = self.load_loan_data()
        loans.append(loan)
        self.save_loan_data(loans)
        self.clear_fields()
        self.load_loans()
        toast("Loan submitted successfully!")

    def clear_fields(self):
        self.ids.name.text = ''
        self.ids.email.text = ''
        self.ids.phone.text = ''
        self.ids.amount.text = ''
        self.ids.loan_type.text = ''
        self.ids.tenure.text = ''

    def load_loan_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_loan_data(self, loans):
        with open(DATA_FILE, 'w') as f:
            json.dump(loans, f, indent=2)

    def load_loans(self):
        self.ids.loans_container.clear_widgets()
        filter_type = self.ids.filter_type.text.strip().lower() if 'filter_type' in self.ids else ""
        loans = self.load_loan_data()

        for idx, loan in enumerate(loans):
            if filter_type and filter_type not in loan['type'].lower():
                continue
            card = MDCard(orientation="vertical", padding=10, size_hint_y=None, height=120)
            card.add_widget(MDLabel(text=f"[b]{loan['name']}[/b] | {loan['type']} | ₹{loan['amount']} | {loan['tenure']}M", markup=True))
            btns = MDBoxLayout(size_hint_y=None, height=40, spacing=10)
            edit_btn = MDFlatButton(text="Edit", on_release=lambda x, i=idx: self.edit_loan(i))
            del_btn = MDFlatButton(text="Delete", on_release=lambda x, i=idx: self.confirm_delete(i))
            btns.add_widget(edit_btn)
            btns.add_widget(del_btn)
            card.add_widget(btns)
            self.ids.loans_container.add_widget(card)

    def edit_loan(self, index):
        loans = self.load_loan_data()
        loan = loans[index]
        self.edit_index = index

        content = EditLoanContent()
        content.ids.name.text = loan['name']
        content.ids.email.text = loan['email']
        content.ids.phone.text = loan['phone']
        content.ids.amount.text = loan['amount']
        content.ids.type.text = loan['type']
        content.ids.tenure.text = loan['tenure']

        self.dialog = MDDialog(
            title="Edit Loan",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Save", on_release=self.save_edit)
            ],
            size_hint=(0.9, None),
            height="550dp"
        )
        self.dialog.open()

    def save_edit(self, *args):
        content = self.dialog.content_cls
        updated = {
            "name": content.ids.name.text,
            "email": content.ids.email.text,
            "phone": content.ids.phone.text,
            "amount": content.ids.amount.text,
            "type": content.ids.type.text,
            "tenure": content.ids.tenure.text
        }
        loans = self.load_loan_data()
        loans[self.edit_index] = updated
        self.save_loan_data(loans)
        self.dialog.dismiss()
        self.load_loans()

    def confirm_delete(self, index):
        self.dialog = MDDialog(
            text="Are you sure you want to delete this loan?",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Delete", on_release=lambda x: self.delete_loan(index))
            ]
        )
        self.dialog.open()

    def delete_loan(self, index):
        loans = self.load_loan_data()
        loans.pop(index)
        self.save_loan_data(loans)
        self.dialog.dismiss()
        self.load_loans()

class LoanApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file("loanmanager.kv")  # Ensure this file contains the layout with loans_container
        return LoanManager()

if __name__ == "__main__":
    LoanApp().run()
