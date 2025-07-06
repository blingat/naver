# PRD 문서 기반 셀렉터 정의
SELECTORS = {
    # 공감 자동화
    'like_button_off': 'a.u_likeit_list_btn._button.off',
    'like_button_on': 'a.u_likeit_list_btn._button.on',
    
    # 서이추 자동화
    'neighbor_search_link': 'div.title_area a.title_link',
    'neighbor_add_btn': 'a.btn_buddy._buddy_popup_btn',
    'neighbor_radio': 'input#each_buddy_add',
    'neighbor_next_btn': 'a.button_next._buddyAddNext',
    'neighbor_msg_box': 'textarea#message',
    'neighbor_msg_box_class': 'textarea.text_box._bothBuddyAddMessage',
    'neighbor_final_next': 'a.button_next._addBothBuddy',
    
    # 댓글 자동화
    'comment_box': 'textarea.u_cbox_text',
    'comment_submit': 'button.u_cbox_btn_upload',
    
    # 로그인 확인
    'login_profile_area': 'div.sc_login.NM_FAVORITE_LOGIN',
    'login_my_info': 'a[href*="nid.naver.com/user2/help"]',
    'login_button': 'a.link_login',
    'login_email_info': 'div.MyView-module__desc_email___JwAKa',
    
    # 블로그 페이지
    'blog_main_frame': 'mainFrame',
    'blog_user_info': 'div.user_info',
    
    # 기타
    'page_loading': 'div.loading',
    'alert_message': 'div.alert_message'
} 