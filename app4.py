# app.py
import streamlit as st
import sqlite3
import time
import os
from datetime import datetime
import pandas as pd
import asyncio
from PIL import Image

# Streamlitアプリのタイトル
st.title('画像を表示したい。たのむ')

# 入力フォーム
user_name = st.text_input('ユーザー名をアルファベットで入力してください:')

# データベース接続
conn = sqlite3.connect('data_timestamp.db')
c = conn.cursor()

# ユーザーごとのテーブルを作成
c.execute(f'''
    CREATE TABLE IF NOT EXISTS {user_name}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_text TEXT,
        time REAL
    )
''')
conn.commit()

#画像表示のための準備
sleeptime = 5  #表示時間
blackImg = Image.open('./images/black.png')
showImg = st.empty()
showImg.image(blackImg)
imgIndex = 1

#一定時間のみ画像を表示する関数
async def display_image(i):
    img = Image.open('./images/'+ i +'.png')
    showImg.image(img)
    await asyncio.sleep(sleeptime)
    showImg.image(blackImg)

# st.session_stateに解答時間を用意する
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = {'start': None, 'save': None}

# 表示ボタンがクリックされたときにタイムスタンプを更新
if st.button('表示'):
    st.session_state.timestamps['start'] = time.time()
    asyncio.run(display_image(imgIndex))

# 入力フォーム
input_text = st.text_input('何に見えますか？')

# 保存ボタンがクリックされたときのみデータベースへ保存
if st.button('保存'):
    # タイムスタンプを更新
    st.session_state.timestamps['save'] = time.time()

    # 解答にかかった時間を計算
    elapsed_time = st.session_state.timestamps['save'] - st.session_state.timestamps['start']

    # データベースへ保存
    c.execute(f'INSERT INTO {user_name} (input_text, time) VALUES (?, ?)',
              (input_text, elapsed_time))
    conn.commit()
    st.success('情報が保存されました！')

# データベースからデータを取得
data = c.execute(f'SELECT * FROM {user_name}').fetchall()

# データを表示
st.subheader('データベース内のユーザー:')
if data:
    # テーブル形式で表示
    st.table(data)
else:
    st.warning('データベースにはまだ情報がありません。')

# 終了ボタンがクリックされたときにエクセルファイルを出力
if st.button('終了'):
    # データベースから全データを取得
    all_data = c.execute(f'SELECT * FROM {user_name}').fetchall()

    # DataFrameに変換
    df = pd.DataFrame(all_data, columns=['id', 'input_text', 'time'])

    # カレントディレクトリを取得
    current_directory = os.getcwd()

    # 日時を取得してフォーマット
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # ファイル名に日時を含めて書き込み
    excel_filename = f'{user_name}_user_data_{current_time}.xlsx'
    relative_filepath = os.path.join('./data', excel_filename)
    df.to_excel(relative_filepath, index=False)
    st.success(f'エクセルファイルが {relative_filepath} に出力されました！')

# データベースクローズ
conn.close()
