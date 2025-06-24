from datetime import datetime, timedelta

import numpy as np
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

ADMISSION_TYPE_DICT = {
    "01": "學士班 (指考分發/聯考)",
    "03": "學士班 (指考分發-外加名額)",
    "12": "學士班轉學 (大二)",
    "13": "學士班轉學 (大三)",
    "14": "學士班台聯大轉校 (大二)",
    "31": "學士班僑生 (海聯會-聯合分發)",
    "32": "學士班體育績優生 (甄試)",
    "33": "學士班身心障礙生甄試",
    "35": "派外人員子女返國入學",
    "37": "學士班體育績優生(外加-甄審)",
    "38": "學士班績優推薦",
    "39": "學士班僑生 (海聯會-個人申請)",
    "46": "繁星推薦",
    "48": "四技二專推薦 (甄選) 入學",
    "51": "學士班申請入學",
    "53": "學士班申請入學(外加)",
    "55": "學士班外籍生申請",
    "58": "學士班申請入學(向日葵計劃)",
    "5D": "學士班 (大陸地區聯合招生)",
}
ADMISSION_TYPE_PROB = [
    0.30,  # 01: 學士班 (指考分發/聯考)
    0.01,  # 03: 學士班 (指考分發-外加名額)
    0.025,  # 12: 學士班轉學 (大二)
    0.005,  # 13: 學士班轉學 (大三)
    0.01,  # 14: 學士班台聯大轉校 (大二)
    0.015,  # 31: 學士班僑生 (海聯會-聯合分發)
    0.002,  # 32: 學士班體育績優生 (甄試)
    0.01,  # 33: 學士班身心障礙生甄試
    0.005,  # 35: 派外人員子女返國入學
    0.002,  # 37: 學士班體育績優生(外加-甄審)
    0.003,  # 38: 學士班績優推薦
    0.015,  # 39: 學士班僑生 (海聯會-個人申請)
    0.05,  # 46: 繁星推薦
    0.008,  # 48: 四技二專推薦 (甄選) 入學
    0.47,  # 51: 學士班申請入學
    0.02,  # 53: 學士班申請入學(外加)
    0.02,  # 55: 學士班外籍生申請
    0.01,  # 58: 學士班申請入學(向日葵計劃)
    0.02,  # 5D: 學士班 (大陸地區聯合招生)
]

ADMISSION_SPECIAL_IDENTITY_LIST = ["轉學", "其他方式", "體育績優", "學士班績優"]
ADMISSION_SPECIAL_IDENTITY_PROB = [0.1, 0.897, 0.002, 0.001]

NORMAL_ADMISSION_TYPE_LIST = [
    "01",  # 01: 學士班 (指考分發/聯考)
    "46",  # 46: 繁星推薦
    "48",  # 48: 四技二專推薦 (甄選) 入學
    "51",  # 51: 學士班申請入學
    "58",  # 58: 學士班申請入學(向日葵計劃)
]
NORMAL_ADMISSION_TYPE_PROB = [
    0.3,  # 01: 學士班 (指考分發/聯考)
    0.2,  # 46: 繁星推薦
    0.04,  # 48: 四技二專推薦 (甄選) 入學
    0.45,  # 51: 學士班申請入學
    0.01,  # 58: 學士班申請入學(向日葵計劃)
]

DISABLED_TYPE_DICT = {
    "0": "無身心障礙",
    "1": "有身心障礙",
}
DISABLED_TYPE_PROB = [
    0.95,  # 無身心障礙
    0.05,  # 有身心障礙
]

