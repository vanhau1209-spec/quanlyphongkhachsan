import streamlit as st
import pandas as pd
from datetime import date, timedelta
import random

# ==========================================
# CẤU HÌNH TRANG
# ==========================================
st.set_page_config(page_title="Hệ Thống Quản Lý Khách Sạn", page_icon="🏨", layout="wide")

# ==========================================
# KHỞI TẠO DỮ LIỆU (MÔ PHỎNG DATABASE)
# ==========================================
def init_data():
    if 'rooms' not in st.session_state:
        st.session_state.rooms = pd.DataFrame({
            'Mã Phòng': ['101', '102', '201', '202', '301', '302'],
            'Loại Phòng': ['Standard', 'Standard', 'Deluxe', 'Deluxe', 'Suite', 'Suite'],
            'Giá/Đêm (VND)': [500000, 500000, 800000, 800000, 1500000, 1500000],
            'Trạng thái': ['Trống', 'Đang sử dụng', 'Trống', 'Bảo trì', 'Trống', 'Đang sử dụng']
        })
    
    if 'guests' not in st.session_state:
        st.session_state.guests = pd.DataFrame(columns=[
            'Mã Booking', 'Tên Khách Hàng', 'CCCD/Passport', 'Mã Phòng', 'Ngày Check-in', 'Ngày Check-out'
        ])

init_data()

# ==========================================
# GIAO DIỆN CHÍNH & ĐIỀU HƯỚNG
# ==========================================
st.sidebar.title("🏨 Hotel Manager")
menu = st.sidebar.radio(
    "Menu điều hướng",
    ["📊 Tổng quan (Dashboard)", "🛎️ Quầy Lễ tân (Reception)", "🛏️ Quản lý Phòng"]
)

st.sidebar.markdown("---")
st.sidebar.info("Ứng dụng quản lý khách sạn phát triển bằng Streamlit.")

# ------------------------------------------
# MODULE 1: TỔNG QUAN (DASHBOARD)
# ------------------------------------------
if menu == "📊 Tổng quan (Dashboard)":
    st.title("📊 Tổng quan tình trạng khách sạn")
    
    df_rooms = st.session_state.rooms
    total_rooms = len(df_rooms)
    available_rooms = len(df_rooms[df_rooms['Trạng thái'] == 'Trống'])
    occupied_rooms = len(df_rooms[df_rooms['Trạng thái'] == 'Đang sử dụng'])
    maintenance_rooms = len(df_rooms[df_rooms['Trạng thái'] == 'Bảo trì'])
    
    # Hiển thị các chỉ số chính (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng số phòng", total_rooms)
    col2.metric("Phòng trống (Sẵn sàng)", available_rooms)
    col3.metric("Phòng đang có khách", occupied_rooms)
    col4.metric("Phòng đang bảo trì", maintenance_rooms)
    
    st.markdown("---")
    st.subheader("Bản đồ phòng hiện tại")
    
    # Hiển thị lưới phòng trực quan
    cols = st.columns(3)
    for index, row in df_rooms.iterrows():
        col = cols[index % 3]
        status_color = "🟢" if row['Trạng thái'] == 'Trống' else "🔴" if row['Trạng thái'] == 'Đang sử dụng' else "🟡"
        with col:
            st.info(f"**Phòng {row['Mã Phòng']}** {status_color}\n\n"
                    f"- Loại: {row['Loại Phòng']}\n"
                    f"- Giá: {row['Giá/Đêm (VND)']:,} đ\n"
                    f"- Trạng thái: **{row['Trạng thái']}**")

