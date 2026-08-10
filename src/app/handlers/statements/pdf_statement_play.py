from collections import defaultdict
import re
import tempfile
from math import inf

from fastapi import HTTPException
import pandas as pd
import pdfplumber
import fitz
from dateutil.parser import parse

from datetime import datetime

from app.db.category import Category
from app.handlers.statements.statement_base import StatementBase, StatementResponse
from app.handlers.statements.statement_columns_const import BALANCE_KEYWORDS, DATE_KEYWORDS, DATE_KEYWORDS, DEPOSIT_KEYWORDS, DESCRIPTION_KEYWORDS, WITHDRAWAL_KEYWORDS
from app.models.transactions import TransactionModel


class PDFStatementPlay(StatementBase):
    DATE_PATTERN = re.compile(
        r"\b(?:"
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
        r"\d{1,2}[-\s](?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[-\s]\d{2,4}"
        r")\b",
        re.IGNORECASE,
    )

    COLUMN_RANGES = {
        "serial": (20, 50),
        "txn_date": (50, 100),
        "value_date": (100, 145),
        "description": (145, 360),
        "debit": (390, 450),
        "credit": (450, 520),
        "balance": (520, 600),
    }
    
    KEYWORD_MAP = {
        "date": DATE_KEYWORDS,
        "description": DESCRIPTION_KEYWORDS,
        "debit": WITHDRAWAL_KEYWORDS,
        "credit": DEPOSIT_KEYWORDS,
        "balance": BALANCE_KEYWORDS,
    }
    
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
        # with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        #     tmp.write(self.request.file.file.read())
        #     tmp_path = tmp.name
        #     print(f"Saved uploaded file to {tmp_path}")
            
        #     doc = fitz.open(tmp_path)

        #     all_transactions = []

        #     # for page in doc:

        #     #     words = page.get_text("words")

        #     #     grouped = defaultdict(list)

        #     #     # GROUP BY BLOCK

        #     #     for word in words:

        #     #         block_no = word[5]

        #     #         grouped[block_no].append(word)

        #     #     # PROCESS BLOCKS

        #     #     for block_no, block_words in grouped.items():

        #     #         if not self.is_transaction(block_words):
        #     #             continue

        #     #         transaction = {
        #     #             "serial": "",
        #     #             "txn_date": "",
        #     #             "value_date": "",
        #     #             "description": [],
        #     #             "debit": "",
        #     #             "credit": "",
        #     #             "balance": "",
        #     #         }

        #     #         # SORT LEFT TO RIGHT

        #     #         block_words = sorted(
        #     #             block_words,
        #     #             key=lambda x: (x[1], x[0])
        #     #         )

        #     #         for word in block_words:

        #     #             x0, y0, x1, y1, text, *_ = word

        #     #             mid_x = (x0 + x1) / 2

        #     #             column = self.get_column(mid_x)

        #     #             if not column:
        #     #                 continue

        #     #             if column == "description":

        #     #                 transaction["description"].append(text)

        #     #             else:

        #     #                 if transaction[column]:

        #     #                     transaction[column] += " " + text

        #     #                 else:

        #     #                     transaction[column] = text

        #     #         transaction["description"] = self.merge_description(
        #     #             transaction["description"]
        #     #         )

        #     #         all_transactions.append(transaction)

        #     # for t in all_transactions:
        #         # print(t)
 
        #     for page in doc:
        #         words = page.get_text("words")
        #         header_block = self.detect_header_block(words)
        #         column_ranges = self.build_column_ranges(header_block)
        #         print(column_ranges)
        
        # with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        #     tmp.write(self.request.file.file.read())
        #     tmp_path = tmp.name
        #     print(f"Saved uploaded file to {tmp_path}")
            
        #     doc = fitz.open(tmp_path)

        #     for page in doc:
        #         words = page.get_text("words")

        #         header_block = self.detect_header_block(words)

        #         if not header_block:
        #             continue

        #         break
        
        # print('header_block:\n', header_block)

        # with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        #     temp.write(self.request.file.file.read())
        #     tmp_path = tmp.name
        #     print(f"Saved uploaded file to {tmp_path}")
            
        #     doc = fitz.open(tmp_path)

        #     for page in doc:
        #         words = page.get_text("words")

        #         group = self.group_by_line(words)
        #         merged_groups = self.merge_same_x0_groups(group)

        #         # todo: we need to someting to identify rows from header block. maybe we can use y coordinate of header block to filter rows below it.
        #         print("\n\n")
        #         print(merged_groups)
                
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(self.request.file.file.read())
            tmp_path = tmp.name

        doc = fitz.open(tmp_path)

        header_block = None
        header_bottom_y = None
        header_page_no = None

        # FIND HEADER ONCE

        for page_no, page in enumerate(doc):

            words = page.get_text("words")

            header_block = self.detect_header_block(words)

            if header_block:

                column_ranges = self.build_column_ranges(
                    header_block
                )

                date_range = None

                for column_name, column_range in column_ranges.items():

                    # I think this is not usesful
                    if "date" in column_name.lower():

                        date_range = column_range
                        break

                if date_range is None:

                    raise ValueError(
                        "Date column not found in header"
                    )

                header_page_no = page_no

                header_words = [
                    word
                    for group in header_block
                    for word in group
                ]

                header_bottom_y = max(
                    word[3]
                    for word in header_words
                )

                break

        if not header_block:
            raise ValueError("Could not detect statement header")

        print("header_block:\n", header_block)
        # range = self.build_column_ranges(header_block)
        print("header_bottom_y:", header_bottom_y)
        column_ranges = self.normalize_column_ranges(column_ranges)
        print("\nrange", column_ranges)

        # PROCESS TRANSACTIONS

        record_start_x0 = None

        # todo: real version below
        records = []
        for page_no, page in enumerate(doc):
            words = page.get_text("words")

            # Skip content above header on header page
            if page_no == header_page_no:

                words = [
                    word
                    for word in words
                    if word[1] > header_bottom_y
                ]

            grouped = defaultdict(list)

            for word in words:
                block_no = word[5]
                grouped[block_no].append(word)

            for block_no, block_words in grouped.items():
                groups = self.group_by_line(block_words)

                merged_groups = self.merge_same_x0_groups(groups)

                if not merged_groups:
                    continue

                has_transaction_date = False

                for group in merged_groups:
                    # print(
                    #     "\nx0=",
                    #     group[0][0],
                    #     "text=",
                    #     " ".join(str(w[4]) for w in group)
                    # )

                    first_x0 = group[0][0]

                    # Group must fall inside Date column
                    # if not (
                    #     date_range[0]
                    #     <= first_x0
                    #     <= date_range[1]
                    # ):
                    #     continue
                    
                    if not (
                        column_ranges['transaction_date'][0]
                        <= first_x0
                        <= column_ranges['transaction_date'][1]
                    ):
                        continue

                    text = " ".join(
                        str(word[4])
                        for word in group
                    ).strip()

                    # print("DATE COLUMN TEXT:", text)

                    if (
                        self.is_date(text)
                        or re.search(r"\d{1,2}-\d{1,2}-\d{2,4}", text)
                        or re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", text)
                        or re.search(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4}", text)
                    ):
                        has_transaction_date = True
                        break

                if not has_transaction_date:
                    continue

                # print(f"\nPAGE={page_no} BLOCK={block_no}")
                # print(merged_groups)

                records.append(merged_groups)
        doc.close()
        print("\nrecords length", len(records))
        print("\nfirst record", records[0] if records else "No records")
        print("\nlast record", records[-1] if records else "No records")
        
        block_words = [
            (44.0, 362.28399658203125, 48.472999572753906, 375.1000061035156, '#', 16, 0, 0), 
            (75.18000030517578, 362.28399658203125, 92.75699615478516, 375.1000061035156, 'Date', 16, 1, 0), 
            (124.19000244140625, 362.28399658203125, 167.45303344726562, 375.1000061035156, 'Description', 16, 2, 0), 
            (279.6600036621094, 362.28399658203125, 312.2939758300781, 375.1000061035156, 'Chq/Ref.', 16, 3, 0), 
            (314.0939636230469, 362.28399658203125, 327.03594970703125, 375.1000061035156, 'No.', 16, 3, 1), 
            (354.8500061035156, 362.28399658203125, 398.0320129394531, 375.1000061035156, 'Withdrawal', 16, 4, 0), 
            (399.8320007324219, 362.28399658203125, 416.1849670410156, 375.1000061035156, '(Dr.)', 16, 4, 1), 
            (428.8999938964844, 362.28399658203125, 457.7989501953125, 375.1000061035156, 'Deposit', 16, 5, 0), 
            (459.59893798828125, 362.28399658203125, 475.555908203125, 375.1000061035156, '(Cr.)', 16, 5, 1), 
            (497.95001220703125, 362.28399658203125, 528.0999755859375, 375.1000061035156, 'Balance', 16, 6, 0),
        ]
        
        # group = self.group_by_line(block_words)
        # merged_groups = self.merge_same_x0_groups(group)

        # print(merged_groups)
        
        transactions = []

        id = 0
        category_ids = self.get_category_ids()

        for idx, record in enumerate(records, start=1):

            transaction = self.build_transaction_model(
                record=record,
                column_ranges=column_ranges,
                transaction_id=idx
            )

            if transaction.transaction_date is not None:
                transaction.id = id
                transactions.append(transaction)
                transaction.category_id = self.detect_category(
                    description=transaction.description,
                    withdrawal=transaction.withdrawal,
                    deposit=transaction.deposit,
                    category_ids=category_ids
                )
                id += 1


        response = StatementResponse(
            transactions=transactions,
            success=True
        )

        return response

    def parse_date(self, text):
        formats = [
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%d-%m-%y",
            "%d/%m/%y",
            "%d %b %Y",   # 01 Mar 2026
            "%d %B %Y",   # 01 March 2026
        ]

        text = text.strip()

        for fmt in formats:

            try:
                return datetime.strptime(
                    text,
                    fmt
                ).date()

            except ValueError:
                continue

        return None

    def get_category_ids(self):
        ids = dict(self.FALLBACK_CATEGORY_IDS)
        categories = self.session.query(Category.id, Category.name).all()
        ids.update({name: category_id for category_id, name in categories})
        return ids

    def detect_category(self, description, withdrawal, deposit, category_ids):
        text = str(description).lower()

        if deposit and deposit > 0 and any(keyword in text for keyword in self.CATEGORY_KEYWORDS["Salary"]):
            return category_ids["Salary"]

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if category == "Salary":
                continue

            if any(keyword in text for keyword in keywords):
                return category_ids[category]

        if deposit and deposit > 0:
            return category_ids["Salary"]

        return category_ids["Other"]

    def build_transaction_model(
        self,
        record,
        column_ranges,
        transaction_id
    ):

        data = {
            "id": transaction_id,
            "date": None,
            "category": 0,
            "description": None,
            "withdrawal": None,
            "deposit": None,
        }

        for group in record:

            if not group:
                continue

            first_x0 = group[0][0]

            text = " ".join(
                str(word[4])
                for word in group
            ).strip()

            for field_name, (start_x, end_x) in column_ranges.items():

                if not any(
                    start_x <= word[0] <= end_x
                    for word in group
                ):
                    continue

                if field_name == "transaction_date":

                    try:

                        data["date"] = self.parse_date(text)

                    except Exception:

                        try:

                            data["date"] = datetime.strptime(
                                text,
                                "%d/%m/%Y"
                            ).date()

                        except Exception:
                            pass

                elif field_name == "description":

                    if data["description"]:

                        data["description"] += " " + text

                    else:

                        data["description"] = text

                elif field_name == "withdrawal":

                    if text and text != "-":

                        try:

                            data["withdrawal"] = float(
                                text.replace(",", "")
                            )

                        except Exception:
                            pass

                elif field_name == "deposit":

                    if text and text != "-":

                        try:

                            data["deposit"] = float(
                                text.replace(",", "")
                            )

                        except Exception:
                            pass

                break

        print('\ndata', data)
        id = len(data)
        return TransactionModel(
            id=id,
            date=data["date"],
            category_id=data["category"],
            description=data["description"],
            withdrawal=data["withdrawal"],
            deposit=data["deposit"],
        )
    def normalize_column_ranges(self, column_ranges):
        normalized = {}

        for header_name, value in column_ranges.items():

            header_lower = header_name.lower()

            if self.contains_keyword(
                header_lower,
                DATE_KEYWORDS
            ):
                normalized["transaction_date"] = value

            elif self.contains_keyword(
                header_lower,
                DESCRIPTION_KEYWORDS
            ):
                normalized["description"] = value

            elif self.contains_keyword(
                header_lower,
                WITHDRAWAL_KEYWORDS
            ):
                normalized["withdrawal"] = value

            elif self.contains_keyword(
                header_lower,
                DEPOSIT_KEYWORDS
            ):
                normalized["deposit"] = value

            elif self.contains_keyword(
                header_lower,
                BALANCE_KEYWORDS
            ):
                normalized["balance"] = value

        return normalized

    def merge_same_x0_groups(self, groups, tolerance=5):
        result = []
        visited = set()

        for i in range(len(groups)):

            if i in visited:
                continue

            start_x0 = groups[i][0][0]

            match_index = None

            for j in range(i + 1, len(groups)):

                current_x0 = groups[j][0][0]

                if abs(current_x0 - start_x0) <= tolerance:
                    match_index = j
                    break

            if match_index is not None:

                merged = []

                for k in range(i, match_index + 1):

                    merged.extend(groups[k])
                    visited.add(k)

                result.append(merged)

            else:

                result.append(groups[i])
                visited.add(i)

        return result
    
    def group_by_line(self, words):
        groups = []

        current_group = []
        current_line_no = None

        # sort by line_no, then word_no
        words = sorted(
            words,
            key=lambda x: (x[6], x[7])
        )

        for word in words:

            line_no = word[6]

            if current_line_no is None:

                current_group.append(word)
                current_line_no = line_no

            elif line_no == current_line_no:

                current_group.append(word)

            else:
                groups.append(current_group)

                current_group = [word]
                current_line_no = line_no

        if current_group:
            groups.append(current_group)

        return groups

    def contains_keyword(self, text, keywords):
        text = text.lower()

        for keyword in keywords:

            keyword = keyword.replace("_", " ")

            if re.search(
                rf"\b{re.escape(keyword)}\b",
                text
            ):
                return True

        return False

    # def detect_header_block(self, words):

    #     grouped = defaultdict(list)

    #     # GROUP BY BLOCK + Y BUCKET

    #     for word in words:

    #         x0, y0, x1, y1, text, block_no, *_ = word

    #         y_bucket = round(y0 / 10)

    #         grouped[(block_no, y_bucket)].append(word)


    #     # MERGE NEARBY HEADER GROUPS

    #     merged_groups = []

    #     visited = set()

    #     keys = sorted(grouped.keys())

    #     for i, (block1, y1) in enumerate(keys):

    #         if (block1, y1) in visited:
    #             continue

    #         current_group = list(grouped[(block1, y1)])

    #         visited.add((block1, y1))

    #         for j in range(i + 1, len(keys)):

    #             block2, y2 = keys[j]

    #             if (
    #                 block1 == block2
    #                 and abs(y1 - y2) <= 1
    #             ):

    #                 current_group.extend(
    #                     grouped[(block2, y2)]
    #                 )

    #                 visited.add((block2, y2))

    #         merged_groups.append(current_group)


    #     # FIND HEADER

    #     for group_words in merged_groups:

    #         # SORT LEFT TO RIGHT

    #         group_words = sorted(
    #             group_words,
    #             key=lambda w: (w[0], w[1])
    #         )

    #         joined_text = " ".join(
    #             str(w[4]).lower()
    #             for w in group_words
    #         )

    #         matched_keys = []

    #         for key, keywords in self.KEYWORD_MAP.items():

    #             if self.contains_keyword(
    #                 joined_text,
    #                 keywords
    #             ):

    #                 matched_keys.append(key)

    #         # at least 3 header types

    #         if len(matched_keys) >= 3:

    #             return group_words

    #     return None

    def is_date(self, value):
        return bool(self.DATE_PATTERN.search(str(value)))

    def detect_header_block(self, words):

        grouped = defaultdict(list)

        # GROUP BY BLOCK

        for word in words:

            block_no = word[5]

            grouped[block_no].append(word)

        # PROCESS BLOCKS

        for block_no, block_words in grouped.items():

            groups = self.group_by_line(block_words)

            groups = self.merge_same_x0_groups(groups)

            matched_keys = set()

            for group in groups:

                text = " ".join(
                    str(word[4]).lower()
                    for word in group
                )

                for key, keywords in self.KEYWORD_MAP.items():

                    if self.contains_keyword(text, keywords):

                        matched_keys.add(key)

            if len(matched_keys) >= 3:

                return groups

        return None

    # def build_column_ranges(self, header_block):
    #     column_positions = {}

    #     for group in header_block:

    #         text = " ".join(
    #             str(word[4]).lower()
    #             for word in group
    #         )

    #         x0 = min(word[0] for word in group)

    #         for key, keywords in self.KEYWORD_MAP.items():

    #             if (
    #                 key not in column_positions
    #                 and self.contains_keyword(text, keywords)
    #             ):
    #                 column_positions[key] = x0

    #     if not column_positions:
    #         return {}

    #     sorted_columns = sorted(
    #         column_positions.items(),
    #         key=lambda x: x[1]
    #     )

    #     column_ranges = {}

    #     for i, (column_name, start_x) in enumerate(sorted_columns):

    #         if i < len(sorted_columns) - 1:

    #             end_x = sorted_columns[i + 1][1]

    #         else:

    #             end_x = start_x + 120

    #         column_ranges[column_name] = (
    #             round(start_x),
    #             round(end_x)
    #         )

    #     return column_ranges

    def build_column_ranges(self, header_block):

        columns = []

        for group in header_block:

            text = " ".join(
                str(word[4]).strip()
                for word in group
            )

            if len(group) == 1:

                center_x = group[0][0]

            else:
                # first x0 + last x0 / 2
                center_x = (
                    group[0][0]
                    + group[-1][0]
                ) / 2

            columns.append(
                (text, center_x)
            )

        ranges = {}

        for i, (column_name, center_x) in enumerate(columns):

            if i == 0:

                start = 0

            else:

                prev_center = columns[i - 1][1]

                start = (
                    prev_center
                    + center_x
                ) / 2

            if i == len(columns) - 1:

                end = inf

            else:

                next_center = columns[i + 1][1]

                end = (
                    center_x
                    + next_center
                ) / 2

            ranges[column_name] = (
                round(start, 2),
                round(end, 2) if end != inf else inf
            )

        return ranges

    def get_column(self, mid_x):
        for column, (start, end) in self.COLUMN_RANGES.items():

            if start <= mid_x <= end:
                return column

        return None


    def clean_text(self, text):
        if not text:
            return ""

        return re.sub(r"\s+", " ", text).strip()


    def merge_description(self, parts):

        result = ""

        for part in parts:

            if not result:
                result = part
                continue

            # merge split words like Se + nt

            if (
                result[-1].isalnum()
                and part
                and part[0].isalnum()
            ):

                result += part

            else:
                result += " " + part

        return self.clean_text(result)


    def is_transaction(self, block):

        text = " ".join(
            word[4]
            for word in block
        )

        has_date = bool(
            re.search(r"\d{2}-\d{2}-\d{4}", text)
        )

        has_amount = bool(
            re.search(r"\d{1,3}(,\d{3})*(\.\d{2})", text)
        )

        return has_date and has_amount

    @property
    def description(self):
        return "PDF Statement Play"
