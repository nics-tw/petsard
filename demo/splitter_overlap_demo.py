#!/usr/bin/env python3
"""
Splitter Overlap Control Demo
演示 Splitter 重疊控制功能

這個示例展示了如何使用改進的 Splitter 功能：
1. 控制樣本之間的重疊百分比
2. 追蹤訓練資料的原始索引
3. 函數化編程方式返回結果
"""

import pandas as pd

from petsard.loader.splitter import Splitter


def main():
    print("=== Splitter 重疊控制功能演示 ===\n")

    # 創建示例資料
    data = pd.DataFrame(
        {
            "feature_1": range(50),
            "feature_2": [f"item_{i}" for i in range(50)],
            "target": [i % 3 for i in range(50)],
        }
    )

    print(f"原始資料大小: {len(data)} 行")
    print(f"資料預覽:\n{data.head()}\n")

    # 示例 1: 嚴格重疊控制
    print("=== 示例 1: 嚴格重疊控制 (最大重疊 10%) ===")
    splitter_strict = Splitter(
        num_samples=2,
        train_split_ratio=0.2,
        max_overlap_ratio=0.1,  # 最大重疊 10%
        random_state=42,
    )

    try:
        split_data, metadata, train_indices = splitter_strict.split(data=data)

        print(f"成功生成 {len(split_data)} 個樣本")
        print("訓練索引:")
        for i, indices in enumerate(train_indices):
            indices_list = list(indices)
            print(f"  樣本 {i + 1}: {len(indices_list)} 個索引 - {indices_list[:5]}...")

        # 檢查重疊情況
        print("\n重疊分析:")
        for i in range(len(train_indices)):
            for j in range(i + 1, len(train_indices)):
                overlap = len(train_indices[i].intersection(train_indices[j]))
                overlap_pct = overlap / len(train_indices[i]) * 100
                print(
                    f"  樣本 {i + 1} vs 樣本 {j + 1}: {overlap} 個重疊索引 ({overlap_pct:.1f}%)"
                )

    except Exception as e:
        print(f"嚴格重疊控制失敗: {e}")

    print("\n" + "=" * 60 + "\n")

    # 示例 2: 寬鬆重疊控制
    print("=== 示例 2: 寬鬆重疊控制 (最大重疊 30%) ===")
    splitter_loose = Splitter(
        num_samples=3,
        train_split_ratio=0.3,
        max_overlap_ratio=0.3,  # 最大重疊 30%
        random_state=42,
    )

    split_data, metadata, train_indices = splitter_loose.split(data=data)

    print(f"成功生成 {len(split_data)} 個樣本")
    print("每個樣本的資料大小:")
    for sample_id, sample_data in split_data.items():
        train_size = len(sample_data["train"])
        val_size = len(sample_data["validation"])
        print(f"  樣本 {sample_id}: 訓練集 {train_size} 行, 驗證集 {val_size} 行")

    print("\n重疊分析:")
    for i in range(len(train_indices)):
        for j in range(i + 1, len(train_indices)):
            overlap = len(train_indices[i].intersection(train_indices[j]))
            overlap_pct = overlap / len(train_indices[i]) * 100
            print(
                f"  樣本 {i + 1} vs 樣本 {j + 1}: {overlap} 個重疊索引 ({overlap_pct:.1f}%)"
            )

    print("\n" + "=" * 60 + "\n")

    # 示例 3: 使用 exist_train_indices 功能
    print("=== 示例 3: 使用 exist_train_indices 避免與現有樣本重疊 ===")

    # 假設我們已經有一些現有的樣本索引
    existing_indices = [
        set(range(0, 10)),  # 第一個現有樣本
        set(range(15, 25)),  # 第二個現有樣本
    ]

    splitter_exclude = Splitter(
        num_samples=2,
        train_split_ratio=0.2,
        max_overlap_ratio=0.3,  # 與現有樣本最大重疊 30%
        random_state=42,
    )

    split_data, metadata, train_indices = splitter_exclude.split(
        data=data, exist_train_indices=existing_indices
    )

    print(f"成功生成 {len(split_data)} 個新樣本")
    print("與現有樣本的重疊分析:")

    for i, indices in enumerate(train_indices):
        print(f"\n  新樣本 {i + 1} ({len(indices)} 個索引):")
        for j, existing_set in enumerate(existing_indices):
            overlap = len(indices.intersection(existing_set))
            overlap_pct = overlap / len(indices) * 100
            print(f"    vs 現有樣本 {j + 1}: {overlap} 個重疊索引 ({overlap_pct:.1f}%)")

    print("\n" + "=" * 60 + "\n")

    # 示例 4: 函數化編程 - 不依賴物件狀態
    print("=== 示例 4: 函數化編程方式 ===")

    def create_splits_functional(data, num_samples=2, overlap_pct=0.15):
        """函數化方式創建分割，不依賴物件狀態"""
        splitter = Splitter(
            num_samples=num_samples,
            train_split_ratio=0.3,
            max_overlap_ratio=overlap_pct,
            random_state=42,
        )

        # 直接返回結果，不存儲在物件中
        return splitter.split(data=data)

    # 使用函數化方式
    splits, meta, indices = create_splits_functional(
        data, num_samples=3, overlap_pct=0.2
    )

    print(f"函數化方式成功創建 {len(splits)} 個分割")
    print("返回的結果類型:")
    print(f"  splits: {type(splits)} (包含 {len(splits)} 個樣本)")
    print(f"  metadata: {type(meta)} (包含 {len(meta)} 個樣本的元資料)")
    print(f"  indices: {type(indices)} (包含 {len(indices)} 個索引集合)")

    # 顯示分割資訊
    sample_data = list(splits.values())[0]
    train_size = len(sample_data["train"])
    val_size = len(sample_data["validation"])
    print(f"  分割資訊: 訓練集 {train_size} 行, 驗證集 {val_size} 行")

    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()
