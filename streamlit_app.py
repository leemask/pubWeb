import streamlit as st
from datetime import datetime, timedelta
import threading
import time
from gSheetComm import gSheetComm

status_messages = {'logout': "로그인 먼저 해주세요", 'login_fail': "로그인 실패", 'login_ok': "로그인성공"}
sheet_name_list=['baemin','coupang','yogi']

# Initialize session state variables
if 'gsheet_instance' not in st.session_state:
    st.session_state['gsheet_instance'] = gSheetComm('baemin')

if 'log_messages' not in st.session_state:
    st.session_state['log_messages'] = []
# 상태 변수 설정
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if 'status_running' not in st.session_state:
    st.session_state['status_running'] = False
if 'setting' not in st.session_state:
    st.session_state['setting'] = []
if 'account' not in st.session_state:
    st.session_state['account'] = []
if 'status' not in st.session_state:
    st.session_state['status'] = 'logout'

# Access the class instance from session state
gsheet = st.session_state['gsheet_instance']
log_msg = st.session_state['log_messages']

# Function to add log messages safely
def add_log_message(message, clear = False):
    if(clear):
        st.session_state['log_messages'] = []    
    comment_area.text(message)

# 배달앱 설정을 클릭했을 때 호출되는 함수
def show_settings():
    if(st.session_state['status'] != 'login_ok'):
        st.error("로그인 먼저 해주세요.")
        return
    st.session_state.show_settings = True

def login_handler(id, password):
    values = gsheet.get_content_fun('account!A:B')
    print(values)
    val = [id,password]
    print(val)
    if val in values:
        print("id found")
        st.session_state['account'] = val
        #get setting
        for i in range(3):
            settings = gsheet.get_content_fun(f'{sheet_name_list[i]}!A:C')
            for setting in settings:
                if setting[0] == id :
                    print(setting)
                    st.session_state['setting'] = setting[1:]
                    break
        return True
    else:
        print("id not found")
        return False
# 설정 완료 버튼을 클릭했을 때 호출되는 함수
def save_settings():
    st.session_state.show_settings = False
    val = st.session_state.setting
    
    
    for i in range(3):
        if(len(val[i][0]) == 0 or len(val[i][1]) == 0):
            print("no data")
            continue
        #get row number
        account = st.session_state.account
        site_ids = gsheet.get_content_fun(f'{sheet_name_list[i]}!A:A') #remove header
        
        val[i].append(0) #가게번호 0로 초기화
        print(site_ids)
        param = account+val[i] 
        account_index = -1
        for idx, site_id in enumerate(site_ids):
            if site_id[0] == account[0] :
                account_index = idx+1   # Google Sheets are 1-indexed
                break
        if account_index == -1:            
            gsheet.append_row (param,sheet_name_list[i])    
        else: #update
            gsheet.update_sheet(sheet_name_list[i], account_index, [param])
            print("update")
        
    print("save_settings")
    st.session_state.comments = ["서버에서 새로운 라인을 추가 중..."]
def cancel_settings():
    st.session_state.show_settings = False

# 레이아웃 설정
col1, col2 = st.columns([2, 8])  # col1 width: 20%, col2 width: 80%

# Row 0 - Column 0: 이미지 배치
with col1:
    st.image("https://via.placeholder.com/150", caption="AI가 대신 고객 리뷰에 답글을 달아줍니다", use_column_width=True)

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
        button_show = True
        if st.session_state['status'] != 'login_ok':
            button_show = False            

        if button_show and st.button("댓글 시작"):            
            while st.session_state['status_running'] :
                val = gsheet.get_content_fun()
                #print(val)  # This is just for debugging purposes
                if(val == None):
                    continue
                val = val[2:]
                val_str = "\n".join([",".join(sublist) for sublist in val])
                print("---",val_str)

                st.session_state['sleep_state'] = True
                time.sleep(10)  # do additional work  
                st.session_state['sleep_state'] = False  
        if button_show and st.button("댓글 중지"):  
            while not st.session_state['sleep_state']:
                time.sleep(0.2)
            gsheet.stop_fun()
            add_log_message("Stopped")
            st.session_state['status_running'] = False
            st.stop()
        if button_show :
            st.button("결과 보기")

    # Row 1 - Column 1: 배달앱 설정 or 실시간 댓글 표시
    with col2:
        # 입력 상자와 버튼들을 담을 공간 설정
        settings_container = st.empty()        
        # 실시간 댓글 영역
        comment_area = st.empty()
        if st.session_state.show_settings:
            with settings_container.container():
                st.write("### 배달앱 설정")
               
                rows = 3
                cols = 3
                grid = []
                platforms =['배민','쿠팡','요기요']
                titles = ["아이디", "패스워드", ""]
                # Generate text inputs and store the results
                for row in range(rows):
                    cols_input = []
                    cols_container = st.columns([2,3,3])
                    for col in range(cols):
                        if col == 0 :
                            cols_container[col].write(f"#### {platforms[row]}")
                        else :
                            cols_input.append(cols_container[col].text_input(f"{titles[col-1]}", key=f"{row}_{col}"))
                    grid.append(cols_input)
                st.session_state.setting = grid
                st.session_state.account = ["cafe_1"]
                # Button to trigger the display of values

                st.button("설정 완료", on_click=save_settings)
                st.button("취소", on_click=cancel_settings)
                
            comment_area.empty()  # 실시간 댓글 영역 비움

        else:
            st.write("### 실시간 댓글")