FOREIGN_NATIONALITY_DICT = {
    "005": "緬甸",
    "006": "柬埔寨",
    "008": "印度",
    "009": "印尼",
    "010": "伊朗",
    "013": "日本",
    "014": "約旦",
    "015": "南韓",
    "017": "寮國",
    "018": "黎巴嫩",
    "019": "馬來西亞",
    "024": "菲律賓",
    "026": "沙烏地阿拉伯",
    "027": "新加坡",
    "030": "泰國",
    "033": "越南",
    "050": "汶萊",
    "060": "香港",
    "070": "澳門",
    "101": "澳大利亞",
    "102": "斐濟",
    "104": "紐西蘭",
    "105": "巴布亞紐幾內亞",
    "112": "帛琉",
    "113": "馬紹爾群島共和國",
    "226": "馬達加斯加",
    "230": "模里西斯",
    "234": "奈及利亞",
    "241": "南非",
    "256": "納米比亞",
    "260": "史瓦帝尼王國",
    "304": "比利時",
    "310": "法國",
    "313": "匈牙利",
    "315": "愛爾蘭",
    "316": "義大利",
    "321": "荷蘭",
    "322": "挪威",
    "323": "波蘭",
    "324": "葡萄牙",
    "327": "西班牙",
    "330": "英國",
    "332": "德國",
    "403": "加拿大",
    "404": "哥斯大黎加",
    "406": "多明尼加",
    "407": "薩爾瓦多",
    "409": "瓜地馬拉",
    "411": "宏都拉斯",
    "413": "墨西哥",
    "414": "尼加拉瓜",
    "415": "巴拿馬",
    "418": "貝里斯",
    "425": "美國",
    "501": "阿根廷",
    "502": "玻利維亞",
    "503": "巴西",
    "504": "智利",
    "505": "哥倫比亞",
    "506": "厄瓜多",
    "508": "巴拉圭",
    "509": "秘魯",
    "512": "委內瑞拉",
    "A00": "中國大陸",
}
FOREIGN_NATIONALITY_PROB = [
    0.031,  # 005: 緬甸
    0.068,  # 006: 柬埔寨
    0.023,  # 008: 印度
    0.023,  # 009: 印尼
    0.008,  # 010: 伊朗
    0.047,  # 013: 日本
    0.008,  # 014: 約旦
    0.032,  # 015: 南韓
    0.016,  # 017: 寮國
    0.008,  # 018: 黎巴嫩
    0.075,  # 019: 馬來西亞
    0.008,  # 024: 菲律賓
    0.003,  # 026: 沙烏地阿拉伯
    0.005,  # 027: 新加坡
    0.008,  # 030: 泰國
    0.008,  # 033: 越南
    0.002,  # 050: 汶萊
    0.045,  # 060: 香港
    0.038,  # 070: 澳門
    0.008,  # 101: 澳大利亞
    0.001,  # 102: 斐濟
    0.008,  # 104: 紐西蘭
    0.001,  # 105: 巴布亞紐幾內亞
    0.001,  # 112: 帛琉
    0.001,  # 113: 馬紹爾群島共和國
    0.001,  # 226: 馬達加斯加
    0.001,  # 230: 模里西斯
    0.003,  # 234: 奈及利亞
    0.008,  # 241: 南非
    0.001,  # 256: 納米比亞
    0.001,  # 260: 史瓦帝尼王國
    0.008,  # 304: 比利時
    0.008,  # 310: 法國
    0.008,  # 313: 匈牙利
    0.008,  # 315: 愛爾蘭
    0.008,  # 316: 義大利
    0.008,  # 321: 荷蘭
    0.003,  # 322: 挪威
    0.008,  # 323: 波蘭
    0.005,  # 324: 葡萄牙
    0.005,  # 327: 西班牙
    0.008,  # 330: 英國
    0.008,  # 332: 德國
    0.075,  # 403: 加拿大
    0.008,  # 404: 哥斯大黎加
    0.008,  # 406: 多明尼加
    0.008,  # 407: 薩爾瓦多
    0.008,  # 409: 瓜地馬拉
    0.008,  # 411: 宏都拉斯
    0.008,  # 413: 墨西哥
    0.008,  # 414: 尼加拉瓜
    0.008,  # 415: 巴拿馬
    0.008,  # 418: 貝里斯
    0.151,  # 425: 美國
    0.008,  # 501: 阿根廷
    0.008,  # 502: 玻利維亞
    0.008,  # 503: 巴西
    0.008,  # 504: 智利
    0.008,  # 505: 哥倫比亞
    0.008,  # 506: 厄瓜多
    0.016,  # 508: 巴拉圭
    0.007,  # 509: 秘魯
    0.008,  # 512: 委內瑞拉
    0.047,  # A00: 中國大陸
]

IDENTITY_DICT = {
    "1": "一般生",
    "2": "一般生 (身障生)",
    "3": "一般生 (離島生)",
    "10": "僑生",
    "30": "原住民",
    "31": "原住民 (阿美族)",
    "32": "原住民 (泰雅族)",
    "33": "原住民 (排灣族)",
    "34": "原住民 (布農族)",
    "35": "原住民 (卑南族)",
    "38": "原住民 (賽夏族)",
    "40": "境外生 (不含僑生)",
    "51": "派外工作人員子女",
    "61": "蒙藏生",
}
IDENTITY_PROB = [
    0.8,  # 1: 一般生
    0.015,  # 2: 一般生 (身障生)
    0.015,  # 3: 一般生 (離島生)
    0.05,  # 10: 僑生
    0.025,  # 30: 原住民
    0.01,  # 31: 原住民 (阿美族)
    0.005,  # 32: 原住民 (泰雅族)
    0.004,  # 33: 原住民 (排灣族)
    0.005,  # 34: 原住民 (布農族)
    0.004,  # 35: 原住民 (卑南族)
    0.002,  # 38: 原住民 (賽夏族)
    0.05,  # 40: 境外生 (不含僑生)
    0.01,  # 51: 派外工作人員子女
    0.005,  # 61: 蒙藏生
]

