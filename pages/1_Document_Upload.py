import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from pages.components.document_parser import parse_uploaded_file
from io import BytesIO
from datetime import datetime

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
    layout="wide"
)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    if st.button("Return to Welcome"):
        st.experimental_set_query_params()
        st.rerun()
    st.stop()

# Header
st.title("Upload Your Documents")
st.write("Upload your CV and transcript to get started")

def upload_and_analyze(file, doc_type: str, is_replacement: bool = False):
    """Upload file to storage and analyze content."""
    try:
        print(f"\nProcessing {doc_type} file: {type(file)}")
        
        # Get file content immediately
        file_data = file.getvalue()
        if not file_data:
            raise ValueError("Empty file")
        print(f"File data type: {type(file_data)}, length: {len(file_data)}")
            
        file_type = os.path.splitext(file.name)[1].lower()
        print(f"File type: {file_type}")
        
        # Include timestamp in filename to make it unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = f"{st.session_state.user.id}/{doc_type}_{timestamp}{file_type}"
        
        # Upload to storage
        try:
            print(f"Attempting upload to {file_path}")
            
            # If this is a replacement, try to clean up old files first
            if is_replacement:
                try:
                    # List files in user's directory
                    old_files = supabase.storage.from_("documents").list(st.session_state.user.id)
                    # Find and delete old files of same document type
                    for old_file in old_files:
                        if old_file["name"].startswith(f"{doc_type}_"):
                            old_path = f"{st.session_state.user.id}/{old_file['name']}"
                            supabase.storage.from_("documents").remove([old_path])
                            print(f"Deleted old file: {old_path}")
                except Exception as delete_error:
                    print(f"Error cleaning up old files: {str(delete_error)}")
            
            # Upload new file
            result = supabase.storage.from_("documents").upload(
                file_path,
                file_data
            )
            print("Upload result:", result)
            st.write("✅ File uploaded to storage")
            
        except Exception as upload_error:
            print(f"Detailed upload error: {str(upload_error)}")
            raise Exception(f"Storage upload failed: {str(upload_error)}")
        
        # Save document reference
        doc_data = {
            "user_id": st.session_state.user.id,
            "document_type": doc_type,
            "file_path": file_path,
            "file_name": file.name,
            "file_type": file_type
        }
        print(f"Saving document reference: {doc_data}")
        
        # If replacement, update existing record
        if is_replacement:
            doc_result = supabase.table("user_documents").update(doc_data).match({
                "user_id": st.session_state.user.id,
                "document_type": doc_type
            }).execute()
        else:
            doc_result = supabase.table("user_documents").insert(doc_data).execute()
        
        if not doc_result.data:
            st.error("Error saving document reference")
            return
            
        document_id = doc_result.data[0]["id"]
        st.write("✅ Document reference saved")
        
        # Create fresh BytesIO object for parsing
        parse_file = BytesIO(file_data)
        parse_file.name = file.name
        
        # Parse document
        with st.spinner(f"Analyzing {doc_type}..."):
            print("Starting document analysis...")
            analysis = parse_uploaded_file(parse_file, file_type, doc_type)
            print("Document parsed successfully")
            st.write("✅ Document parsed")
            
            # Prepare analysis data
            analysis_data = {
                "user_id": st.session_state.user.id,
                "document_id": document_id,
                "document_type": doc_type,
                "parsed_data": analysis,
                "status": "complete"
            }
            print(f"Saving analysis: {analysis_data}")
            
            try:
                # If replacement, delete old analysis first
                if is_replacement:
                    try:
                        supabase.table("document_analysis").delete().match({
                            "user_id": st.session_state.user.id,
                            "document_type": doc_type
                        }).execute()
                        print("Deleted old analysis record")
                    except Exception as e:
                        print(f"Error deleting old analysis: {str(e)}")
                
                # Insert new analysis
                analysis_result = supabase.table("document_analysis").insert(analysis_data).execute()
                
                if not analysis_result.data:
                    st.error("Error saving document analysis")
                    return
                    
                st.success(f"✅ {doc_type.upper()} uploaded and analyzed successfully!")
                
                # Show analysis preview
                with st.expander("View Analysis Results"):
                    st.json(analysis)
                    
            except Exception as analysis_error:
                print(f"Error saving analysis: {str(analysis_error)}")
                st.error("Error saving analysis results")
                
    except Exception as e:
        print(f"Error in upload_and_analyze: {str(e)}")
        st.error(f"Error processing document: {str(e)}")

# Document upload sections
col1, col2 = st.columns(2)

with col1:
    st.write("### CV")
    
    # Check if CV exists
    cv = supabase.table("user_documents").select("*").eq("user_id", st.session_state.user.id).eq("document_type", "cv").execute()
    has_cv = bool(cv.data)
    
    if has_cv:
        st.success("CV uploaded!", icon="✅")
        
        # Show analysis status
        analysis = supabase.table("document_analysis").select("*").eq("document_id", cv.data[0]["id"]).execute()
        if analysis.data:
            if analysis.data[0]["status"] == "complete":
                st.info("CV analyzed successfully")
                with st.expander("View Analysis"):
                    st.json(analysis.data[0]["parsed_data"])
            elif analysis.data[0]["status"] == "error":
                st.warning(f"Error analyzing CV: {analysis.data[0]['error_message']}")
            else:
                st.info("CV analysis in progress...")
        
        # Replace CV section
        uploaded_cv = st.file_uploader("Replace CV", type=["pdf", "docx", "doc"], key="cv_replace")
        if uploaded_cv and st.button("Upload and Process New CV"):
            upload_and_analyze(uploaded_cv, "cv", is_replacement=True)
    else:
        # New CV upload section
        uploaded_cv = st.file_uploader("Upload CV", type=["pdf", "docx", "doc"], key="cv_new")
        if uploaded_cv and st.button("Upload and Process CV"):
            upload_and_analyze(uploaded_cv, "cv", is_replacement=False)

with col2:
    st.write("### Transcript")
    
    # Check if transcript exists
    transcript = supabase.table("user_documents").select("*").eq("user_id", st.session_state.user.id).eq("document_type", "transcript").execute()
    has_transcript = bool(transcript.data)
    
    if has_transcript:
        st.success("Transcript uploaded!", icon="✅")
        
        # Show analysis status
        analysis = supabase.table("document_analysis").select("*").eq("document_id", transcript.data[0]["id"]).execute()
        if analysis.data:
            if analysis.data[0]["status"] == "complete":
                st.info("Transcript analyzed successfully")
                with st.expander("View Analysis"):
                    st.json(analysis.data[0]["parsed_data"])
            elif analysis.data[0]["status"] == "error":
                st.warning(f"Error analyzing transcript: {analysis.data[0]['error_message']}")
            else:
                st.info("Transcript analysis in progress...")
        
        # Replace transcript section
        uploaded_transcript = st.file_uploader("Replace Transcript", type=["pdf", "docx", "doc"], key="transcript_replace")
        if uploaded_transcript and st.button("Upload and Process New Transcript"):
            upload_and_analyze(uploaded_transcript, "transcript", is_replacement=True)
    else:
        # New transcript upload section
        uploaded_transcript = st.file_uploader("Upload Transcript", type=["pdf", "docx", "doc"], key="transcript_new")
        if uploaded_transcript and st.button("Upload and Process Transcript"):
            upload_and_analyze(uploaded_transcript, "transcript", is_replacement=False)
