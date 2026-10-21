# Demo Streamlit – Gom cụm quốc gia (Đề tài 15)

Ứng dụng đọc kết quả K-Means (K=3) trên 167 quốc gia và cho phép:
1. Chọn quốc gia → xem thuộc cụm nào, các chỉ số, vị trí trên bản đồ.
2. So sánh quốc gia với trung bình cụm.
3. Chọn cụm → danh sách quốc gia và đặc điểm chung.
4. Xem kết quả phân cụm: biểu đồ PCA 2D và bảng đánh giá.

## Cấu trúc thư mục (đặt cùng một thư mục)
```
app.py
requirements.txt
country_clustered.csv
cluster_evaluation_kmeans.csv
cluster_evaluation_ward.csv
cluster_sensitivity.csv
elbow_inertia.png
cluster_metrics_by_k.png
```

## Cách chạy
```
pip install -r requirements.txt
streamlit run app.py
```
Trình duyệt tự mở tại http://localhost:8501. Python 3.9 trở lên.

## Lưu ý
- Màu và tên cụm lấy từ cột `cluster_name` của `country_clustered.csv`
  (không dùng cột `cluster` vì số thứ tự gốc của K-Means không trùng tên cụm trong báo cáo).
- Dữ liệu: Unsupervised Learning on Country Data (HELP International).

LINK: https://countryclussteringdemo-lzvxvrbetqdyjv9oimq3w2.streamlit.app/