SEX_LIST = ["女", "男"]

UNIVERSITY_LIST = list(UNIVERSITY_DICT.keys())
DISABLED_TYPE_LIST = list(DISABLED_TYPE_DICT.keys())
IDENTITY_LIST = list(IDENTITY_DICT.keys())
FOREIGN_NATIONALITY_LIST = list(FOREIGN_NATIONALITY_DICT.keys())


def get_sun_sign(date) -> str:
    """
    根據 datetime 物件判斷太陽星座

    參數:
        date (datetime): 包含年月日的 datetime 物件

    返回:
        str: 太陽星座名稱
    """
    month = date.month
    day = date.day

    # 星座日期範圍和對應名稱
    zodiac_dates = [
        ((1, 20), (2, 18), "水瓶座"),  # 水瓶座: 1/20 - 2/18
        ((2, 19), (3, 20), "雙魚座"),  # 雙魚座: 2/19 - 3/20
        ((3, 21), (4, 19), "牡羊座"),  # 牡羊座: 3/21 - 4/19
        ((4, 20), (5, 20), "金牛座"),  # 金牛座: 4/20 - 5/20
        ((5, 21), (6, 21), "雙子座"),  # 雙子座: 5/21 - 6/21
        ((6, 22), (7, 22), "巨蟹座"),  # 巨蟹座: 6/22 - 7/22
        ((7, 23), (8, 22), "獅子座"),  # 獅子座: 7/23 - 8/22
        ((8, 23), (9, 22), "處女座"),  # 處女座: 8/23 - 9/22
        ((9, 23), (10, 23), "天秤座"),  # 天秤座: 9/23 - 10/23
        ((10, 24), (11, 22), "天蠍座"),  # 天蠍座: 10/24 - 11/22
        ((11, 23), (12, 21), "射手座"),  # 射手座: 11/23 - 12/21
        ((12, 22), (1, 19), "摩羯座"),  # 摩羯座: 12/22 - 1/19
    ]

    # 特殊處理摩羯座（跨年）
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "摩羯座"

    # 查找對應的星座
    for start, end, sign in zodiac_dates:
        if (month > start[0] or (month == start[0] and day >= start[1])) and (
            month < end[0] or (month == end[0] and day <= end[1])
        ):
            return sign

    # 不太可能到達這裡，除非日期不合法
    return "日期不合法"


def get_disabled_code(identity_code) -> str:
    # 如果身份為 2: 一般生 (身障生)，則必為身心障礙
    # 但 10: 僑生、40: 境外生 (不含僑生) 亦有機會身心障礙
    return (
        "1"
        if identity_code == "2"
        # 1: 有身心障礙 <=> 2: 一般生 (身障生)
        else np.random.choice(DISABLED_TYPE_LIST, p=DISABLED_TYPE_PROB)
        if identity_code in ["10", "40"]
        # 10: 僑生、40: 境外生 (不含僑生) 抽選
        else "0"  # 0: 無身心障礙
    )


def get_foreign_nationality_code(identity_code) -> str:
    # 再來按比例抽選國籍
    return (
        np.random.choice(
            FOREIGN_NATIONALITY_LIST,
            p=FOREIGN_NATIONALITY_PROB,
        )
        if identity_code in ["10", "40"]
        # 10: 僑生、40: 境外生 (不含僑生) 抽選
        else ""  # Taiwan
    )


def update_identity_code(identity_code, foreign_nationality_code) -> str:
    # 如果抽到港澳生，則必為僑生，回過頭來改變身份
    return (
        "10"
        if foreign_nationality_code
        in ["060", "070"]  # 10: 僑生 <=> 060: 香港、070: 澳門
        else identity_code
    )


def get_admission_type_code(identity_code) -> str:
    # 先抽轉學、體育績優、或學士班績優，這三種可以有各種身份
    # 但一定要是台灣人
    return (
        "其他方式"
        if identity_code != ""
        else np.random.choice(
            ADMISSION_SPECIAL_IDENTITY_LIST,
            p=ADMISSION_SPECIAL_IDENTITY_PROB,
        )
    )


