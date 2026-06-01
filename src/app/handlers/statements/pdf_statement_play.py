from collections import defaultdict
import re
import tempfile

from fastapi import HTTPException
import pandas as pd
import pdfplumber
import fitz
from dateutil.parser import parse

from app.db.category import Category
from app.handlers.statements.statement_base import StatementBase, StatementResponse
from app.handlers.statements.statement_columns_const import BALANCE_KEYWORDS, DATE_KEYWORDS, DATE_KEYWORDS, DEPOSIT_KEYWORDS, DESCRIPTION_KEYWORDS, WITHDRAWAL_KEYWORDS
from app.models.transactions import TransactionModel


class PDFStatementPlay(StatementBase):
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
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(self.request.file.file.read())
            tmp_path = tmp.name
            print(f"Saved uploaded file to {tmp_path}")
            
            doc = fitz.open(tmp_path)

            all_transactions = []

            # for page in doc:

            #     words = page.get_text("words")

            #     grouped = defaultdict(list)

            #     # GROUP BY BLOCK

            #     for word in words:

            #         block_no = word[5]

            #         grouped[block_no].append(word)

            #     # PROCESS BLOCKS

            #     for block_no, block_words in grouped.items():

            #         if not self.is_transaction(block_words):
            #             continue

            #         transaction = {
            #             "serial": "",
            #             "txn_date": "",
            #             "value_date": "",
            #             "description": [],
            #             "debit": "",
            #             "credit": "",
            #             "balance": "",
            #         }

            #         # SORT LEFT TO RIGHT

            #         block_words = sorted(
            #             block_words,
            #             key=lambda x: (x[1], x[0])
            #         )

            #         for word in block_words:

            #             x0, y0, x1, y1, text, *_ = word

            #             mid_x = (x0 + x1) / 2

            #             column = self.get_column(mid_x)

            #             if not column:
            #                 continue

            #             if column == "description":

            #                 transaction["description"].append(text)

            #             else:

            #                 if transaction[column]:

            #                     transaction[column] += " " + text

            #                 else:

            #                     transaction[column] = text

            #         transaction["description"] = self.merge_description(
            #             transaction["description"]
            #         )

            #         all_transactions.append(transaction)

            # for t in all_transactions:
                # print(t)
 
            for page in doc:
                words = page.get_text("words")

                header_block = self.detect_header_block(words)

                if not header_block:
                    continue

                # column_ranges = self.build_column_ranges(
                #     header_block
                # )

                break
        
        print('header_block:\n', header_block)

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
        response = StatementResponse(
            transactions=[],
            success=True
        )

        return response
    
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
    def build_column_ranges(self, header_words):

        """
        Returns:
        {
            "date": (50, 100),
            ...
        }
        """

        if not header_words:
            return

        column_positions = {}

        # FIND HEADER POSITIONS

        for word in header_words:

            x0, y0, x1, y1, text, *_ = word

            text_lower = str(text).lower()

            for key, keywords in self.KEYWORD_MAP.items():

                if (
                    key not in column_positions
                    and self.contains_keyword(text_lower, keywords)
                ):

                    column_positions[key] = x0

        # SORT BY X

        sorted_columns = sorted(
            column_positions.items(),
            key=lambda x: x[1]
        )

        column_ranges = {}

        for i, (key, start_x) in enumerate(sorted_columns):

            if i < len(sorted_columns) - 1:

                next_x = sorted_columns[i + 1][1]

                end_x = next_x

            else:

                end_x = start_x + 120

            column_ranges[key] = (
                round(start_x),
                round(end_x)
            )

        return column_ranges

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