# ------------------------------------------
# MODULE 2: QUẦY LỄ TÂN (CHECK-IN / CHECK-OUT)
# ------------------------------------------
elif menu == "🛎️ Quầy Lễ tân (Reception)":
    st.title("🛎️ Quầy Lễ tân")
    
    tab1, tab2 = st.tabs(["📝 Check-in (Nhận phòng)", "📤 Check-out (Trả phòng)"])
    
    # --- TAB CHECK-IN ---
    with tab1:
        st.subheader("Làm thủ tục nhận phòng")
        df_rooms = st.session_state.rooms
        available_rooms_list = df_rooms[df_rooms['Trạng thái'] == 'Trống']['Mã Phòng'].tolist()
        
        with st.form("checkin_form"):
            col1, col2 = st.columns(2)
            with col1:
                guest_name = st.text_input("Tên khách hàng (*)")
                guest_id = st.text_input("CCCD / Passport (*)")
            with col2:
                selected_room = st.selectbox("Chọn phòng trống", available_rooms_list if available_rooms_list else ["Không có phòng trống"])
                checkin_date = st.date_input("Ngày Check-in", date.today())
                checkout_date = st.date_input("Ngày Check-out dự kiến", date.today() + timedelta(days=1))
            
            submit_checkin = st.form_submit_button("Xác nhận Check-in")
            
            if submit_checkin:
                if not guest_name or not guest_id:
                    st.error("Vui lòng nhập đầy đủ thông tin khách hàng!")
                elif selected_room == "Không có phòng trống":
                    st.error("Hiện tại không có phòng trống để check-in!")
                elif checkin_date >= checkout_date:
                    st.error("Ngày Check-out phải sau ngày Check-in!")
                else:
                    # Tạo mã booking
                    booking_id = f"BK{random.randint(1000, 9999)}"
                    
                    # Thêm vào danh sách khách
                    new_guest = pd.DataFrame([{
                        'Mã Booking': booking_id,
                        'Tên Khách Hàng': guest_name,
                        'CCCD/Passport': guest_id,
                        'Mã Phòng': selected_room,
                        'Ngày Check-in': checkin_date,
                        'Ngày Check-out': checkout_date
                    }])
                    st.session_state.guests = pd.concat([st.session_state.guests, new_guest], ignore_index=True)
                    
                    # Cập nhật trạng thái phòng
                    st.session_state.rooms.loc[st.session_state.rooms['Mã Phòng'] == selected_room, 'Trạng thái'] = 'Đang sử dụng'
                    
                    st.success(f"Check-in thành công cho khách {guest_name} tại phòng {selected_room}!")
                    st.rerun()
                    
    # --- TAB CHECK-OUT ---
    with tab2:
        st.subheader("Làm thủ tục trả phòng")
        current_guests = st.session_state.guests
        
        if current_guests.empty:
            st.info("Hiện không có khách nào đang lưu trú.")
        else:
            selected_booking = st.selectbox(
                "Chọn khách hàng cần Check-out", 
                current_guests['Mã Booking'] + " - " + current_guests['Tên Khách Hàng'] + " (Phòng " + current_guests['Mã Phòng'] + ")"
            )
            
            if st.button("Xác nhận Check-out"):
                # Lấy mã booking từ chuỗi hiển thị
                b_id = selected_booking.split(" - ")[0]
                room_to_free = current_guests.loc[current_guests['Mã Booking'] == b_id, 'Mã Phòng'].values[0]
                
                # Xóa khỏi danh sách khách đang lưu trú
                st.session_state.guests = current_guests[current_guests['Mã Booking'] != b_id]
                
                # Cập nhật trạng thái phòng thành "Trống"
                st.session_state.rooms.loc[st.session_state.rooms['Mã Phòng'] == room_to_free, 'Trạng thái'] = 'Trống'
                
                st.success(f"Đã trả phòng {room_to_free} thành công!")
                st.rerun()

# ------------------------------------------
# MODULE 3: QUẢN LÝ PHÒNG (ROOM SETTINGS)
# ------------------------------------------
elif menu == "🛏️ Quản lý Phòng":
    st.title("🛏️ Quản lý danh mục phòng")
    st.write("Bạn có thể chỉnh sửa trực tiếp trên bảng dữ liệu bên dưới để thay đổi giá, loại phòng hoặc trạng thái.")
    
    # Sử dụng data_editor để chỉnh sửa dữ liệu dễ dàng
    edited_df = st.data_editor(
        st.session_state.rooms,
        column_config={
            "Trạng thái": st.column_config.SelectboxColumn(
                "Trạng thái",
                help="Tình trạng phòng",
                options=["Trống", "Đang sử dụng", "Bảo trì"],
                required=True,
            ),
            "Loại Phòng": st.column_config.SelectboxColumn(
                "Loại Phòng",
                options=["Standard", "Deluxe", "Suite", "Family"],
                required=True,
            ),
            "Giá/Đêm (VND)": st.column_config.NumberColumn(
                "Giá/Đêm (VND)",
                min_value=0,
                format="%d"
            )
        },
        num_rows="dynamic", # Cho phép thêm dòng mới
        use_container_width=True,
        key="room_editor"
    )
    
    # Nút lưu thay đổi
    if st.button("💾 Lưu thay đổi"):
        st.session_state.rooms = edited_df
        st.success("Cập nhật danh sách phòng thành công!")
