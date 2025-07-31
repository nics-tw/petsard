import calendar
from datetime import datetime
from pprint import pprint

import pandas as pd

UNIVERSITY_DICT = {
    "001": "國立臺灣大學",
    "002": "國立政治大學",
}

COLLEGE_DICT = {
    # 臺大
    "1000": "文學院",
    "2000": "理學院",
    "9000": "電機資訊學院",
    # 政大
    "100": "文學院",
    "700": "理學院",
    "ZA0": "資訊學院",
}
UNIVERSITY_COLLEGE_COMPARATION_DICT = {
    "001": ["1000", "2000", "9000"],
    "002": ["100", "700", "ZA0"],
}

DEPARTMENT_DICT = {
    # 臺大
    "1010": "中國文學系",
    "1020": "外國語文學系",
    "1030": "歷史學系",
    "1040": "哲學系",
    "1050": "人類學系",
    "1060": "圖書資訊學系",
    "1070": "日本語文學系",
    "1090": "戲劇學系",
    "2010": "數學系",
    "2020": "物理學系",
    "2030": "化學系",
    "2040": "地質科學系",
    "2070": "心理學系",
    "2080": "地理環境資源學系",
    "2090": "大氣科學系",
    "9010": "電機工程學系",
    "9020": "資訊工程學系",
    # 政大
    "101": "中國文學系",
    "102": "教育學系",
    "103": "歷史學系",
    "104": "哲學系",
    "701": "應用數學系",
    "702": "心理學系",
    "703": "資訊科學系",
}
COLLEGE_DEPARTMENT_COMPARATION_DICT = {
    # 臺大
    "1000": ["1010", "1020", "1030", "1040", "1050", "1060", "1070", "1090"],
    "2000": ["2010", "2020", "2030", "2040", "2070", "2080", "2090"],
    "9000": ["9010", "9020"],
    # 政大
    "100": ["101", "102", "103", "104"],
    "700": ["701", "702"],
    "ZA0": ["703"],
}


