# 企業基本資料 (Enterprise Basic Information)
def generate_company_data(n_companies=1000):
    # 產業分類（高基數示範）(Industry Categories - High Cardinality Example)
    industry_types = {
        "製造業": ["電子零組件", "金屬加工", "紡織", "食品", "塑膠製品"],
        "服務業": ["餐飲", "物流", "教育", "休閒娛樂", "專業諮詢"],
        "批發零售": ["電子商務", "進出口貿易", "零售", "汽機車零件", "民生用品"],
        "營建工程": ["土木工程", "建築工程", "室內裝修", "機電工程", "環保工程"],
    }

    # 縣市與區域 (Cities and Districts)
    locations = {
        "臺北市": ["大安區", "信義區", "內湖區"],
        "新北市": ["板橋區", "三重區", "新莊區"],
        "桃園市": ["中壢區", "桃園區", "龜山區"],
    }

    companies = []
    for i in range(n_companies):
        industry = np.random.choice(list(industry_types.keys()))
        sub_industry = np.random.choice(industry_types[industry])
        city = np.random.choice(list(locations.keys()))
        district = np.random.choice(locations[city])

        # 生成隨機成立日期（2010-2020年間）
        # Generate random establishment date (between 2010-2020)
        established_date = datetime(2010, 1, 1) + timedelta(
            days=np.random.randint(0, 365 * 10)
        )

        company = {
            "company_id": f"C{str(i + 1).zfill(6)}",
            "industry": industry,
            "sub_industry": sub_industry,
            "city": city,
            "district": district,
            "established_date": established_date,
            "capital": np.random.randint(1000, 50000)
            * 1000,  # 資本額（以千為單位）(Capital in thousands)
        }
        companies.append(company)

    return pd.DataFrame(companies)


# 融資申請紀錄 (Financing Application Records)
def generate_application_data(companies_df, years_of_data=10):
    # 最多十年 (Maximum 10 years)
    applications = []
    # 貸款類型 (Loan Types)
    loan_types = [
        "營運週轉金",
        "購置機器設備",
        "廠房擴充",
        "創新研發",
        "數位轉型",
        "疫後紓困",
    ]

    for _, company in companies_df.iterrows():
        # 每家公司可能有0-5次申請 (Each company may have 0-5 applications)
        n_applications = np.random.randint(0, 6)
        for j in range(n_applications):
            # 以季為單位計算申請時間 (Calculate application time by quarters)
            # 最多40季 (Maximum 40 quarters)
            quarters = np.random.randint(1, years_of_data * 4)
            apply_date = company["established_date"] + timedelta(days=quarters * 90)

            # 處理天數 1-60天 (Processing period: 1-60 days)
            process_days = np.random.randint(1, 61)
            approval_date = apply_date + timedelta(days=process_days)

            # 申請狀態 (Application Status)
            status = np.random.choice(
                ["approved", "rejected", "withdrawn"], p=[0.75, 0.15, 0.10]
            )

            # 申請金額（以千為單位並轉換為實際金額）
            # (Requested amount in thousands converted to actual amount)
            amount_requested = np.random.randint(500, 20000) * 1000

            application = {
                "application_id": f"A{str(len(applications) + 1).zfill(8)}",
                "company_id": company["company_id"],
                "loan_type": np.random.choice(loan_types),
                "apply_date": apply_date,
                "approval_date": approval_date if status == "approved" else None,
                "status": status,
                "amount_requested": amount_requested,
                "amount_approved": None,
            }

            if status == "approved":
                # 核准金額為申請金額的60-100%，以千為單位四捨六入五隨機
                # (Approved amount is 60-100% of requested amount,
                # rounded to thousands with random rounding at 5)
                raw_amount = amount_requested * np.random.uniform(0.6, 1.0)
                application["amount_approved"] = int(round(raw_amount / 1000)) * 1000

            applications.append(application)

    return pd.DataFrame(applications)


# 財務追蹤紀錄 (Financial Tracking Records)
def generate_financial_tracking(companies_df, applications_df):
    tracking_records = []

    # 篩選核准的申請案 (Filter approved applications)
    approved_applications = applications_df[applications_df["status"] == "approved"]

    for _, application in approved_applications.iterrows():
        # 每季追蹤一次，追蹤4-12次 (Quarterly tracking, 4-12 times)
        n_tracking = np.random.randint(4, 13)

        for i in range(n_tracking):
            track_date = application["approval_date"] + timedelta(days=90 * i)

            # 營收與獲利（以千為單位）(Revenue and profit in thousands)
            base_revenue = np.random.randint(1000, 50000) * 1000
            growth_factor = np.random.uniform(0.8, 1.2)
            revenue = int(base_revenue * growth_factor)
            profit = int(
                revenue * np.random.uniform(-0.1, 0.2)
            )  # 可能虧損 (Possible loss)

            # 根據獲利率決定風險等級 (Determine risk level based on profit ratio)
            profit_ratio = profit / revenue

            # 獲利率分級標準 (Profit ratio thresholds)
            if profit_ratio >= 0.05:
                risk_level = "normal"  # 獲利率 >= 5%
            elif profit_ratio >= 0.02:
                risk_level = "attention"  # 獲利率 2-5%
            elif profit_ratio >= 0:
                risk_level = "warning"  # 獲利率 0-2%
            elif profit_ratio >= -0.03:
                risk_level = "high_risk"  # 獲利率 -3-0%
            elif profit_ratio >= -0.05:
                risk_level = "critical"  # 獲利率 -5--3%
            else:
                risk_level = "severe"  # 獲利率 < -5%

            tracking = {
                "track_id": f"T{str(len(tracking_records) + 1).zfill(8)}",
                "application_id": application["application_id"],
                "company_id": application["company_id"],
                "tracking_date": track_date,
                "revenue": revenue,
                "profit": profit,
                "profit_ratio": profit_ratio,
                "risk_level": risk_level,
            }

            tracking_records.append(tracking)

    return pd.DataFrame(tracking_records)


