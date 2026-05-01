import streamlit as st
import pandas as pd
from pyecharts.charts import Geo, Line, WordCloud
from pyecharts import options as opts
from pyecharts.globals import ChartType
import streamlit.components.v1 as components
import jieba
from collections import Counter

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="北京景点评价分析平台",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 强制浅色主题CSS ====================
st.markdown("""
<style>
    /* 整体背景白色 */
    .stApp, .stApp > div, .main > div, .main .block-container {
        background-color: #ffffff !important;
    }

    /* 顶部标题区域深蓝色背景 */
    .stApp header {
        background-color: #1a1a2e !important;
        padding: 10px 0 !important;
    }
    .stApp header .stDecoration {
        display: none !important;
    }

    /* 主标题红色 */
    h1 {
        color: #8B0000 !important;
        text-align: center !important;
        font-size: 2.8rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0rem !important;
    }

    /* 副标题 */
    .custom-subtitle {
        text-align: center;
        color: #ccc !important;
        margin-bottom: 0.5rem !important;
        font-size: 1rem;
    }

    /* 普通文字 */
    .stMarkdown, .stMarkdown p, .stMarkdown li {
        color: #333333 !important;
    }

    /* 标题颜色 */
    h2, h3, h4 {
        color: #8B0000 !important;
    }

    /* 按钮样式 */
    .stButton > button {
        border-radius: 20px !important;
        background-color: #8B0000 !important;
        color: white !important;
    }
    .stButton > button:hover {
        background-color: #a52a2a !important;
    }

    /* expander 样式：默认深色背景白色文字 */
    div[data-testid="stExpander"] details summary {
        background-color: #1a1a2e !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        border: none !important;
    }
    div[data-testid="stExpander"] details summary p {
        color: white !important;
        font-weight: normal !important;
    }
    div[data-testid="stExpander"] details summary:hover {
        background-color: #2a2a4e !important;
    }
    div[data-testid="stExpander"] details {
        background-color: transparent !important;
    }
    div[data-testid="stExpander"] .streamlit-expanderContent {
        background-color: #f5f5f5 !important;
        border-radius: 0 0 8px 8px !important;
        padding: 10px !important;
    }

    /* metric数据 */
    div[data-testid="stMetric"] p,
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div {
        color: #333333 !important;
    }

    /* 下拉框 */
    .stSelectbox div[data-baseweb="select"] div,
    .stSelectbox input {
        color: #333 !important;
        background-color: white !important;
    }
    .stNumberInput input, .stTextInput input {
        color: #333 !important;
        background-color: white !important;
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #555 !important;
    }

    .stCaption {
        color: #888 !important;
    }

    hr {
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 侧边栏样式 ====================
st.markdown("""
<style>
    .css-1d391kg, .css-1633bj1, [data-testid="stSidebar"] {
        background-color: #1a1a2e !important;
    }
    .stSidebar, .stSidebar .stMarkdown, .stSidebar .stMarkdown p, 
    .stSidebar .stSelectbox label, .stSidebar .stMultiSelect label,
    .stSidebar .stSlider label, .stSidebar .stRadio label,
    .stSidebar .stSidebarContent {
        color: white !important;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar .stSubheader {
        color: white !important;
    }
    .metric-card {
        background: rgba(255,255,255,0.12) !important;
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        text-align: center;
    }
    .metric-card .label {
        color: #ccc !important;
        font-size: 0.8rem;
    }
    .metric-card .value {
        color: #ffcc00 !important;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .stSidebar .stCaption {
        color: #aaa !important;
    }
    .stSidebar hr {
        border-color: #444 !important;
    }
    .stSidebar .stRadio > div {
        color: white !important;
    }
    .sidebar-header {
        text-align: center;
        padding: 10px 0;
    }
    .stSidebar .stSelectbox div[data-baseweb="select"] div {
        color: white !important;
        background-color: #2a3a4a !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 页面二报告头部样式 ====================
st.markdown("""
<style>
    .report-header {
        background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
    }
    .report-header .title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #8B0000;
    }
    .report-header .subtitle {
        font-size: 0.9rem;
        color: #666;
    }
    .ranking-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px 0;
        border-left: 4px solid #8B0000;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 标题区域 ====================
st.title("🏯 北京景点评价分析平台")
st.markdown('<p class="custom-subtitle">🎯 基于游客评论的多维度口碑可视化分析平台</p>', unsafe_allow_html=True)
st.markdown('<hr style="border: none; height: 2px; background-color: #333333; margin: 5px 0 20px 0;">',
            unsafe_allow_html=True)

# ==================== 初始化 ====================
if 'last_page' not in st.session_state:
    st.session_state['last_page'] = None


# ==================== 数据加载 ====================
@st.cache_data
def load_comments_data():
    try:
        df = pd.read_csv('comments.csv')
        return df
    except FileNotFoundError:
        st.error("未找到 comments.csv 文件")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"读取失败：{e}")
        return pd.DataFrame()


comments_df = load_comments_data()
if comments_df.empty:
    st.stop()

if 'date' in comments_df.columns:
    comments_df['date_parsed'] = pd.to_datetime(comments_df['date'], errors='coerce')
else:
    comments_df['date_parsed'] = pd.NaT

# ==================== 侧边栏 ====================
st.sidebar.markdown("""
<div class="sidebar-header">
    <div style="font-size: 3rem;">🏯</div>
    <div style="font-weight: bold; font-size: 1.2rem;">北京景点分析</div>
    <div style="font-size: 0.8rem; color: #ccc;">数据驱动 · 口碑洞察</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

spot_list = comments_df['spot_name'].unique().tolist()
selected_spot = st.sidebar.selectbox("选择景点", spot_list)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 数据洞察")

sentiment_by_spot = comments_df.groupby('spot_name').agg(
    sentiment_score=('sentiment', lambda x: (x == 'positive').mean())
).reset_index()

best_spot = sentiment_by_spot.loc[sentiment_by_spot['sentiment_score'].idxmax(), 'spot_name']
best_score = sentiment_by_spot.loc[sentiment_by_spot['sentiment_score'].idxmax(), 'sentiment_score']
worst_spot = sentiment_by_spot.loc[sentiment_by_spot['sentiment_score'].idxmin(), 'spot_name']
worst_score = sentiment_by_spot.loc[sentiment_by_spot['sentiment_score'].idxmin(), 'sentiment_score']
most_commented = comments_df['spot_name'].value_counts().index[0]
most_commented_count = comments_df['spot_name'].value_counts().values[0]
avg_positive = len(comments_df[comments_df['sentiment'] == 'positive']) / len(comments_df) * 100

st.sidebar.markdown(f"""
<div class="metric-card">
    <div class="label">🏆 好评率最高</div>
    <div class="value">{best_spot} ({best_score:.0%})</div>
</div>
<div class="metric-card">
    <div class="label">⚠️ 需要关注</div>
    <div class="value">{worst_spot} ({worst_score:.0%})</div>
</div>
<div class="metric-card">
    <div class="label">🔥 讨论最多</div>
    <div class="value">{most_commented} ({most_commented_count}条)</div>
</div>
<div class="metric-card">
    <div class="label">📊 平均好评率</div>
    <div class="value">{avg_positive:.1f}%</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 景点对比分析")
compare_spots = st.sidebar.multiselect(
    "选择要对比的景点（可多选）",
    spot_list,
    default=[spot_list[0]] if len(spot_list) > 0 else []
)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 时间范围筛选")

if 'date_parsed' in comments_df.columns and comments_df['date_parsed'].notna().any():
    valid_dates = comments_df['date_parsed'].dropna()
    min_date = valid_dates.min()
    max_date = valid_dates.max()
    start_date, end_date = st.sidebar.slider(
        "选择时间范围",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime())
    )
    date_mask = (comments_df['date_parsed'] >= pd.Timestamp(start_date)) & (
            comments_df['date_parsed'] <= pd.Timestamp(end_date))
    filtered_comments = comments_df[date_mask]
    st.sidebar.caption(f"筛选后评论数：{len(filtered_comments)} 条")
else:
    filtered_comments = comments_df
    st.sidebar.info("数据中无日期字段，显示全部数据")

st.sidebar.markdown("---")
st.sidebar.caption("数据来源：携程网游客评论")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "选择功能页面",
    ["📊 数据可视化", "📋 综合分析报告", "📄 数据详情浏览"]
)

if st.session_state['last_page'] != page:
    st.session_state['last_page'] = page
    st.rerun()


# ==================== 辅助函数 ====================
def extract_keywords(texts, topK=20):
    if not texts:
        return []
    all_text = ' '.join(texts)
    words = jieba.cut(all_text)
    stopwords = set(['的', '了', '是', '在', '我', '有', '和', '就', '不', '都', '也', '很',
                     '到', '说', '去', '来', '这', '那', '上', '下', '个', '吧', '啊', '哦',
                     '非常', '有点', '感觉', '真的', '实在', '而且', '所以', '但是', '因为'])
    words = [w for w in words if w not in stopwords and len(w) > 1]
    word_freq = Counter(words).most_common(topK)
    return word_freq


def create_wordcloud(texts, title):
    if not texts:
        return None
    word_freq = extract_keywords(texts, topK=20)
    if not word_freq:
        return None
    wordcloud = WordCloud(init_opts=opts.InitOpts(width="100%", height="400px"))
    wordcloud.add(
        series_name="关键词",
        data_pair=word_freq,
        word_size_range=[12, 50],
        shape="circle"
    )
    wordcloud.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        tooltip_opts=opts.TooltipOpts(is_show=False)
    )
    return wordcloud


def safe_render(chart, height=550):
    if chart is None:
        return
    try:
        # 生成唯一的文件名避免缓存冲突
        import uuid
        temp_file = f"temp_chart_{uuid.uuid4().hex}.html"
        chart.render(temp_file)
        with open(temp_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=height)
    except Exception as e:
        # 出错时不显示任何内容
        pass


def create_sentiment_map(comments_df):
    sentiment_by_spot = comments_df.groupby('spot_name').agg(
        sentiment_score=('sentiment', lambda x: (x == 'positive').mean())
    ).reset_index()

    all_coords = {
        '故宫博物院': [116.397, 39.918],
        '天坛公园': [116.413, 39.883],
        '颐和园': [116.273, 39.999],
        '南锣鼓巷': [116.404, 39.940],
        '圆明园': [116.296, 40.008],
        '八达岭长城': [116.010, 40.359],
    }

    geo = Geo(init_opts=opts.InitOpts(width="100%", height="500px", theme="light"))
    geo.add_schema(maptype="china", zoom=8, center=[116.4, 39.9])

    data_pairs = []
    for _, row in sentiment_by_spot.iterrows():
        name = row['spot_name']
        score = round(row['sentiment_score'], 2)
        if name in all_coords:
            geo.add_coordinate(name, all_coords[name][0], all_coords[name][1])
            data_pairs.append((name, score))
        else:
            st.warning(f"景点 '{name}' 未找到坐标，已跳过")

    if not data_pairs:
        st.error("没有可显示的景点数据")
        return None

    geo.add(
        series_name="情感得分",
        data_pair=data_pairs,
        type_=ChartType.EFFECT_SCATTER,
        symbol_size=15,
    )

    geo.set_global_opts(
        title_opts=opts.TitleOpts(title="各景点情感得分分布"),
        visualmap_opts=opts.VisualMapOpts(
            min_=0, max_=1,
            range_color=["#313695", "#4575b4", "#74add1", "#abd9e9",
                         "#e0f3f8", "#ffffbf", "#fee090", "#fdae61",
                         "#f46d43", "#d73027", "#a50026"],
            is_calculable=True
        ),
        tooltip_opts=opts.TooltipOpts(
            formatter="{b}: {c}",
            background_color="rgba(0,0,0,0.7)",
            border_color="#fff"
        )
    )
    return geo


def create_trend_chart(comments_df, spot_name):
    spot_df = comments_df[comments_df['spot_name'] == spot_name].copy()
    if spot_df.empty:
        return None
    if 'date_parsed' not in spot_df.columns:
        return None
    spot_df = spot_df.dropna(subset=['date_parsed'])
    if spot_df.empty:
        return None
    spot_df['month'] = spot_df['date_parsed'].dt.to_period('M').astype(str)
    monthly_sentiment = spot_df.groupby('month').apply(
        lambda x: (x['sentiment'] == 'positive').mean()
    ).reset_index()
    monthly_sentiment.columns = ['month', 'sentiment_score']
    line = Line(init_opts=opts.InitOpts(width="100%", height="400px"))
    line.add_xaxis(monthly_sentiment['month'].tolist())
    line.add_yaxis(
        "情感得分",
        monthly_sentiment['sentiment_score'].tolist(),
        label_opts=opts.LabelOpts(is_show=True),
        linestyle_opts=opts.LineStyleOpts(width=2, color="#d73027"),
        symbol="circle",
        symbol_size=8,
    )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title=f"{spot_name}口碑趋势分析"),
        xaxis_opts=opts.AxisOpts(name="时间"),
        yaxis_opts=opts.AxisOpts(name="情感得分", min_=0, max_=1),
        tooltip_opts=opts.TooltipOpts(trigger="axis")
    )
    return line


# ==================== 页面一：数据可视化 ====================
if page == "📊 数据可视化":
    st.subheader("🗺️ 北京景点情感分布地图")
    st.caption("💡 鼠标悬停在圆点上可查看具体情感得分")

    sentiment_map = create_sentiment_map(filtered_comments)
    safe_render(sentiment_map, 550)

    st.markdown("---")

    if len(compare_spots) >= 2:
        st.subheader("📊 景点口碑对比")
        compare_data = []
        for spot in compare_spots:
            spot_df = filtered_comments[filtered_comments['spot_name'] == spot]
            if len(spot_df) > 0:
                pos_count = len(spot_df[spot_df['sentiment'] == 'positive'])
                neg_count = len(spot_df[spot_df['sentiment'] == 'negative'])
                pos_rate = pos_count / (pos_count + neg_count) * 100 if (pos_count + neg_count) > 0 else 0
                compare_data.append({'景点': spot, '好评率(%)': round(pos_rate, 1), '评论数': len(spot_df)})

        compare_df = pd.DataFrame(compare_data)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**各景点好评率对比**")
            st.bar_chart(compare_df.set_index('景点')['好评率(%)'])
        with col2:
            st.markdown("**各景点评论数量对比**")
            st.bar_chart(compare_df.set_index('景点')['评论数'])
        st.markdown("**详细数据对比**")
        st.dataframe(compare_df, use_container_width=True)
        st.markdown("---")

    st.subheader("📈 口碑趋势分析")
    st.caption("💡 展示选定景点口碑随时间的变化趋势")

    trend_chart = create_trend_chart(filtered_comments, selected_spot)
    safe_render(trend_chart, 450)

    st.markdown("---")

    st.subheader("💬 游客心声")
    st.caption("💡 词云越大表示该关键词出现频率越高")

    spot_comments = filtered_comments[filtered_comments['spot_name'] == selected_spot]
    positive_texts = spot_comments[spot_comments['sentiment'] == 'positive']['content'].tolist()
    negative_texts = spot_comments[spot_comments['sentiment'] == 'negative']['content'].tolist()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 😊 正面评价词云")
        pos_wordcloud = create_wordcloud(positive_texts, "正面评价")
        safe_render(pos_wordcloud, 350)
        st.caption(f"共 {len(positive_texts)} 条正面评价")
    with col2:
        st.markdown("#### 😞 负面评价词云")
        neg_wordcloud = create_wordcloud(negative_texts, "负面评价")
        safe_render(neg_wordcloud, 350)
        st.caption(f"共 {len(negative_texts)} 条负面评价")

    st.subheader("🔍 关键词深入分析")
    keyword_search = st.text_input("输入关键词，查看包含该关键词的评论", placeholder="例如：壮观、人多、排队")

    if keyword_search:
        keyword_comments = spot_comments[spot_comments['content'].str.contains(keyword_search, na=False, case=False)]
        if len(keyword_comments) > 0:
            st.markdown(f"**找到 {len(keyword_comments)} 条包含「{keyword_search}」的评论：**")
            pos_keyword = len(keyword_comments[keyword_comments['sentiment'] == 'positive'])
            neg_keyword = len(keyword_comments[keyword_comments['sentiment'] == 'negative'])
            col1, col2 = st.columns(2)
            with col1:
                st.metric("正面评论", pos_keyword)
            with col2:
                st.metric("负面评论", neg_keyword)

            with st.expander("📋 点击展开查看所有相关评论"):
                for i, comment in enumerate(keyword_comments['content'].head(20), 1):
                    sentiment_emoji = "😊" if keyword_comments.iloc[i - 1]['sentiment'] == 'positive' else "😞"
                    st.write(f"{i}. {sentiment_emoji} {comment}")
        else:
            st.info(f"未找到包含「{keyword_search}」的评论")

    st.markdown("**热门关键词快速分析：**")
    hot_keywords = ['壮观', '人多', '排队', '历史', '商业化', '值得']
    hot_cols = st.columns(len(hot_keywords))
    for i, kw in enumerate(hot_keywords):
        with hot_cols[i]:
            if st.button(kw, key=f"hot_{kw}"):
                keyword_search = kw
                st.rerun()

    st.markdown("---")

    st.markdown("### 📊 分析总结")
    current_spot_sentiment = spot_comments['sentiment'].value_counts()
    if not current_spot_sentiment.empty:
        pos_cnt = current_spot_sentiment.get('positive', 0)
        neg_cnt = current_spot_sentiment.get('negative', 0)
        total = pos_cnt + neg_cnt
        if total > 0:
            pos_rate = pos_cnt / total * 100
            if pos_rate >= 70:
                sentiment_text = "好评率较高，游客整体满意度不错"
                color = "green"
            elif pos_rate >= 50:
                sentiment_text = "评价分化，需要关注具体问题"
                color = "orange"
            else:
                sentiment_text = "好评率偏低，存在较多负面反馈"
                color = "red"
            st.markdown(
                f"**{selected_spot}** 共有 {total} 条评论，正面 {pos_cnt} 条（{pos_rate:.1f}%），负面 {neg_cnt} 条（{100 - pos_rate:.1f}%）。")
            st.markdown(f"综合评价：<span style='color:{color};font-weight:bold;'>{sentiment_text}</span>",
                        unsafe_allow_html=True)

# ==================== 页面二：综合分析报告 ====================
elif page == "📋 综合分析报告":
    # 检查是否有数据
    if filtered_comments.empty:
        st.warning("当前时间范围内没有评论数据，请调整时间范围后重试。")
        st.stop()



    st.markdown("""
    <div class="report-header">
        <div class="title">📋 北京景点口碑综合分析报告</div>
        <div class="subtitle">基于游客评论数据的自动诊断分析</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 一、整体概况")
    total_comments = len(filtered_comments)
    total_positive = len(filtered_comments[filtered_comments['sentiment'] == 'positive'])
    avg_rate = total_positive / total_comments * 100 if total_comments > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总评论数", total_comments)
    with col2:
        st.metric("正面评论", total_positive)
    with col3:
        st.metric("平均好评率", f"{avg_rate:.1f}%")
    with col4:
        st.metric("覆盖景点", len(filtered_comments['spot_name'].unique()))

    st.markdown("---")
    st.markdown("## 二、各景点口碑排名")

    spot_ranking = filtered_comments.groupby('spot_name').agg(
        好评率=('sentiment', lambda x: (x == 'positive').mean() * 100),
        评论数=('content', 'count')
    ).reset_index().sort_values('好评率', ascending=False)
    spot_ranking['好评率'] = spot_ranking['好评率'].round(1)
    spot_ranking['排名'] = range(1, len(spot_ranking) + 1)

    for idx, row in spot_ranking.iterrows():
        medal = "🥇" if row['排名'] == 1 else "🥈" if row['排名'] == 2 else "🥉" if row['排名'] == 3 else f"{row['排名']}."
        star_rating = '⭐' * int(row['好评率'] / 20) if row['好评率'] >= 20 else '☆'
        color = 'green' if row['好评率'] >= 70 else 'orange' if row['好评率'] >= 50 else 'red'
        st.markdown(f"""
        <div class="ranking-card">
            <span style="font-size: 1.2rem;">{medal}</span>
            <span style="font-weight: bold; margin-left: 10px;">{row['spot_name']}</span>
            <span style="float: right;">
                <span style="color: {color};">
                    {star_rating} {row['好评率']}%
                </span>
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 三、优势与问题诊断")

    if len(spot_ranking) > 0:
        best = spot_ranking.iloc[0]
        st.markdown(f"### ✅ 口碑最佳：{best['spot_name']}")
        st.markdown(f"好评率 **{best['好评率']}%**，共 {best['评论数']} 条评论")
        best_comments = filtered_comments[filtered_comments['spot_name'] == best['spot_name']]
        best_positive = best_comments[best_comments['sentiment'] == 'positive']['content'].tolist()
        if best_positive:
            best_keywords = extract_keywords(best_positive, topK=5)
            st.markdown(f"**核心优势关键词：** {', '.join([kw for kw, _ in best_keywords])}")
    else:
        st.info("暂无足够数据进行优势分析")

    if len(spot_ranking) > 1:
        worst = spot_ranking.iloc[-1]
        st.markdown(f"### ⚠️ 需要关注：{worst['spot_name']}")
        st.markdown(f"好评率 **{worst['好评率']}%**，共 {worst['评论数']} 条评论")
        worst_comments = filtered_comments[filtered_comments['spot_name'] == worst['spot_name']]
        worst_negative = worst_comments[worst_comments['sentiment'] == 'negative']['content'].tolist()
        if worst_negative:
            worst_keywords = extract_keywords(worst_negative, topK=5)
            st.markdown(f"**主要问题关键词：** {', '.join([kw for kw, _ in worst_keywords])}")
    else:
        st.info("暂无足够数据进行问题诊断")

    st.markdown("---")
    st.markdown("## 四、时间洞察")

    if 'date_parsed' in filtered_comments.columns and filtered_comments['date_parsed'].notna().any():
        temp_df = filtered_comments.copy()
        temp_df['month'] = temp_df['date_parsed'].dt.to_period('M').astype(str)
        monthly_data = temp_df.groupby('month').apply(
            lambda x: (x['sentiment'] == 'positive').mean() * 100
        ).reset_index()
        monthly_data.columns = ['month', '好评率']
        if len(monthly_data) > 0:
            best_month = monthly_data.loc[monthly_data['好评率'].idxmax(), 'month']
            worst_month = monthly_data.loc[monthly_data['好评率'].idxmin(), 'month']
            col1, col2 = st.columns(2)
            with col1:
                st.metric("口碑最佳月份", best_month)
            with col2:
                st.metric("口碑待改进月份", worst_month)
        else:
            st.info("暂无充足时间数据")
    else:
        st.info("暂无充足时间数据")

    st.markdown("---")
    st.markdown("## 五、改进建议")

    suggestions = []

    if len(spot_ranking) > 1:
        worst = spot_ranking.iloc[-1]
        if worst['好评率'] < 60:
            suggestions.append(
                f"🔴 **{worst['spot_name']}** 好评率偏低（{worst['好评率']}%），建议重点关注该景区的服务质量和游客体验")

        worst_comments = filtered_comments[filtered_comments['spot_name'] == worst['spot_name']]
        worst_negative = worst_comments[worst_comments['sentiment'] == 'negative']['content'].tolist()
        if worst_negative:
            worst_keywords = extract_keywords(worst_negative, topK=5)
            worst_keywords_list = [kw for kw, _ in worst_keywords]
            if '人多' in worst_keywords_list or '拥挤' in worst_keywords_list:
                suggestions.append("🟡 **承载量问题**：游客普遍反映“人多”“拥挤”，建议加强人流疏导，推行预约制")
            if '商业化' in worst_keywords_list:
                suggestions.append("🟡 **商业化问题**：游客反映商业化过度，建议在商业开发与文化保护之间寻求平衡")
            if '排队' in worst_keywords_list:
                suggestions.append("🟡 **服务效率问题**：游客反映排队时间长，建议优化购票和检票流程")
            if '门票贵' in worst_keywords_list:
                suggestions.append("🟡 **价格问题**：游客反映门票价格偏高，建议考虑推出优惠票种或淡季票价")

    if len(suggestions) == 0:
        suggestions.append("✅ 各景点整体口碑良好，建议继续保持并加强优势宣传")

    for s in suggestions:
        st.markdown(s)

    st.markdown("---")
    st.caption(f"报告生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ==================== 页面三：数据详情浏览 ====================
elif page == "📄 数据详情浏览":
    st.subheader("📄 游客评论数据详情")
    st.markdown("浏览、筛选和搜索原始评论数据")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_spot = st.selectbox("按景点筛选", ["全部"] + list(filtered_comments['spot_name'].unique()))
    with col2:
        filter_sentiment = st.selectbox("按情感筛选", ["全部", "正面", "负面"])
    with col3:
        search_keyword = st.text_input("按关键词搜索", placeholder="输入关键词")

    data_df = filtered_comments.copy()
    if filter_spot != "全部":
        data_df = data_df[data_df['spot_name'] == filter_spot]
    if filter_sentiment == "正面":
        data_df = data_df[data_df['sentiment'] == 'positive']
    elif filter_sentiment == "负面":
        data_df = data_df[data_df['sentiment'] == 'negative']
    if search_keyword:
        data_df = data_df[data_df['content'].str.contains(search_keyword, na=False, case=False)]

    st.markdown(f"**共找到 {len(data_df)} 条评论**")

    page_size = 10
    total_pages = max(1, (len(data_df) + page_size - 1) // page_size)
    page_num = st.number_input("页码", min_value=1, max_value=total_pages, value=1)
    start_idx = (page_num - 1) * page_size
    end_idx = start_idx + page_size
    page_data = data_df.iloc[start_idx:end_idx]

    display_df = page_data[['spot_name', 'content', 'sentiment', 'date']].copy()
    display_df.columns = ['景点', '评论内容', '情感', '日期']
    display_df['情感'] = display_df['情感'].map({'positive': '😊 正面', 'negative': '😞 负面'})

    st.dataframe(display_df, use_container_width=True, height=400)

    st.markdown("---")
    csv = data_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 导出当前数据为CSV",
        data=csv,
        file_name="comments_export.csv",
        mime="text/csv"
    )
