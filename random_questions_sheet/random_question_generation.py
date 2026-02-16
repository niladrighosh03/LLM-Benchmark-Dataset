import pandas as pd
import glob
import os

# Define the target CSV files and their corresponding sheet names
# Excluding falcon as requested
# Current directory is random_questions_sheet/
datasets = {
    'mistral': '../results/without_image/mistral_mcq_dataset.csv',
    'phi': '../results/without_image/phi_mcq_dataset.csv',
    'qween': '../results/without_image/qween_mcq_dataset.csv',
    'llama': '../results/without_image/llama_mcq_dataset.csv'
}

output_file = 'manual_evaluation.xlsx'

# Create a Pandas Excel writer using XlsxWriter as the engine
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    for sheet_name, csv_path in datasets.items():
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found. Skipping.")
            continue
            
        print(f"Processing {sheet_name} from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        if len(df.columns) >= 9:
            # Add original row number (1-based index)
            df['Original_Row_Number'] = df.index + 2 # +2 considering header and 0-based index
            
            # Limit to first 195 rows
            df = df.head(195)
            
            # The CSV header has 10 columns but data effectively aligns to 9 columns + 1 NaN
            # Index mapping based on debug:
            # 3: Question
            # 4: Option A
            # 5: Option B
            # 6: Option C
            # 7: Option D
            # 8: Correct Answer
            
            # Select relevant columns by index
            # We need to include the new 'Original_Row_Number' column
            # It's the last column added
            row_num_idx = len(df.columns) - 1
            
            # Reorder to put Row Number first
            df_corrected = df.iloc[:, [row_num_idx, 3, 4, 5, 6, 7, 8]].copy()
            df_corrected.columns = ['Original_Row_Number', 'question', 'option_A', 'option_B', 'option_C', 'option_D', 'correct_answer']
            
            # Additional check: ensure 'question' column looks like a string
            df_corrected['question'] = df_corrected['question'].astype(str)
            
        else:
            print(f"Warning: {sheet_name} has unexpected column count {len(df.columns)}. Skipping or trying standard parsing.")
            # Fallback to name based if the file is fixed later? 
            # For now, let's assume all follow the observed broken pattern
            continue

        # Sample 20 random rows
        if len(df_corrected) > 20:
            final_df = df_corrected.sample(n=20, random_state=42).copy()
        else:
            final_df = df_corrected.copy()
        
        # Add blank columns for manual scoring
        final_df['Quality_Score'] = ''
        final_df['Difficulty_Score'] = ''
        
        # Write to Excel
        final_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Add formatting
        # Set column width
        worksheet.set_column('A:A', 10) # Row Number
        worksheet.set_column('B:B', 50) # Question column
        worksheet.set_column('C:F', 20) # Options
        worksheet.set_column('G:G', 15) # Answer
        worksheet.set_column('H:I', 15) # Scores

print(f"Successfully created {output_file}")