def update_admission_type_code(
    admission_type_code, identity_code, foreign_nationality_code
) -> str:
    return (
        # 32: 學士班體育績優生 (甄試) / 37: 學士班體育績優生(外加-甄審)：體育績優不變，不論身份
        "32"
        if admission_type_code == "體育績優"
        else "38"
        if admission_type_code == "學士班績優"
        # 38: 學士班績優推薦：學士班績優不變，不論身份
        # 12: 學士班轉學 (大二) / 13: 學士班轉學 (大三) / 14: 學士班台聯大轉校 (大二)
        else np.random.choice(["12", "13", "14"])
        if admission_type_code == "轉學"
        # 轉學
        # 31: 學士班僑生 (海聯會-聯合分發) / 39: 學士班僑生 (海聯會-個人申請) <=> 10: 僑生
        else (
            np.random.choice(["31", "39"])
            if identity_code == "10"
            else "33"
            if identity_code == "2"
            # 33: 學士班身心障礙生甄試 <=> 2: 一般生 (身障生)
            else "35"
            if identity_code == "51"
            # 35: 派外人員子女返國入學 <=> 51: 派外工作人員子女
            else "5D"
            if foreign_nationality_code == "A00"
            # 5D: 學士班 (大陸地區聯合招生) <=> A00: 中國大陸
            else "55"
            if identity_code == "40"
            # 非中國大陸的 55: 學士班外籍生申請 <=> 40: 境外生 (不含僑生)
            # 3: 一般生 (離島生) / 30: 原住民 / 31: 原住民 (阿美族) / 32: 原住民 (泰雅族) / 33: 原住民 (排灣族) /
            # 34: 原住民 (布農族) / 35: 原住民 (卑南族) / 38: 原住民 (賽夏族) /
            # 51: 派外工作人員子女 / 61: 蒙藏生 <=> 03: 學士班 (指考分發-外加名額) / 53: 學士班申請入學(外加)
            else np.random.choice(
                ["3", "30", "31", "32", "33", "34", "35", "38", "51", "61"]
            )
            if identity_code in ["03", "53"]
            else np.random.choice(
                NORMAL_ADMISSION_TYPE_LIST, p=NORMAL_ADMISSION_TYPE_PROB
            )
        )
    )


if __name__ == "__main__":
    from petsard.loader.benchmarker import digest_sha256

    # 決定學生數量 (Number of students)
    n_students: int = 10000

    # 檔案名稱 (File names)
    students_filepath = "best-practices_categorical_high-cardinality.csv"

    students = []
    for i in range(n_students):
        # 生成生日：最晚為 2006-08-31，最早為其六年前
        birth_date = datetime(2006, 8, 31) - timedelta(
            days=np.random.randint(0, 365 * 6)
        )
        # 轉換為星座
        zodiac = get_sun_sign(birth_date)

        # 隨機選擇大學
        university_code = np.random.choice(UNIVERSITY_LIST)
        # 在對應學院中隨機選擇
        college_code = np.random.choice(
            UNIVERSITY_COLLEGE_COMPARATION_DICT[university_code]
        )
        # 在對應系所中隨機選擇
        department_code = np.random.choice(
            COLLEGE_DEPARTMENT_COMPARATION_DICT[college_code]
        )

        # 先抽身份
        identity_code = np.random.choice(IDENTITY_LIST, p=IDENTITY_PROB)

        # 用身份決定是否身心障礙
        disabled_code = get_disabled_code(identity_code)

        # 用身份決定是否外國國籍
        foreign_nationality_code = get_foreign_nationality_code(identity_code)

        # 用外國國籍更新身份
        identity_code = update_identity_code(identity_code, foreign_nationality_code)

        # 最後才是按邏輯計算入學類別
        # 先處理特殊的入學類別
        admission_type_code = get_admission_type_code(identity_code)
        # 再來才處理非特殊的用邏輯的問題
        admission_type_code = update_admission_type_code(
            admission_type_code,
            identity_code,
            foreign_nationality_code,
        )

        # 隨機抽選性別
        sex = np.random.choice(SEX_LIST)

        # 總結
        student = {
            "birth_year": birth_date.year,
            "birth_month": birth_date.month,
            "birth_day": birth_date.day,
            "zodiac": zodiac,
            "university_code": university_code,
            "university": UNIVERSITY_DICT[university_code],
            "college_code": college_code,
            "college": COLLEGE_DICT[college_code],
            "department_code": department_code,
            "department_name": DEPARTMENT_DICT[department_code],
            "admission_type_code": admission_type_code,
            "admission_type": ADMISSION_TYPE_DICT[admission_type_code],
            "disabled_code": disabled_code,
            "disabled_type": DISABLED_TYPE_DICT[disabled_code],
            "nationality_code": foreign_nationality_code,
            "nationality": (
                "中華民國"
                if foreign_nationality_code == ""
                else FOREIGN_NATIONALITY_DICT[foreign_nationality_code]
            ),
            "identity_code": identity_code,
            "identity": IDENTITY_DICT[identity_code],
            "sex": sex,
        }

        students.append(student)

    students = pd.DataFrame(students)
    print(students.head(3).T)

    # Save to CSV files
    students.to_csv(students_filepath, index=False)

    print(
        f"""
    SHA256: {digest_sha256(students_filepath)}
    """
    )
