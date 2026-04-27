import re
import tempfile

import pandas as pd
import pdfplumber
from dateutil.parser import parse

from app.handlers.statements.statement_base import StatementBase, StatementResponse
from app.models.transactions import TransactionModel


class PDFStatement(StatementBase):
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

        df = df[df[date_col].apply(self.is_date)]
        df["date"] = df[date_col].apply(self.normalize_date)
        df['withdrawal'] = df[withdrawal_col].apply(self.clean_amount) if withdrawal_col else 0
        df['deposit'] = df[deposit_col].apply(self.clean_amount) if deposit_col else 0
        df["description"] = df[desc_col].astype(str).str.strip()

        result = df[["date", "description", "withdrawal", "deposit"]]
        print(df.head())
        records = df.to_dict(orient="records")

        transactions = [TransactionModel(**row) for row in records]
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

    @property
    def description(self):
        return "PDF Statement"
