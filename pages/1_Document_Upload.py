import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

# Page config
st.set_page_config(
    page_title="Document Upload - WhiteCoat",
    page_icon="📄",
    layout="centered"
)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()

# Main content
st.title("Document Upload")

# Document type selection
doc_type = st.radio(
    "Select document type",
    ["CV", "Transcript"],
    horizontal=True
)

# File upload
uploaded_file = st.file_uploader(f"Upload your {doc_type}", type=["pdf", "doc", "docx"])

if uploaded_file:
    try:
        # Construct file path
        file_path = f"documents/{st.session_state.user.id}/{doc_type.lower()}/{uploaded_file.name}"
        
        # Check if file exists and delete it
        try:
            supabase.storage.from_("documents").remove([file_path])
        except Exception as e:
            # Ignore error if file doesn't exist
            pass
            
        # Upload new file
        supabase.storage.from_("documents").upload(
            file_path,
            uploaded_file.getvalue()
        )
        
        # Save document reference
        data = {
            "user_id": st.session_state.user.id,
            "document_type": "cv" if doc_type == "CV" else "transcript",
            "file_path": file_path,  # Changed from storage_path to file_path
            "file_name": uploaded_file.name,
            "file_type": uploaded_file.type if hasattr(uploaded_file, 'type') else None
        }
        
        # Check if document already exists
        existing = supabase.table("user_documents").select("*").eq("user_id", st.session_state.user.id).eq("document_type", data["document_type"]).execute()
        
        if existing.data:
            # Update existing document
            result = supabase.table("user_documents").update(data).eq("id", existing.data[0]["id"]).execute()
        else:
            # Insert new document
            result = supabase.table("user_documents").insert(data).execute()
        
        st.success(f"{doc_type} uploaded successfully!")
        
        # Show next steps
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Upload Another Document"):
                st.rerun()
        with col2:
            if st.button("Continue to Profile"):
                st.switch_page("pages/2_Profile.py")
                
    except Exception as e:
        st.error(f"Error uploading document: {str(e)}")
        # Log full error for debugging
        st.write("Debug info:")
        st.write(e)
else:
    # Show existing documents
    docs = supabase.table("user_documents").select("*").eq("user_id", st.session_state.user.id).execute()
    if docs.data:
        st.write("### Your Documents")
        for doc in docs.data:
            doc_name = "CV" if doc["document_type"] == "cv" else "Transcript"
            st.info(f"**{doc_name}**: {doc['file_name']}", icon="📄")
