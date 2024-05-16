from transformers import AdamW, get_scheduler

def train(model, data, epochs, batch_size, learning_rate):
    """
    Train a DistilBERT model.
    Args:
    - model: The DistilBERT model to be trained.
    - data: The tokenized dataset.
    - epochs (int): Number of training epochs.
    - batch_size (int): Size of each training batch.
    - learning_rate (float): The learning rate for the optimizer.

    Returns:
    - model: The trained model.
    """
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    
    for epoch in range(epochs):
        for i in range(0, len(data['input_ids']), batch_size):
            batch = {k: v[i:i+batch_size] for k, v in data.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item()}")
    
    return model
