#!/usr/bin/env python3

def col_to_a1(col_num):
    """Convert column number to A1 notation"""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(col_num % 26 + ord('A')) + result
        col_num //= 26
    return result

# Check column mappings
print("Column mappings:")
print(f"Column 54: {col_to_a1(54)}")  # BB
print(f"Column 55: {col_to_a1(55)}")  # BC  
print(f"Column 56: {col_to_a1(56)}")  # BD
print(f"Column 57: {col_to_a1(57)}")  # BE
print(f"Column 58: {col_to_a1(58)}")  # BF
print(f"Column 59: {col_to_a1(59)}")  # BG
print(f"Column 60: {col_to_a1(60)}")  # BH
print(f"Column 61: {col_to_a1(61)}")  # BI
print(f"Column 62: {col_to_a1(62)}")  # BJ
print(f"Column 63: {col_to_a1(63)}")  # BK
print(f"Column 64: {col_to_a1(64)}")  # BL
print(f"Column 65: {col_to_a1(65)}")  # BM

