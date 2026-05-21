import re
import tempfile

import pandas as pd
import pdfplumber
from dateutil.parser import parse

from app.db.category import Category
from app.handlers.statements.statement_base import StatementBase, StatementResponse
from app.models.transactions import TransactionModel


class PDFStatement(StatementBase):
    CATEGORY_KEYWORDS = {
        "Food": (
            "restaurant", "cafe", "coffee", "food", "swiggy", "zomato",
            "domino", "pizza", "hotel", "bakery", "grocery", "supermarket"
        ),
        "Travel": (
            "uber", "ola", "taxi", "metro", "rail", "irctc", "flight", "rickshaw",
            "airline", "fuel", "petrol", "diesel", "parking", "toll", "bus"
        ),
        "Shopping": (
            "amazon", "flipkart", "myntra", "shop", "store", "retail",
            "mall", "market", "purchase"
        ),
        "Bills": (
            "electricity", "water", "gas", "utility", "bill", "recharge",
            "mobile", "broadband", "internet", "dth", "rent", "emi"
        ),
        "Salary": ("salary", "payroll", "wages"),
        "Investment": (
            "mutual fund", "sip", "stock", "equity", "broker", "zerodha",
            "groww", "upstox", "dividend", "interest", "fd", "deposit"
        ),
        "Health": (
            "hospital", "clinic", "medical", "medicine", "pharmacy",
            "doctor", "health", "diagnostic"
        ),
        "Entertainment": (
            "movie", "cinema", "netflix", "prime video", "hotstar",
            "spotify", "bookmyshow", "game"
        ),
        "Transfer": (
            "transfer", "neft", "imps", "rtgs", "upi", "atm", "cash",
            "withdrawal", "self", "wallet"
        ),
    }
    FALLBACK_CATEGORY_IDS = {
        "Food": 1,
        "Travel": 2,
        "Shopping": 3,
        "Bills": 4,
        "Salary": 5,
        "Investment": 6,
        "Health": 7,
        "Entertainment": 8,
        "Transfer": 9,
        "Other": 10,
    }

    def process(self) -> StatementResponse:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(self.request.file.file.read())
            tmp_path = tmp.name
        
        rows = []

        date_index = 0
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    for t in table:
                        exists = any(
                            any("date" in str(x).lower() for x in sublist)
                            for sublist in rows
                        )

                        if any("date" in str(x).lower() for x in t) and not exists:
                            date_index = next(i for i, x in enumerate(t) if "date" in str(x).lower())
                            rows.append(t)

                        if t[date_index] is not None and self.is_date(t[date_index]):
                            rows.append(t)

        df = pd.DataFrame(rows[1:], columns=rows[0])  # skip header
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        date_col = self.find_column(df.columns, ["date"])
        desc_col = self.find_column(df.columns, ["description", "details"])
        withdrawal_col = self.find_column(df.columns, ["withdraw", "debit", "dr"])
        deposit_col = self.find_column(df.columns, ["deposit", "credit", "cr"])

        category_ids = self.get_category_ids()

        df = df[df[date_col].apply(self.is_date)]
        df["date"] = df[date_col].apply(self.normalize_date)
        df['withdrawal'] = df[withdrawal_col].apply(self.clean_amount) if withdrawal_col else 0
        df['deposit'] = df[deposit_col].apply(self.clean_amount) if deposit_col else 0
        df["description"] = df[desc_col].astype(str).str.strip()
        df["category"] = [
            self.detect_category(description, withdrawal, deposit, category_ids)
            for description, withdrawal, deposit in zip(df["description"], df["withdrawal"], df["deposit"])
        ]

        print(df.head())
        records = df.to_dict(orient="records")

        transactions = [
            TransactionModel(
                id=i,
                **row
            )
            for i, row in enumerate(records)
        ]
        print(records)
        
        
        # dfs = tabula.read_pdf(tmp_path, pages="all", multiple_tables=True)

        # # Combine all tables
        # df = pd.concat(dfs)

        # # Clean column names (optional)
        # # df.columns = [col.strip() for col in df.columns]

        # # print(df.head(n=1000))
        # print(df.to_dict(orient="records"))

        response = StatementResponse(
            transactions=transactions,
            success=True
        )

        return response

    def normalize_date(self, x):
        try:
            return parse(str(x)).strftime("%Y-%m-%d")
        except:
            return None

    def is_date(self, value):
        try:
            parse(str(value), fuzzy=False)
            return True
        except:
            return False

    def find_column(self, columns, keywords):
        for col in columns:
            col_clean = col.lower()
            for k in keywords:
                if col_clean == k:
                    return col
            
            words = re.sub(r'[^\w]', ' ', col_clean).split()
            if any(k in words for k in keywords):
                return col
        return None

    def clean_amount(self, amount):
        print(amount)
        if pd.isna(amount) or amount == '':
            return 0
        return float(str(amount).replace(',', '').strip())

    def get_category_ids(self):
        ids = dict(self.FALLBACK_CATEGORY_IDS)
        categories = self.session.query(Category.id, Category.name).all()
        ids.update({name: category_id for category_id, name in categories})
        return ids

    def detect_category(self, description, withdrawal, deposit, category_ids):
        text = str(description).lower()

        if deposit > 0 and any(keyword in text for keyword in self.CATEGORY_KEYWORDS["Salary"]):
            return category_ids["Salary"]

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if category == "Salary":
                continue

            if any(keyword in text for keyword in keywords):
                return category_ids[category]

        if deposit > 0:
            return category_ids["Salary"]

        return category_ids["Other"]

    @property
    def description(self):
        return "PDF Statement"
