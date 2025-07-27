import streamlit as st
from ocr_to_summary import NoteProcessor
import os
from PIL import Image
import cv2

def main():
    """Streamlit dashboard for note processing."""
    st.set_page_config(page_title="Note to Summary Converter", layout="wide")
    st.title("📝 Note to Summary Converter")

    # Initialize processor
    processor = NoteProcessor()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        ocr_model = st.selectbox("OCR Model", ["tesseract", "pytesseract"], index=0)
        gpt_format = st.selectbox("Output Format", ["summary", "outline", "teaching", "qa"])
        prompt_style = st.selectbox("Prompt Style", ["default", "teaching_12yo", "technical"])
        uploaded_file = st.file_uploader("Upload Image/PDF", type=["png", "jpg", "jpeg", "pdf"])
        focus_region = st.checkbox("Highlight Focus Region")
        output_format = st.selectbox("Download Format", ["txt", "md", "pdf"])
        output_filename = st.text_input("Output Filename", value="output")

    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Input Preview")
        if uploaded_file:
            file_path = f"temp_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(file_path)
                st.image(img, caption="Uploaded Image", use_column_width=True)
            
            # Process file
            if st.button("Process File"):
                raw_text, summary, flashcards, layout = processor.process_file(
                    file_path, ocr_model, gpt_format, prompt_style
                )
                st.session_state.raw_text = raw_text
                st.session_state.summary = summary
                st.session_state.flashcards = flashcards
                os.remove(file_path)

    with col2:
        st.header("Output")
        if 'raw_text' in st.session_state:
            st.subheader("Raw OCR Text")
            raw_text_edit = st.text_area("Edit OCR Text", st.session_state.raw_text, height=200)
            if st.button("Reprocess Edited Text"):
                st.session_state.summary = processor.process_file(
                    None, ocr_model, gpt_format, prompt_style, raw_text=raw_text_edit
                )[1]
            
            st.subheader("Processed Summary")
            st.write(st.session_state.summary)
            
            if st.session_state.flashcards:
                st.subheader("Flashcards")
                for i, card in enumerate(st.session_state.flashcards, 1):
                    st.write(f"**Q{i}**: {card['question']}")
                    st.write(f"**A{i}**: {card['answer']}")
            
            if st.button("Download Output"):
                processor.save_output(st.session_state.summary, output_format, f"{output_filename}.{output_format}")
                with open(f"outputs/{output_filename}.{output_format}", "rb") as f:
                    st.download_button(
                        label=f"Download {output_format.upper()}",
                        data=f.read(),
                        file_name=f"{output_filename}.{output_format}",
                        mime="text/plain" if output_format in ['txt', 'md'] else "application/pdf"
                    )

    # History
    st.header("Processing History")
    for entry in processor.history[-5:]:
        st.write(f"[{entry['timestamp']}] {entry['file_path']} ({entry['gpt_format']})")
        if st.button(f"View Summary {entry['timestamp']}"):
            st.write(entry['summary'])

if __name__ == '__main__':
    main()