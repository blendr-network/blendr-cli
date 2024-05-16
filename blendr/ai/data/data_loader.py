import pandas as pd
from transformers import DistilBertTokenizer

def load_data(file_path):
    """
    Load data from a CSV file.
    Args:
    - file_path (str): The file path to the CSV file.

    Returns:
    - data (pd.DataFrame): The loaded data.
    """
    data = pd.read_csv(file_path)
    return data

def prepare_data(data, tokenizer_path):
    """
    Tokenize and prepare data using DistilBERT tokenizer.
    Args:
    - data (pd.DataFrame): The data to be tokenized.
    - tokenizer_path (str): Path to the tokenizer.

    Returns:
    - tokenized_data (dict): Tokenized data prepared for DistilBERT input.
    """
    tokenizer = DistilBertTokenizer.from_pretrained(tokenizer_path)
    tokenized_data = tokenizer(data['text'].tolist(), add_special_tokens=True, truncation=True, padding=True, return_tensors="pt")
    return tokenized_data