def check_invalid_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    檢查資料集中不合理的年月日紀錄

    參數:
    df (DataFrame): 包含 birth_year, birth_month, birth_day 欄位的資料框

    返回:
    DataFrame: 包含不合理日期的資料列索引和原因
    """
    invalid_rows = []

    for idx, row in df.iterrows():
        year = row.get("birth_year")
        month = row.get("birth_month")
        day = row.get("birth_day")

        # 檢查是否有缺失值
        if pd.isna(year) or pd.isna(month) or pd.isna(day):
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "缺失值 Missing values",
                    "year": year,
                    "month": month,
                    "day": day,
                }
            )
            continue

        # 轉換為整數
        try:
            year = int(year)
            month = int(month)
            day = int(day)
        except (ValueError, TypeError):
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "格式錯誤 Missing values",
                    "year": year,
                    "month": month,
                    "day": day,
                }
            )
            continue

        # 基本範圍檢查
        if not (1900 <= year <= datetime.now().year):
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "年份超出合理範圍 Year out of reasonable range",
                    "year": year,
                    "month": month,
                    "day": day,
                }
            )
            continue

        if not (1 <= month <= 12):
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "月份超出範圍 Month out of range",
                    "year": year,
                    "month": month,
                    "day": day,
                }
            )
            continue

        # 檢查日期在當月的有效性
        try:
            # 取得當月的最大天數
            max_days = calendar.monthrange(year, month)[1]
            if not (1 <= day <= max_days):
                invalid_rows.append(
                    {
                        "index": idx,
                        "reason": f"該年{month}月沒有{day}日 Day {day} does not exist in {month} that year",
                        "year": year,
                        "month": month,
                        "day": day,
                    }
                )
        except ValueError:
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "無效的日期組合 Invalid date combination",
                    "year": year,
                    "month": month,
                    "day": day,
                }
            )

    return pd.DataFrame(invalid_rows)


def check_invalid_zodiacs(df: pd.DataFrame) -> pd.DataFrame:
    """
    檢查資料集中星座與出生日期是否匹配

    參數:
    df (DataFrame): 包含 birth_month, birth_day, zodiac 欄位的資料框

    返回:
    DataFrame: 包含星座與生日不匹配的資料列索引和詳情
    """
    # 定義星座日期範圍 (月, 日) 的起始
    zodiac_ranges = {
        "摩羯座": [(12, 22), (1, 19)],  # 特殊情況跨年
        "水瓶座": [(1, 20), (2, 18)],
        "雙魚座": [(2, 19), (3, 20)],
        "牡羊座": [(3, 21), (4, 19)],
        "金牛座": [(4, 20), (5, 20)],
        "雙子座": [(5, 21), (6, 21)],
        "巨蟹座": [(6, 22), (7, 22)],
        "獅子座": [(7, 23), (8, 22)],
        "處女座": [(8, 23), (9, 22)],
        "天秤座": [(9, 23), (10, 23)],
        "天蠍座": [(10, 24), (11, 22)],
        "射手座": [(11, 23), (12, 21)],
    }

    invalid_rows = []

    for idx, row in df.iterrows():
        month = row.get("birth_month")
        day = row.get("birth_day")
        zodiac = row.get("zodiac")

        # 檢查是否有缺失值
        if pd.isna(month) or pd.isna(day) or pd.isna(zodiac):
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "缺失值 Missing values",
                    "month": month,
                    "day": day,
                    "zodiac": zodiac,
                    "expected_zodiac": "N/A",
                }
            )
            continue

        # 轉換為整數
        try:
            month = int(month)
            day = int(day)
        except (ValueError, TypeError):
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "月份或日期格式錯誤 Month or day format error",
                    "month": month,
                    "day": day,
                    "zodiac": zodiac,
                    "expected_zodiac": "N/A",
                }
            )
            continue

        # 檢查月份和日期是否在有效範圍內
        if not (1 <= month <= 12) or not (1 <= day <= 31):
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "月份或日期超出範圍 Month or day out of range",
                    "month": month,
                    "day": day,
                    "zodiac": zodiac,
                    "expected_zodiac": "N/A",
                }
            )
            continue

        # 根據月份和日期判斷正確的星座
        correct_zodiac = None
        for sign, [
            (start_month, start_day),
            (end_month, end_day),
        ] in zodiac_ranges.items():
            # 處理跨年的摩羯座
            if sign == "摩羯座":
                if (month == 12 and day >= start_day) or (
                    month == 1 and day <= end_day
                ):
                    correct_zodiac = sign
                    break
            # 處理一般星座
            elif start_month == month and day >= start_day:
                correct_zodiac = sign
                break
            elif end_month == month and day <= end_day:
                correct_zodiac = sign
                break

        # 如果星座不匹配，加入不合理列表
        if correct_zodiac != zodiac:
            invalid_rows.append(
                {
                    "index": idx,
                    "reason": "星座與出生日期不匹配 Zodiac mismatch",
                    "month": month,
                    "day": day,
                    "zodiac": zodiac,
                    "expected_zodiac": correct_zodiac,
                }
            )

    return pd.DataFrame(invalid_rows)


def check_nationality_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    檢查 nationality_code 和 nationality 的一致性

    參數:
    df (DataFrame): 包含 nationality_code 和 nationality 欄位的資料框

    返回:
    DataFrame: 包含不一致紀錄的資料列索引、原始值和中英文原因
    """
    invalid_rows = []

    for idx, row in df.iterrows():
        nat_code = row.get("nationality_code")
        nationality = row.get("nationality")

        # 情況1: 國籍代碼為空但國籍不是中華民國
        if pd.isna(nat_code) and not pd.isna(nationality) and nationality != "中華民國":
            invalid_rows.append(
                {
                    "index": idx,
                    "nationality_code": nat_code,
                    "nationality": nationality,
                    "reason": "國籍代碼缺失但國籍非中華民國 (Missing nationality_code for non-ROC)",
                }
            )

        # 情況2: 國籍代碼非空但國籍是中華民國
        elif (
            not pd.isna(nat_code)
            and not pd.isna(nationality)
            and nationality == "中華民國"
        ):
            invalid_rows.append(
                {
                    "index": idx,
                    "nationality_code": nat_code,
                    "nationality": nationality,
                    "reason": "中華民國國籍不應有國籍代碼 (ROC nationality should not have nationality code)",
                }
            )

        # 情況3: 國籍為空但國籍代碼不為空
        elif not pd.isna(nat_code) and pd.isna(nationality):
            invalid_rows.append(
                {
                    "index": idx,
                    "nationality_code": nat_code,
                    "nationality": nationality,
                    "reason": "國籍缺失但有國籍代碼 (Missing nationality for code)",
                }
            )

        # 情況4: 國籍和國籍代碼都是空的
        elif pd.isna(nat_code) and pd.isna(nationality):
            invalid_rows.append(
                {
                    "index": idx,
                    "nationality_code": nat_code,
                    "nationality": nationality,
                    "reason": "國籍和國籍代碼皆缺失 (Both nationality_code and nationality are missing)",
                }
            )

    return pd.DataFrame(invalid_rows)


