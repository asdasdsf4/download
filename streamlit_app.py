import streamlit as st
import shutil
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Streamlit Drive", page_icon="🗂️", layout="wide")

# --- PATH SETUP ---
# Root directory for storing files.
STORAGE_DIR = Path("file_storage")
STORAGE_DIR.mkdir(exist_ok=True)

# Initialize session state for navigation.
if "current_path" not in st.session_state:
    st.session_state.current_path = STORAGE_DIR

# --- HELPER FUNCTIONS ---

def get_file_icon(file_path):
    """Returns an emoji icon based on file extension."""
    extension = file_path.suffix.lower()
    icon_map = {
        ".pdf": "📄", ".docx": "📝", ".txt": "🗒️", ".xlsx": "📊", ".csv": "📈",
        ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️",
        ".zip": "📦", ".py": "🐍", ".mp3": "🎵", ".wav": "🎧", ".mp4": "🎬",
    }
    return icon_map.get(extension, "❔")

def format_bytes(size):
    """Converts bytes to a human-readable format (KB, MB, GB)."""
    if size is None: return "N/A"
    power = 1024
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power and n < len(power_labels) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def get_all_folders(root_dir):
    """Recursively gets all subdirectories within the root directory."""
    folders = [path for path in root_dir.rglob('*') if path.is_dir()]
    return [STORAGE_DIR] + folders # Include the root itself

def handle_rename(old_path, new_name):
    """Renames a file or folder."""
    if not new_name.strip():
        st.warning("Name cannot be empty.")
        return
    new_path = old_path.parent / new_name.strip()
    if new_path.exists():
        st.error(f"'{new_name}' already exists in this folder.")
    else:
        try:
            old_path.rename(new_path)
            st.success(f"Renamed to '{new_name}'")
            st.rerun()
        except Exception as e:
            st.error(f"Error renaming: {e}")

# --- UI STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #F0F2F5; }
    .main .block-container { padding: 2rem 3rem; }
    footer { visibility: hidden; }
    .stButton>button {
        border: none;
        background-color: #FFFFFF;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR FOR ACTIONS ---
with st.sidebar:
    st.title("🗂️ Streamlit Drive")
    st.markdown("---")
    with st.expander("⬆️ Upload Files", expanded=True):
        uploaded_files = st.file_uploader("Select files...", accept_multiple_files=True, label_visibility="collapsed")
        if st.button("Upload", use_container_width=True, disabled=not uploaded_files):
            for up_file in uploaded_files:
                save_path = st.session_state.current_path / up_file.name
                with open(save_path, "wb") as f:
                    # ⭐ MODIFICATION HERE: Stream the file to disk for memory efficiency
                    shutil.copyfileobj(up_file, f)
            st.success(f"Uploaded {len(uploaded_files)} file(s)!")
            st.rerun()

    with st.expander("➕ Create New Folder"):
        with st.form("new_folder_form", clear_on_submit=True):
            folder_name = st.text_input("Folder Name")
            submitted = st.form_submit_button("Create Folder")
            if submitted and folder_name:
                new_folder_path = st.session_state.current_path / folder_name
                if not new_folder_path.exists():
                    new_folder_path.mkdir()
                    st.success(f"Folder '{folder_name}' created!")
                    st.rerun()
                else:
                    st.error(f"Folder '{folder_name}' already exists.")
    st.markdown("---")
    st.info("Manage your files and folders in the main window.")


# --- MAIN CONTENT AREA ---

# Header: Home Button and Breadcrumbs
st.markdown("### My Files")

main_header = st.container()
with main_header:
    cols = st.columns([1, 6])
    with cols[0]:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_path = STORAGE_DIR
            st.rerun()

    with cols[1]:
        path_parts = st.session_state.current_path.relative_to(STORAGE_DIR).parts
        breadcrumb_cols = st.columns(len(path_parts) * 2 + 1)
        with breadcrumb_cols[0]:
             st.markdown("Home")
        for i, part in enumerate(path_parts):
            with breadcrumb_cols[i*2 + 1]:
                 st.markdown("&nbsp;>&nbsp;", unsafe_allow_html=True)
            with breadcrumb_cols[i*2 + 2]:
                if i < len(path_parts) - 1:
                    if st.button(part, key=f"bc_{i}"):
                        st.session_state.current_path = STORAGE_DIR.joinpath(*path_parts[:i+1])
                        st.rerun()
                else:
                    st.markdown(f"**{part}**")

st.markdown("<hr style='margin:0.5rem 0'>", unsafe_allow_html=True)

# --- File & Folder Listing ---
try:
    items = list(st.session_state.current_path.iterdir())
    folders = sorted([i for i in items if i.is_dir()], key=lambda i: i.name.lower())
    files = sorted([i for i in items if i.is_file()], key=lambda i: i.name.lower())

    if not folders and not files:
        st.info("This folder is empty.", icon="📂")

    for folder in folders:
        cols = st.columns([6, 2, 2])
        with cols[0]:
            if st.button(f"📁 {folder.name}", key=f"folder_{folder}", use_container_width=True):
                st.session_state.current_path = folder
                st.rerun()
        with cols[1]:
            st.markdown(f"<div style='text-align:right; color:grey;'>Folder</div>", unsafe_allow_html=True)
        with cols[2]:
            with st.popover("...", use_container_width=True):
                st.header(f"Actions for {folder.name}")
                with st.form(f"rename_form_{folder}", clear_on_submit=True):
                    new_name = st.text_input("New name", value=folder.name)
                    if st.form_submit_button("Rename", use_container_width=True):
                        handle_rename(folder, new_name)
                if st.button("🗑️ Delete Folder", key=f"del_{folder}", type="primary", use_container_width=True):
                    shutil.rmtree(folder)
                    st.success(f"Deleted folder '{folder.name}'")
                    st.rerun()

    for file in files:
        stat = file.stat()
        cols = st.columns([6, 2, 2])
        with cols[0]:
            st.markdown(f'<div>{get_file_icon(file)}<span style="margin-left:10px;">{file.name}</span></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<div style='text-align:right; color:grey;'>{format_bytes(stat.st_size)}</div>", unsafe_allow_html=True)

        with cols[2]:
            with st.popover("...", use_container_width=True):
                st.header(f"Actions for {file.name}")
                with open(file, "rb") as f:
                    st.download_button("⬇️ Download", data=f, file_name=file.name, use_container_width=True)
                with st.form(f"move_form_{file}", clear_on_submit=True):
                    all_folders = get_all_folders(STORAGE_DIR)
                    folder_options = {f.relative_to(STORAGE_DIR): f for f in all_folders if f != file.parent}
                    dest_folder_rel = st.selectbox("Choose destination", options=folder_options.keys(), format_func=lambda p: "Home" if str(p) == "." else str(p))
                    if st.form_submit_button("Move File", use_container_width=True):
                        destination_path = folder_options[dest_folder_rel]
                        shutil.move(str(file), str(destination_path))
                        st.success(f"Moved '{file.name}' to '{dest_folder_rel}'")
                        st.rerun()
                with st.form(f"rename_form_{file}", clear_on_submit=True):
                    new_name = st.text_input("New name", value=file.name)
                    if st.form_submit_button("Rename", use_container_width=True):
                        handle_rename(file, new_name)
                if st.button("🗑️ Delete File", key=f"del_{file}", type="primary", use_container_width=True):
                    file.unlink()
                    st.success(f"Deleted '{file.name}'")
                    st.rerun()

except Exception as e:
    st.error(f"An error occurred: {e}")
