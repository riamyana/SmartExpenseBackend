import re
import tempfile

from fastapi import HTTPException
import pandas as pd
import pdfplumber
import fitz
from dateutil.parser import parse

from app.db.category import Category
from app.handlers.statements.statement_base import StatementBase, StatementResponse
from app.handlers.statements.statement_columns_const import DATE_KEYWORDS, DATE_KEYWORDS, DEPOSIT_KEYWORDS, DESCRIPTION_KEYWORDS, WITHDRAWAL_KEYWORDS
from app.models.transactions import TransactionModel


class PDFStatement(StatementBase):
    DATE_PATTERN = re.compile(
        r"\b(?:"
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
        r"\d{1,2}[-\s](?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[-\s]\d{2,4}"
        r")\b",
        re.IGNORECASE,
    )
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

        header_found = False
        date_index = 0
        # with pdfplumber.open(tmp_path) as pdf:
        #     current_row = None
        #     for page in pdf.pages:
        #         table = page.extract_table(
        #             table_settings={
        #                 "vertical_strategy": "lines",
        #                 "horizontal_strategy": "text",
        #                 "snap_tolerance": 3,
        #                 "join_tolerance": 3
        #             }
        #         )
        #         if table:
        #             for t in table:
        #                 if not t:
        #                     continue

        #                 if not header_found and self.is_header_row(t):
        #                     date_index = next(
        #                         (
        #                             i for i, x in enumerate(t)
        #                             if re.search(r"\bdate\b", str(x).lower())
        #                         ),
        #                         None
        #                     )
                            
        #                     description_index = self.find_description_index(t)

        #                     rows.append(t)
        #                     header_found = True
        #                     continue
                        
        #                 if (
        #                     header_found
        #                     and date_index is not None
        #                     and len(t) > date_index
        #                     and t[date_index]
        #                     and self.is_date(t[date_index])
        #                 ):

        #                     current_row = t
        #                     rows.append(t)

        #                 if (
        #                     current_row
        #                     and description_index is not None
        #                     and len(t) > description_index
        #                     and t[description_index]
        #                 ):

        #                     current_description = (
        #                         current_row[description_index] or ""
        #                     )

        #                     continuation = t[description_index]

        #                     current_row[description_index] = (
        #                         current_description
        #                         + " "
        #                         + continuation
        #                     ).strip()

        text = ""
        doc = fitz.open(tmp_path)

        for page in doc:
            words = page.get_text("words")

            print(words[0:500])
        
        if len(rows) <= 1:
            raise HTTPException(
                status_code=400,
                detail="Unable to extract transactions from statement PDF."
            )

        df = pd.DataFrame(rows[1:], columns=rows[0])  # skip header
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        date_col = self.find_column(df.columns, DATE_KEYWORDS)
        desc_col = self.find_column(df.columns, DESCRIPTION_KEYWORDS)
        withdrawal_col = self.find_column(df.columns, WITHDRAWAL_KEYWORDS)
        deposit_col = self.find_column(df.columns, DEPOSIT_KEYWORDS)

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
        match = self.DATE_PATTERN.search(str(x))
        if not match:
            return None
        try:
            return parse(match.group(0)).strftime("%Y-%m-%d")
        except:
            return None

    def is_date(self, value):
        return bool(self.DATE_PATTERN.search(str(value)))

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

    def contains_keywords(self, text: str, keywords: list[str]) -> bool:

        text = text.lower()

        return any(
            re.search(rf"\b{re.escape(keyword)}\b", text)
            for keyword in keywords
        )


    def is_header_row(self, row):

        text = " ".join(
            str(x).lower()
            for x in row
            if x
        )

        has_date = re.search(r"\bdate\b", text)

        has_transaction_columns = any([
            self.contains_keywords(text, DESCRIPTION_KEYWORDS),
            self.contains_keywords(text, WITHDRAWAL_KEYWORDS),
            self.contains_keywords(text, DEPOSIT_KEYWORDS)
        ])

        return has_date and has_transaction_columns

    def find_description_index(self, row):
        for i, value in enumerate(row):
            if not value:
                continue

            text = str(value).lower()

            for keyword in DESCRIPTION_KEYWORDS:
                if re.search(
                    rf"\b{re.escape(keyword)}\b",
                    text
                ):
                    return i

        return None

    @property
    def description(self):
        return "PDF Statement"