def check_university_consistency(df):
    """
    檢查大學代碼與名稱是否一致

    參數:
    df (DataFrame): 包含 university_code 和 university 欄位的資料框

    返回:
    DataFrame: 包含不一致記錄的資料框
    """
    invalid_rows = []

    for idx, row in df.iterrows():
        uni_code = row.get("university_code")
        uni_code = uni_code if pd.isna(uni_code) else str(uni_code).zfill(3)
        uni_name = row.get("university")

        # 檢查是否有缺失值
        if pd.isna(uni_code) or pd.isna(uni_name):
            invalid_rows.append(
                {
                    "index": idx,
                    "university_code": uni_code,
                    "university": uni_name,
                    "reason": "大學代碼或名稱缺失 (Missing university code or name)",
                }
            )
            continue

        # 檢查大學代碼與名稱是否匹配
        if UNIVERSITY_DICT.get(uni_code) != uni_name:
            expected_uni_name = UNIVERSITY_DICT.get(uni_code, "未知大學")
            invalid_rows.append(
                {
                    "index": idx,
                    "university_code": uni_code,
                    "university": uni_name,
                    "reason": f"大學代碼與名稱不符，大學代碼應對應 {expected_uni_name} (University code and name mismatch)",
                }
            )

    return pd.DataFrame(invalid_rows)


def check_college_consistency(df):
    """
    檢查學院代碼與名稱是否一致

    參數:
    df (DataFrame): 包含 college_code 和 college 欄位的資料框

    返回:
    DataFrame: 包含不一致記錄的資料框
    """
    invalid_rows = []

    for idx, row in df.iterrows():
        col_code = str(row.get("college_code"))
        col_name = row.get("college")

        # 檢查是否有缺失值
        if pd.isna(col_code) or pd.isna(col_name):
            invalid_rows.append(
                {
                    "index": idx,
                    "college_code": col_code,
                    "college": col_name,
                    "reason": "學院代碼或名稱缺失 (Missing college code or name)",
                }
            )
            continue

        # 檢查學院代碼與名稱是否匹配
        if COLLEGE_DICT.get(col_code) != col_name:
            expected_col_name = COLLEGE_DICT.get(col_code, "未知學院")
            invalid_rows.append(
                {
                    "index": idx,
                    "college_code": col_code,
                    "college": col_name,
                    "reason": f"學院代碼與名稱不符，學院代碼應對應 {expected_col_name} (College code and name mismatch)",
                }
            )

    return pd.DataFrame(invalid_rows)


def check_department_consistency(df):
    """
    檢查系所代碼與名稱是否一致

    參數:
    df (DataFrame): 包含 department_code 和 department_name 欄位的資料框

    返回:
    DataFrame: 包含不一致記錄的資料框
    """
    invalid_rows = []

    for idx, row in df.iterrows():
        dept_code = str(row.get("department_code"))
        dept_name = row.get("department_name")

        # 檢查是否有缺失值
        if pd.isna(dept_code) or pd.isna(dept_name):
            invalid_rows.append(
                {
                    "index": idx,
                    "department_code": dept_code,
                    "department_name": dept_name,
                    "reason": "系所代碼或名稱缺失 (Missing department code or name)",
                }
            )
            continue

        # 檢查系所代碼與名稱是否匹配
        if DEPARTMENT_DICT.get(dept_code) != dept_name:
            expected_dept_name = DEPARTMENT_DICT.get(dept_code, "未知系所")
            invalid_rows.append(
                {
                    "index": idx,
                    "department_code": dept_code,
                    "department_name": dept_name,
                    "reason": f"系所代碼與名稱不符，系所代碼應對應 {expected_dept_name} (Department code and name mismatch)",
                }
            )

    return pd.DataFrame(invalid_rows)


def check_university_college_relationship(df):
    """
    檢查大學與學院的從屬關係是否正確

    參數:
    df (DataFrame): 包含 university_code 和 college_code 欄位的資料框

    返回:
    DataFrame: 包含不正確從屬關係的記錄資料框
    """
    invalid_rows = []

    for idx, row in df.iterrows():
        uni_code = row.get("university_code")
        uni_code = uni_code if pd.isna(uni_code) else str(uni_code).zfill(3)
        col_code = str(row.get("college_code"))

        # 檢查是否有缺失值
        if pd.isna(uni_code) or pd.isna(col_code):
            invalid_rows.append(
                {
                    "index": idx,
                    "university_code": uni_code,
                    "college_code": col_code,
                    "reason": "大學代碼或學院代碼缺失 (Missing university or college code)",
                }
            )
            continue

        # 檢查大學與學院關係是否正確
        if uni_code in UNIVERSITY_COLLEGE_COMPARATION_DICT:
            if col_code not in UNIVERSITY_COLLEGE_COMPARATION_DICT[uni_code]:
                invalid_rows.append(
                    {
                        "index": idx,
                        "university_code": uni_code,
                        "college_code": col_code,
                        "reason": f"學院 {col_code} 不屬於大學 {uni_code} (College does not belong to university)",
                    }
                )

    return pd.DataFrame(invalid_rows)


