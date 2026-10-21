"""Demo Streamlit – Gom cụm quốc gia (Đề tài 15, HELP International).
Chạy: streamlit run app.py   (đặt cùng thư mục với các file .csv / .png)"""
import os
import pandas as pd
import plotly.express as px
import pycountry
import streamlit as st

st.set_page_config(page_title="Gom cụm quốc gia", layout="wide")

FEATURES = ["child_mort", "exports", "health", "imports", "income",
            "life_expec", "total_fer", "gdpp", "inflation"]
LABELS = {"child_mort": "Tử vong trẻ em", "exports": "Xuất khẩu", "health": "Chi y tế",
          "imports": "Nhập khẩu", "income": "Thu nhập", "life_expec": "Tuổi thọ",
          "total_fer": "Tỷ lệ sinh", "gdpp": "GDP/người", "inflation": "Lạm phát"}
FIX = {"Brunei": "BRN", "Cape Verde": "CPV", "Congo, Dem. Rep.": "COD",
       "Congo, Rep.": "COG", "Cote d'Ivoire": "CIV", "Macedonia, FYR": "MKD",
       "Micronesia, Fed. Sts.": "FSM", "Russia": "RUS",
       "St. Vincent and the Grenadines": "VCT", "Turkey": "TUR"}


def to_iso3(name):
    if name in FIX:
        return FIX[name]
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return None


@st.cache_data
def load():
    d = pd.read_csv("country_clustered.csv")
    d["iso3"] = d["country"].map(to_iso3)
    return d


df = load()
order = sorted(df["cluster_name"].unique())          # luôn dùng cluster_name (khớp báo cáo)
COLORS = dict(zip(order, ["#d73027", "#fee08b", "#1a9850"]))
GLOBAL_MEAN, GLOBAL_STD = df[FEATURES].mean(), df[FEATURES].std()

st.title("Gom cụm quốc gia theo điều kiện kinh tế – xã hội – sức khỏe")
st.caption("K-Means (K=3) trên 167 quốc gia, dữ liệu HELP International")

tab1, tab2, tab3 = st.tabs(["🌍 Quốc gia & bản đồ", "🧩 Chọn cụm", "📊 Kết quả phân cụm"])

# ---------------- TAB 1: chọn quốc gia + so sánh với cụm ----------------
with tab1:
    countries = sorted(df["country"])
    country = st.selectbox("Chọn quốc gia", countries, index=countries.index("Vietnam"))
    sel = df[df["country"] == country]
    row = sel.iloc[0]
    mean = df[df["cluster_name"] == row["cluster_name"]][FEATURES].mean()

    fig = px.choropleth(
        df, locations="iso3", color="cluster_name", hover_name="country",
        hover_data={"iso3": False, "cluster_name": False, "child_mort": ":.1f",
                    "income": ":,.0f", "gdpp": ":,.0f", "life_expec": ":.1f"},
        color_discrete_map=COLORS, category_orders={"cluster_name": order},
        labels={**LABELS, "cluster_name": "Cụm"})
    fig.add_scattergeo(locations=sel["iso3"], mode="markers", hoverinfo="skip", showlegend=False,
                       marker=dict(size=12, color="black", symbol="circle-open", line=dict(width=3)))
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth")
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=430,
                      legend=dict(orientation="h", y=-0.05, title_text=""))
    st.plotly_chart(fig, width="stretch")

    st.subheader(f"{country} thuộc: {row['cluster_name']}")
    comp = pd.DataFrame({
        "Chỉ số": [LABELS[f] for f in FEATURES],
        "Quốc gia": row[FEATURES].astype(float).values,
        "TB cụm": mean.values,
        "Chênh lệch (%)": ((row[FEATURES].astype(float) / mean - 1) * 100).values,
    }).round(2)
    st.markdown("**So sánh quốc gia với trung bình cụm**")
    st.dataframe(comp, hide_index=True, width="stretch")
    bar = px.bar(comp, x="Chỉ số", y="Chênh lệch (%)", color="Chênh lệch (%)",
                 color_continuous_scale="RdBu_r", color_continuous_midpoint=0)
    bar.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
    st.plotly_chart(bar, width="stretch")

# ---------------- TAB 2: chọn cụm -> danh sách + đặc điểm chung ----------------
with tab2:
    cname = st.selectbox("Chọn cụm", order)
    sub = df[df["cluster_name"] == cname]
    c1, c2 = st.columns(2)
    c1.metric("Số quốc gia", len(sub))
    c2.metric("Tỷ lệ trên tổng", f"{len(sub) / len(df):.0%}")

    cm = sub[FEATURES].mean()
    z = (cm - GLOBAL_MEAN) / GLOBAL_STD
    prof = pd.DataFrame({
        "Chỉ số": [LABELS[f] for f in FEATURES],
        "TB cụm": cm.values,
        "TB toàn bộ": GLOBAL_MEAN.values,
        "Z-score cụm": z.values,
    }).round(2)
    st.markdown("**Đặc điểm chung (trung bình cụm so với toàn bộ 167 nước)**")
    st.dataframe(prof, hide_index=True, width="stretch")
    zfig = px.bar(prof, x="Z-score cụm", y="Chỉ số", orientation="h", color="Z-score cụm",
                  color_continuous_scale="RdBu_r", color_continuous_midpoint=0)
    zfig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
    st.plotly_chart(zfig, width="stretch")
    st.caption("Z-score > 0: trung bình cụm cao hơn mức chung; < 0: thấp hơn. "
               "Đây là mô tả đặc điểm, không phải quan hệ nhân quả.")

    st.markdown("**Danh sách quốc gia trong cụm**")
    st.dataframe(sub[["country"] + FEATURES].rename(columns={"country": "Quốc gia", **LABELS})
                 .sort_values("Quốc gia"), hide_index=True, width="stretch")

# ---------------- TAB 3: kết quả phân cụm ----------------
with tab3:
    st.markdown("**Biểu đồ PCA 2D**")
    pca = px.scatter(df, x="PC1", y="PC2", color="cluster_name", hover_name="country",
                     color_discrete_map=COLORS, category_orders={"cluster_name": order},
                     labels={"cluster_name": "Cụm"})
    pca.update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0),
                      legend=dict(orientation="h", y=-0.15, title_text=""))
    st.plotly_chart(pca, width="stretch")

    st.markdown("**Bảng đánh giá**")
    for title, f in [("K-Means, K = 2–6", "cluster_evaluation_kmeans.csv"),
                     ("Phân cấp (Ward), K = 2–6", "cluster_evaluation_ward.csv"),
                     ("So sánh cách tiền xử lý (K=3)", "cluster_sensitivity.csv")]:
        if os.path.exists(f):
            st.markdown(f"*{title}*")
            st.dataframe(pd.read_csv(f), hide_index=True, width="stretch")
    for cap, f in [("Elbow (Inertia theo K)", "elbow_inertia.png"),
                   ("Các chỉ số đánh giá theo K", "cluster_metrics_by_k.png")]:
        if os.path.exists(f):
            st.image(f, caption=cap)
