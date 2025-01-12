import streamlit as st
from datetime import datetime
import pytz

def render_documents_section(supabase):
    """Render the documents section of My Profile."""
    st.write("### 📄 Documents")
    
    # Get user's documents
    docs = supabase.table("user_documents").select("*").eq("user_id", st.session_state.user.id).execute()
    user_docs = docs.data if docs.data else []
    
    # Group by document type
    cv = next((d for d in user_docs if d["document_type"] == "cv"), None)
    transcript = next((d for d in user_docs if d["document_type"] == "transcript"), None)
    
    # Display documents
    doc_col1, doc_col2 = st.columns(2)
    
    with doc_col1:
        if cv:
            try:
                # Parse timestamp with timezone
                upload_date = datetime.strptime(cv["created_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                upload_date = pytz.utc.localize(upload_date)
                st.info(f"**CV**  \nUploaded {upload_date.strftime('%b %d, %Y')}", icon="📄")
            except Exception as e:
                st.info(f"**CV**  \nUploaded (date unavailable)", icon="📄")
            
            if st.button("View CV", key="view_cv", use_container_width=True):
                try:
                    # Get file content
                    file_data = supabase.storage.from_("documents").download(cv["file_path"])
                    
                    # Create expander for document
                    with st.expander("CV Options", expanded=True):
                        st.download_button(
                            "⬇️ Download CV",
                            file_data,
                            cv["file_name"],
                            "application/pdf" if cv["file_path"].endswith(".pdf") else "application/octet-stream",
                            use_container_width=True
                        )
                        
                        if st.button("Upload New Version", use_container_width=True):
                            st.switch_page("pages/1_Document_Upload.py")
                except Exception as e:
                    st.error(f"Error accessing document: {str(e)}")
        else:
            st.info("**CV**  \nNo CV uploaded yet", icon="📄")
            if st.button("Upload CV", key="upload_cv", use_container_width=True):
                st.switch_page("pages/1_Document_Upload.py")
    
    with doc_col2:
        if transcript:
            try:
                # Parse timestamp with timezone
                upload_date = datetime.strptime(transcript["created_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                upload_date = pytz.utc.localize(upload_date)
                st.info(f"**Transcript**  \nUploaded {upload_date.strftime('%b %d, %Y')}", icon="📄")
            except Exception as e:
                st.info(f"**Transcript**  \nUploaded (date unavailable)", icon="📄")
            
            if st.button("View Transcript", key="view_transcript", use_container_width=True):
                try:
                    # Get file content
                    file_data = supabase.storage.from_("documents").download(transcript["file_path"])
                    
                    # Create expander for document
                    with st.expander("Transcript Options", expanded=True):
                        st.download_button(
                            "⬇️ Download Transcript",
                            file_data,
                            transcript["file_name"],
                            "application/pdf" if transcript["file_path"].endswith(".pdf") else "application/octet-stream",
                            use_container_width=True
                        )
                        
                        if st.button("Upload New Version", use_container_width=True):
                            st.switch_page("pages/1_Document_Upload.py")
                except Exception as e:
                    st.error(f"Error accessing document: {str(e)}")
        else:
            st.info("**Transcript**  \nNo transcript uploaded yet", icon="📄")
            if st.button("Upload Transcript", key="upload_transcript", use_container_width=True):
                st.switch_page("pages/1_Document_Upload.py")
