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
    layout="wide"
)

st.title("🏯 北京景点评价分析平台")
st.markdown("基于游客评论的景点口碑可视化分析")
st.markdown("---")


# ==================== 数据加载 ====================
@st.cache_data
def load_comments_data():
    """加载评论数据"""
    try:
        df = pd.read_csv('comments.csv')
        st.success(f"成功加载评论数据，共 {len(df)} 条")
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

# ==================== 侧边栏筛选 ====================
st.sidebar.header("📊 筛选条件")
spot_list = comments_df['spot_name'].unique().tolist()
selected_spot = st.sidebar.selectbox("选择景点", spot_list)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 数据概览")
st.sidebar.metric("总评论数", len(comments_df))
st.sidebar.metric("景点数量", len(spot_list))
positive_count = len(comments_df[comments_df['sentiment'] == 'positive'])
st.sidebar.metric("正面评论占比", f"{positive_count / len(comments_df) * 100:.1f}%")

# ==================== 1. 情感地图 ====================
st.subheader("🗺️ 北京景点情感分布地图")


def create_sentiment_map(comments_df):
    """生成情感地图"""
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
            formatter="{b}<br/>经纬度: {c}",
            background_color="rgba(0,0,0,0.7)",
            border_color="#fff"
        )
    )

    # 不再返回图表对象，而是直接在当前函数里渲染它
    geo.render("sentiment_map.html")
    with open("sentiment_map.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=550)
    return None  # 因为已经渲染了，所以不需要再返回


# 直接调用函数，它会自己把地图显示出来
create_sentiment_map(comments_df)

st.markdown("---")

# ==================== 2. 时间趋势图 ====================
st.subheader("📈 口碑趋势分析")


def create_trend_chart(comments_df, spot_name):
    """生成口碑趋势图（按日期排序）"""
    spot_df = comments_df[comments_df['spot_name'] == spot_name].copy()

    if spot_df.empty:
        st.info(f"{spot_name} 暂无评论数据")
        return None

    # 检查是否有date列
    if 'date' not in spot_df.columns:
        st.warning("数据缺少日期字段，无法生成趋势图")
        return None

    try:
        # 转换日期格式并排序
        spot_df['date'] = pd.to_datetime(spot_df['date'], errors='coerce')
        spot_df = spot_df.dropna(subset=['date'])
        spot_df = spot_df.sort_values('date')

        # 按月份分组计算平均情感分
        spot_df['month'] = spot_df['date'].dt.to_period('M').astype(str)
        monthly_sentiment = spot_df.groupby('month').apply(
            lambda x: (x['sentiment'] == 'positive').mean()
        ).reset_index()
        monthly_sentiment.columns = ['month', 'sentiment_score']

        # 创建折线图（移除rotate参数）
        line = Line(init_opts=opts.InitOpts(width="100%", height="400px"))
        line.add_xaxis(monthly_sentiment['month'].tolist())
        line.add_yaxis(
            "情感得分",
            monthly_sentiment['sentiment_score'].tolist(),
            label_opts=opts.LabelOpts(is_show=True, rotate=45),  # rotate移到LabelOpts中
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
    except Exception as e:
        st.warning(f"生成趋势图时出错：{e}")
        return None


trend_chart = create_trend_chart(comments_df, selected_spot)
if trend_chart:
    components.html(trend_chart.render_embed(), height=450)
else:
    st.info("暂无趋势数据")

st.markdown("---")

# ==================== 3. 词云图 ====================
st.subheader("💬 游客心声")


def extract_keywords(texts, topK=20):
    """提取关键词"""
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
    """生成词云图"""
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


spot_comments = comments_df[comments_df['spot_name'] == selected_spot]
positive_texts = spot_comments[spot_comments['sentiment'] == 'positive']['content'].tolist()
negative_texts = spot_comments[spot_comments['sentiment'] == 'negative']['content'].tolist()

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 😊 正面评价词云")
    pos_wordcloud = create_wordcloud(positive_texts, "正面评价")
    if pos_wordcloud:
        components.html(pos_wordcloud.render_embed(), height=350)
        st.caption(f"共 {len(positive_texts)} 条正面评价")
    else:
        st.info("暂无正面评价")

with col2:
    st.markdown("#### 😞 负面评价词云")
    neg_wordcloud = create_wordcloud(negative_texts, "负面评价")
    if neg_wordcloud:
        components.html(neg_wordcloud.render_embed(), height=350)
        st.caption(f"共 {len(negative_texts)} 条负面评价")
    else:
        st.info("暂无负面评价")

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