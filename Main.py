import streamlit as st
import time
import cv2
from pyzbar.pyzbar import decode
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av

# ------------------ CONFIG ------------------
st.set_page_config(page_title="MHE Pallet Tracking", layout="centered")

# ------------------ SESSION ------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = None

if "last_scan" not in st.session_state:
    st.session_state.last_scan = None

# ------------------ MOCK DATABASE ------------------
USERS = {
    "admin": {"password": "123", "role": "Admin"},
    "user1": {"password": "123", "role": "User"}
}

# ------------------ FUNCTIONS ------------------
def go(page):
    st.session_state.page = page

def authenticate(username, password):
    user = USERS.get(username)
    if not user:
        return False, "User not found"
    if user["password"] != password:
        return False, "Wrong password"
    return True, user

def require_login():
    if not st.session_state.get("user"):
        st.warning("Please login first")
        go("login")
        st.stop()

# ------------------ CAMERA PROCESSOR ------------------
class VideoProcessor(VideoProcessorBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        decoded_objects = decode(img)

        for obj in decoded_objects:
            x, y, w, h = obj.rect
            barcode_data = obj.data.decode("utf-8")

            # วาดกรอบ
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # ใส่ข้อความ
            cv2.putText(img, barcode_data, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

            # save ล่าสุด
            st.session_state.last_scan = barcode_data

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ------------------ PAGES ------------------
def login_page():
    st.title("🔐 MHE Pallet Tracking")
    st.caption("Track pallets in trip assignment")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            success, result = authenticate(username, password)

            if not success:
                st.error(result)
            else:
                st.session_state.user = {
                    "username": username,
                    "role": result["role"]
                }
                with st.spinner("Logging in..."):
                    time.sleep(1)
                go("scan")

def scan_page():
    require_login()

    user = st.session_state.user

    st.title("📦 Scanning Page")
    st.success(f"Logged in as: {user['username']} ({user['role']})")

    st.subheader("📷 Camera Scanner (OpenCV)")

    webrtc_streamer(
        key="scanner",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
    )

    # แสดงผลล่าสุด
    if st.session_state.last_scan:
        st.success(f"✅ Last Scan: {st.session_state.last_scan}")

    st.divider()

    # Manual input (backup)
    pallet_id = st.text_input("⌨️ Or Enter Pallet ID")
    if st.button("Submit Manual"):
        if pallet_id:
            st.success(f"Pallet '{pallet_id}' saved!")
        else:
            st.warning("Please enter pallet ID")

    st.divider()

    if st.button("Logout"):
        st.session_state.clear()
        go("login")

# ------------------ ROUTER ------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "scan":
    scan_page()
