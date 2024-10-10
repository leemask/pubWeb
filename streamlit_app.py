import streamlit as st
from datetime import datetime, timedelta
import threading
import time
#from gSheetComm import gSheetComm
from dbms import *
import pandas as pd
from st_aggrid import AgGrid

status_messages = {'logout': "로그인 먼저 해주세요", 'login_fail': "로그인 실패", 'login_ok': "로그인성공"}
platform_list=['baemin','coupang','yogi']

if 'log_messages' not in st.session_state:
    st.session_state['log_messages'] = "", None
if 'db_init' not in st.session_state:
    st.session_state['dbms'] =dbms() 
    

# 상태 변수 설정
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if 'status_running' not in st.session_state:
    st.session_state['status_running'] = False
if 'setting' not in st.session_state:
    st.session_state['setting'] = [], False, False
if 'account' not in st.session_state:
    st.session_state['account'] = []
if 'status' not in st.session_state:
    st.session_state['status'] = 'logout'

total_posts, df_msg = st.session_state['log_messages']
dbms = st.session_state['dbms']
setting_values, system_enabled, user_enabled = st.session_state['setting']
account = st.session_state['account']

# Function to add log messages safely
def add_log_message(message, clear = False):
    if(clear):
        st.session_state['log_messages'] = "", None    
    comment_area.text(message)

# 배달앱 설정을 클릭했을 때 호출되는 함수
def show_settings():
    if(st.session_state['status'] != 'login_ok'):
        st.error("로그인 먼저 해주세요.")
        return
    st.session_state.show_settings = True

def login_handler(id, password):
    
    val = [id,password]
    print(val)
    if dbms.loginCheck(id, password):
        print("id found")
        st.session_state['account'] = val
        #get setting
        settings, system_enabled, user_enabled = dbms.get_settings(id)
        values = []
        for setting in settings:
            print(setting)
            values.append([setting['id'], setting['password']])   
            
        st.session_state['setting'] = values, system_enabled, user_enabled
        print(values)
        return True
    else:
        print("id not found")
        return False
# 설정 완료 버튼을 클릭했을 때 호출되는 함수
def save_settings():
    st.session_state.show_settings = False
    val, system_enabled,user_enabled = st.session_state.setting
    
    values = []
    for i in range(3): #비어있어도 3개 입력, 나중에 수정하거나 지울 수 있을때를 대비해서 
        account = st.session_state.account
        val[i] = [ account[0], platform_list[i]] +  val[i] + ["",""] #가게번호 ""로 초기화       
        values.append(val[i])
    print(values) 
    dbms.update_setttings(values)    
    #st.session_state.setting = [value[2:] for value in values], system_enabled, user_enabled
        
    print("save_settings")

def cancel_settings():
    st.session_state.show_settings = False

# 레이아웃 설정
col1, col2 = st.columns([2, 8])  # col1 width: 20%, col2 width: 80%

# Row 0 - Column 0: 이미지 배치
with col1:
    st.image("aicafe.PNG", caption="❤️      AI가 고객리뷰에 답글을 달아줍니다 ", use_column_width=True)

# Row 0 - Column 1: 로그인 폼
with col2:
    col2_1, col2_2,col2_3 = st.columns(3)
    #st.write("### 로그인")
    with col2_1:
        user_id = st.text_input("ID")
    with col2_2:
        password = st.text_input("Password", type="password")
    with col2_3:
        print(st.session_state['status'])
        if st.session_state['status'] == 'login_ok':
            st.write(f"### {st.session_state['account'][0]}님 환영합니다.")
            if st.button("로그아웃") :
                st.session_state['account'] = []
                st.session_state['status'] = 'logout'
                st.session_state['setting'] = [], False, False
                st.session_state['log_messages'] = "", None
                st.session_state.show_settings = False
                st.rerun()
        else :            
            if st.session_state['status'] == 'login_fail':
                st.write("### 로그인 실패")
            else:
                st.write("### 로그인 먼저 해주세요.")
            if st.button("로그인") :
                if(not user_id or not password):
                    st.session_state['status'] = 'login_fail'
                else:
                    if(login_handler(user_id,password)) :
                        st.session_state['status'] = 'login_ok'                                        
                        st.success("로그인 성공")
                    else :
                        st.error("로그인 실패")
                        st.session_state['status'] = 'login_fail'
                st.rerun()
 