def check_college_department_relationship(df):
    """
    檢查學院與系所的從屬關係是否正確

    參數:
    df (DataFrame): 包含 college_code 和 department_code 欄位的資料框

    返回:
    DataFrame: 包含不正確從屬關係的記錄資料框
    """
    invalid_rows = []

    for idx, row in df.iterrows():
        col_code = str(row.get("college_code"))
        dept_code = str(row.get("department_code"))

        # 檢查是否有缺失值
        if pd.isna(col_code) or pd.isna(dept_code):
            invalid_rows.append(
                {
                    "index": idx,
                    "college_code": col_code,
                    "department_code": dept_code,
                    "reason": "學院代碼或系所代碼缺失 (Missing college or department code)",
                }
            )
            continue

        # 檢查學院與系所關係是否正確
        if col_code in COLLEGE_DEPARTMENT_COMPARATION_DICT:
            if dept_code not in COLLEGE_DEPARTMENT_COMPARATION_DICT[col_code]:
                dept_code_map = (
                    dept_code if dept_code in DEPARTMENT_DICT.keys() else "未知編號"
                )
                invalid_rows.append(
                    {
                        "index": idx,
                        "college_code": col_code,
                        "department_code": dept_code,
                        "reason": f"系所 {dept_code_map} 不屬於該學院 (Department does not belong to college)",
                    }
                )

    return pd.DataFrame(invalid_rows)


def check_invalid(
    df: pd.DataFrame,
    invalid_types: list[str] = [
        "birthday",
        "zodiac",
        "university",
        "college",
        "department",
        "nationality",
    ],
) -> None:
    """
    檢查資料集中的不合理紀錄

    參數:
    df (DataFrame) 包含必要欄位的資料框
    invalid_type (list[str]): 要檢查的類型，預設為全部

    返回:
    無
    """
    # 定義所有檢查的配置
    check_configs = {
        "birthday": {
            "function": check_invalid_dates,
            "message": "invalid birthday dates",
        },
        "zodiac": {
            "function": check_invalid_zodiacs,
            "message": "invalid zodiac signs",
        },
        "nationality": {
            "function": check_nationality_consistency,
            "message": "invalid nationalities",
        },
        "university": {
            "function": check_university_consistency,
            "message": "invalid universities",
        },
        "college": {
            "function": check_college_consistency,
            "message": "invalid colleges",
        },
        "department": {
            "function": check_department_consistency,
            "message": "invalid departments",
        },
        "university_college": {
            "function": check_university_college_relationship,
            "message": "invalid university-college relationships",
        },
        "college_department": {
            "function": check_college_department_relationship,
            "message": "invalid college-department relationships",
        },
    }

    # 定義檢查的依賴關係（如果依賴的檢查被選擇，相關檢查也應該被執行）
    dependencies = {
        "college": ["university_college"],
        "department": ["college_department"],
    }

    # 擴展檢查類型以包含依賴關係
    expanded_types = set(invalid_types)
    for check_type in invalid_types:
        if check_type in dependencies:
            expanded_types.update(dependencies[check_type])

    invalid_results = {}
    invalid_nrows = 0
    invalid_indices = set()

    # 執行每種檢查
    for check_type in expanded_types:
        if check_type not in check_configs:
            print(f"Warning: Unknown check type '{check_type}'")
            continue

        config = check_configs[check_type]

        # 執行檢查
        result = config["function"](df)
        invalid_n = result.shape[0]
        invalid_nrows += invalid_n

        # 更新索引集合
        if invalid_n > 0:
            invalid_indices.update(result["index"].tolist())

        # 儲存結果
        invalid_results[check_type] = result

        # 輸出結果
        if invalid_n > 0:
            print(f"# {invalid_n} {config['message']} found\n")
            print(result.head(5))
            print("")
            print("Counts by reason:")
            pprint(result.groupby("reason")["index"].count().sort_index())
            print("")
        else:
            print(f"# No {config['message']} found\n")

    print(f"Total invalid records: {invalid_nrows}")
    print(f"Unique invalid records: {len(invalid_indices)}")
