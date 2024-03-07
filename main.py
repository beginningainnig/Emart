import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from collections import Counter
import re
import webbrowser


plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['font.size'] = 7

st.markdown('### 이마트 새벽배송 카테고리 별 상위 20% 항목 분석')
st.markdown('###### -이마트 PB의 입지 파악 및 개선 방향 중심으로')

st.text('신세계아이앤씨 / 데이터분석')
st.text('활용도\n-신세계가 제공하는 새벽배송 서비스에서 판매량 상위 20% 상품 PB/not-PB비교 분석\n\n의미\n-PB 상품의 현재 경쟁력 파악 및 방향성 탐구')
st.markdown('---')
st.text('데이터 수집 페이지')
url = 'https://emart.ssg.com/disp/theme/category.ssg?dispCtgId=6000224023&sort=sale'

if st.button('Browser'):
    webbrowser.open_new_tab(url) 
st.text('수집 데이터 설명\n카테고리별 상품명, 브랜드명, 링크, 해시태그, 할인율 데이터 수집\n페이지바 태그 수집해 자동으로 페이지 돌아가며 수집\n[Brand]에서 PB 브랜드명 리스트와 비교해 [PB or Not] 생성\n판매순으로 크롤링->인덱스열을 [Rank]로 생성 ')
st.text('1. 전처리\nDType 변환, 불용어 제거, 상위 20% 데이터셋 추출')
st.text('2. 활용1\n 카테고리 별로 상위 20% 제품 할인율 비교 by boxplot')
st.text('3. 활용2\n 상위 20% 제품 TOP 10 해시태그 비교 by barplot')

st.markdown('---')

# 데이터 읽어오기(함수로) 
### @st.cache_data  -->  데이터 저장해두기.  불필요한 실행 반복하지 않도록 하기
@st.cache_data
def read_raw_data():
    raw = pd.read_csv('./dataset.csv')
    return raw
def read_top_data():
    top = pd.read_csv('./top_20_df.csv')
    return top
# 데이터 읽어오기
raw = read_raw_data()
top = read_top_data()


#카테고리
category_list=['과일/견과/쌀', '채소', '정육/계란류', '수산물/건해산', 
               '우유/유제품', '밀키트/반찬/간편요리', '김치/반찬/델리', '생수/음료/커피/건강',
               '면류/통조림', '양념/오일', '과자/간식', '베이커리/잼', '제지/위생용품', 
               '청소/생활용품', '가구/인테리어', '주방용품', '반려동물', '뷰티', '베이비/키즈', 
               '리빙/생활']

# 전체 데이터 표시하기
with st.expander("Top Ranked Products"):
    selected_column_list = st.multiselect("Show Columns : ", top.columns, 
                                          default = ['Rank', 'Category', 'Product_Name', 'Brand', 'Hashtags', 'Discount_Rate', 'Link', 'PB or Not'])
    st.dataframe(top[selected_column_list])

pb = top[top['PB or Not'] == 'PB']
not_pb = top[top['PB or Not'] == 'NotPB']

# 요약 데이터 표시 : 총 상품 수, 총 카테고리 별 상위 20% 상품 수, PB상품 수, PB 상품의 Ranked 비율 
columns = st.columns(4)
with columns[0]:
    st.metric(label = "총 상품 수", value = raw.shape[0]) 
with columns[1]:
    st.metric(label = "상위 20%에 든 상품 수", value = top.shape[0])
with columns[2]:
    st.metric(label = "상위 20%에 든 PB상품 수", value = pb.shape[0])
with columns[3]:
    st.metric(label="PB상품의 Ranked 비율", value=f"{(pb.shape[0] / top.shape[0]) * 100:.1f}%")


    
    
st.markdown('---')
columns = st.columns(2)
with columns[0]:
    st.markdown('#### 할인율 Boxplot')
with columns[1]:
    st.text('A SMALL\n- Share\n- Discount Rate\n- Number of discounted products')

# Streamlit 앱 생성
# PB의 박스플롯 그리기
fig_pb = px.box(pb, x='Category', y='Discount_Rate', color='PB or Not', points=False, 
                color_discrete_map={'PB': 'yellow'}, title='PB 할인율 Boxplot')
st.plotly_chart(fig_pb)
    