# Row 1 - Column 0: 4개의 버튼 생성
with st.container():
    col1, col2 = st.columns([2, 8])  # col1 width: 20%, col2 width: 80%

    with col1:
        st.write("### 기능")
        st.button("배달앱 설정", on_click=show_settings)
        # Buttons for start and stop
        
        if st.session_state['status'] != 'login_ok' or st.session_state.show_settings:
            button_show = False            
        else:
            button_show = True
            
        if button_show and st.button("댓글 보기"):    
            account = st.session_state['account']
            df, total = dbms.get_gptPosts(account[0]) 
            st.write("here")  
            if(total == 0):
                st.write("데이터가 없습니다.")
            else:
                st.session_state['log_messages'] = total, df
                #AgGrid(df, height=400, fit_columns_on_grid_load=True)
            st.rerun()
                
        if button_show :
            if user_enabled :
                if st.button("댓글 중지"):  
                # update dbms
                    dbms.update_user_enabled(account[0], False)
                    st.session_state['setting'] = setting_values, system_enabled, False
                    
                    st.rerun()
            else :
                if st.button("댓글 시작"):  
                    # update dbms
                    dbms.update_user_enabled(account[0], True)
                    st.session_state['setting'] = setting_values, system_enabled, True
                    st.rerun()

    # Row 1 - Column 1: 배달앱 설정 or 실시간 댓글 표시
    with col2:
        # 입력 상자와 버튼들을 담을 공간 설정
        settings_container = st.empty()        
        if st.session_state.show_settings:
            with settings_container.container():
                st.write("### 배달앱 설정")
                #values = st.session_state['setting']
                values = setting_values
                print("--", values)
                for ind in range (3-len(values)):
                    values.append(["",""])
               
                rows = 3
                cols = 3
                grid = []
                platforms =['배민','쿠팡','요기요']
                titles = ["아이디", "패스워드", ""]
                # Generate text inputs and store the results
                #if len(values) < 3:
                #    values = values + [["",""],["",""]]
                for row in range(rows):
                    cols_input = []
                    cols_container = st.columns([2,3,3])
                    for col in range(cols):
                        if col == 0 :
                            cols_container[col].write(f"#### {platforms[row]}")
                        else :
                            cols_input.append(cols_container[col].text_input(f"{titles[col-1]}", key=f"{row}_{col}", value=values[row][col-1]))
                    grid.append(cols_input)
                print(grid)
                st.session_state.setting = grid, system_enabled, user_enabled
                #st.session_state.account = ["cafe_1"]
                # Button to trigger the display of values

                st.button("설정 완료", on_click=save_settings)
                st.button("취소", on_click=cancel_settings)
        else:
                    # 실시간 댓글 영역
            comment_area = st.empty()
            comment_area.empty()  # 실시간 댓글 영역 비움
            st.write("### 댓글 결과")            
            
            if df_msg is not None and not df_msg.empty:
                #AgGrid(df, height=400, fit_columns_on_grid_load=True)
                info_msg = ""
                if(system_enabled==False): 
                    info_msg = ("시스템에서 댓글을 중지하였습니다. \n")    
                if(user_enabled==False):
                    info_msg = ("사용자가 댓글을 중지하였습니다. \n")
                info_msg += f"총 댓글수 : {total_posts}개"
                st.write(info_msg)

                for index, row in df_msg.iterrows():
                    row['reply'] = '\n ===> '+ row['reply']
                    st.write(f"{index + 1}. {','.join(map(str, row.values))}")
            