def summarize_tracking_data(tracking_df):
    """
    彙整每個申請案的財務追蹤狀況 (Summarize financial tracking status for each application)
    """

    # 將風險等級轉換為數值以計算平均 (Convert risk levels to numeric for calculation)
    risk_level_map = {
        "normal": 1,
        "attention": 2,
        "warning": 3,
        "high_risk": 4,
        "critical": 5,
        "severe": 6,
    }

    # 檢查資料欄位是否存在 (Check if columns exist)
    expected_columns = ["risk_level", "profit_ratio", "tracking_date", "revenue"]
    for col in expected_columns:
        if col not in tracking_df.columns:
            raise ValueError(
                f"欄位 '{col}' 不存在於追蹤資料中 (Column '{col}' not found in tracking data)"
            )

    tracking_df["risk_level_num"] = tracking_df["risk_level"].map(risk_level_map)

    summary = (
        tracking_df.groupby("application_id")
        .agg(
            {
                "risk_level_num": [
                    (
                        "avg_risk_3y",
                        lambda x: x.iloc[-12:].mean() if len(x) >= 12 else x.mean(),
                    ),
                    ("last_risk", "last"),
                    ("second_last_risk", lambda x: x.iloc[-2] if len(x) >= 2 else None),
                ],
                "profit_ratio": [
                    ("avg_profit_ratio", "mean"),
                    ("min_profit_ratio", "min"),
                    ("profit_ratio_std", "std"),
                    ("negative_profit_count", lambda x: (x < 0).sum()),
                ],
                "tracking_date": [
                    ("tracking_months", lambda x: (x.max() - x.min()).days / 30),
                    ("last_tracking_date", "max"),
                ],
                "revenue": [
                    ("avg_revenue", "mean"),
                    (
                        "revenue_growth",
                        lambda x: (x.iloc[-1] / x.iloc[0] - 1) if len(x) >= 2 else 0,
                    ),
                ],
            }
        )
        .reset_index()
    )

    # 將多層次欄位名稱合併 (Flatten multi-level column names)
    summary.columns = ["_".join(col).strip("_") for col in summary.columns.values]

    # 將風險等級轉回文字 (Convert risk levels back to text)
    risk_level_reverse_map = {v: k for k, v in risk_level_map.items()}
    for col in ["risk_level_num_last_risk", "risk_level_num_second_last_risk"]:
        summary[col.replace("num_", "")] = summary[col].map(risk_level_reverse_map)

    # 移除中間計算用的欄位 (Remove intermediate calculation columns)
    summary = summary.drop(columns=[col for col in summary.columns if "num_" in col])

    return summary


if __name__ == "__main__":
    from datetime import datetime, timedelta

    import numpy as np
    import pandas as pd

    from petsard.loader.benchmarker import digest_sha256

    # 決定公司數量 (Number of companies)
    company_num: int = 1000

    # 檔案名稱 (File names)
    companies_filepath = "best-practices_multi-table_companies.csv"
    applications_filepath = "best-practices_multi-table_applications.csv"
    tracking_filepath = "best-practices_multi-table_tracking.csv"

    companies = generate_company_data(company_num)
    print("\n企業基本資料前5筆 (Top 5 records of Enterprise)：\n")
    print(companies.head(5))

    applications = generate_application_data(companies)
    print("\n融資申請紀錄前5筆 (Top 5 records of Financing Application)：\n")
    print(applications.head(5))

    tracking = generate_financial_tracking(companies, applications)
    tracking = summarize_tracking_data(tracking)
    print("\n財務追蹤紀錄前5筆 (Top 5 records of Financial Tracking)：\n")
    print(tracking.head(5))

    # Save to CSV files
    companies.to_csv(companies_filepath, index=False)
    applications.to_csv(applications_filepath, index=False)
    tracking.to_csv(tracking_filepath, index=False)
    print("\nCSV files have been saved successfully.")

    print(
        f"""
    SHA256:
        - companies: {digest_sha256(companies_filepath)}
        - applications: {digest_sha256(applications_filepath)}
        - tracking: {digest_sha256(tracking_filepath)}
    """
    )