# Not PB의 박스플롯 그리기
fig_not_pb = px.box(not_pb, x='Category', y='Discount_Rate', color='PB or Not', 
                   color_discrete_map={'NotPB': 'red'}, points=False, title='Not PB 할인율 Boxplot')
st.plotly_chart(fig_not_pb)

# PB와 Not PB를 하나의 데이터프레임으로 합치기
combined_data = pd.concat([pb.assign(type='PB'), not_pb.assign(type='Not PB')])

# 할인율 Boxplot 그리기
fig_combined = px.box(combined_data, x='Category', y='Discount_Rate', color='type', 
                      color_discrete_map={'PB': 'yellow', 'Not PB': 'red'}, points=False, 
                      title='Discount_Rate Boxplot')

# Streamlit 앱에 그래프 표시
st.plotly_chart(fig_combined)


st.markdown('---')
st.markdown('#### 상위 Hash tag 비교')

hash_top = top.dropna(subset=['Hashtags'])
# PB와 Not PB로 데이터 나누기
hash_pb = hash_top[hash_top['PB or Not'] == 'PB']
hash_not_pb = hash_top[hash_top['PB or Not'] == 'NotPB']


# 'PB'일 때의 해시태그 리스트
# 'Hashtags' 열의 값을 차례대로 저장할 빈 리스트 생성
hashtags_list_pb = hash_pb['Hashtags'].tolist()
hashtags_list_pb_cleaned = [tag.strip("[] ") for tags in hashtags_list_pb for tag in tags.split(',') if tag != '[]']
# 각 행의 'Hashtags' 열 값 가져와서 리스트에 추가 (단, '[]', 공백은 제외, 값 여러개면 쉼표 기준으로 문자열 분리)


# 'Not PB'일 때의 해시태그 리스트
hashtags_list_not_pb = hash_not_pb['Hashtags'].tolist()
hashtags_list_not_pb_cleaned = [tag.strip("[] ") for tags in hashtags_list_not_pb for tag in tags.split(',') if tag != '[]']
# 각 행의 'Hashtags' 열 값 가져와서 리스트에 추가 (단, '[]', 공백은 제외, 값 여러개면 쉼표 기준으로 문자열 분리)


# 'PB'일 때의 빈도수 계산
hashtags_counter_pb = Counter(hashtags_list_pb_cleaned)

# 'Not PB'일 때의 빈도수 계산
hashtags_counter_not_pb = Counter(hashtags_list_not_pb_cleaned)

# 결과를 데이터프레임으로 변환
hashtags_df_pb = pd.DataFrame(list(hashtags_counter_pb.items()), columns=['Hashtag', 'Frequency'])
hashtags_df_not_pb = pd.DataFrame(list(hashtags_counter_not_pb.items()), columns=['Hashtag', 'Frequency'])

# Frequency 기준으로 내림차순 정렬
hashtags_df_pb = hashtags_df_pb.sort_values(by='Frequency', ascending=False)
hashtags_df_not_pb = hashtags_df_not_pb.sort_values(by='Frequency', ascending=False)
columns = st.columns(2)
with columns[0]:
        # 'PB'일 때의 상위 10개 빈도수 막대 그래프 (노란색)
    fig_hash_pb, ax_hash_pb = plt.subplots()
    ax_hash_pb.bar(hashtags_df_pb['Hashtag'].head(10), hashtags_df_pb['Frequency'].head(10), color='yellow')
    ax_hash_pb.set_title('Top 10 Hashtags - PB')
    ax_hash_pb.set_xlabel('Hashtag')
    ax_hash_pb.set_ylabel('Frequency')
    
    # 결과 확인
    st.pyplot(fig_hash_pb)

with columns[1]:
# 'Not PB'일 때의 상위 10개 빈도수 막대 그래프 (빨간색)
    fig_hash_not_pb, ax_hash_not_pb = plt.subplots()
    ax_hash_not_pb.bar(hashtags_df_not_pb['Hashtag'].head(10), hashtags_df_not_pb['Frequency'].head(10), color='red')
    ax_hash_not_pb.set_title('Top 10 Hashtags - Not PB')
    ax_hash_not_pb.set_xlabel('Hashtag')
    ax_hash_not_pb.set_ylabel('Frequency')

    st.pyplot(fig_hash_not_pb)

