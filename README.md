# LLM Benchamrk Dataset

This project extracts text from PDF files, splits it into chunks, and uses the Mistral-7B LLM to generate multiple-choice questions with answers.

## Features

- 📄 **PDF Processing**: Extracts and chunks PDF content (3 pages per chunk with 1-page overlap)
- 🤖 **LLM**: Uses Mistral-7B-Instruct model for question generation


## How to Use

1. **Open the Notebook**: `mcq_generator.ipynb`

2. **Run the Cells in Order**:

   - **Cell 1-2**: Load helper functions
   - **Cell 3**: Extract and chunk your PDF (change the PDF filename here)
   - **Cell 4-6**: Load LLM
   - **Cell 7**: Generate MCQs and save to CSV

3. **Check Output**:
   - MCQs are saved to: `mcq_dataset.csv`
   - PDF chunks are saved to: `pdf_chunks.json`

## Output Format

The CSV file contains:

- PDF name
- Chunk and page numbers
- Question text
- 4 answer options (A, B, C, D)
- Correct answer (formatted as "D) Option text")

## Files

- `mcq_generator.ipynb` - Main notebook to run
- `mcq_dataset.csv` - Generated MCQ output
- `pdf_chunks.json` - Processed PDF chunks
- `LLM_cs124_week7_2025.pdf` - Example input PDF