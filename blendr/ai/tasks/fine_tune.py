# from ai.data.data_loader import load_data, prepare_data
# from ai.training.trainer import train
import os
import tarfile
import requests
from ai.data.cache import setup_local_cache
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
from blendr.initiate_socket.initiate import sio
from blendr.config.settings import SERVER_URL


def fine_tune(task_details):
    try:
        base_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'cache')
        results_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'results')
        save_dir = os.path.join(results_dir, 'saved_model')

        model_cache = setup_local_cache({
            'model': task_details['aiModel']['url'],
            'config': task_details['aiModel']['configUrl'],
            'tokenizer': task_details['aiModel']['otherUrl']['tokenizerConfig'],
            'vocab': task_details['aiModel']['otherUrl']['vocab'],
            'special_tokens_map': task_details['aiModel']['otherUrl']['specialTokensMap']
        })

        sio.emit('BMAIN: logs', {'taskId':task_details['id'], 'message': 'Model and tokenizer cache setup complete'})

        # Load tokenizer and model using local paths
        tokenizer = AutoTokenizer.from_pretrained(base_path)
        model = AutoModelForSequenceClassification.from_pretrained(base_path)
        sio.emit('BMAIN: logs', {'taskId':task_details['id'], 'message': 'Model and tokenizer loaded'})

        # Setup cache and load datasets
        data_cache = setup_local_cache({
            'train_data': task_details['trainingData']['trainingDataUrl'],
            'validation_data': task_details['trainingData']['validationDataUrl']
        })
        sio.emit('BMAIN: logs', {'taskId':task_details['id'], 'message': 'Data cache setup complete'})

        dataset = load_dataset('csv', data_files={
            'train': data_cache['train_data'],
            'validation': data_cache['validation_data']
        })
        sio.emit('BMAIN: logs', {'taskId':task_details['id'], 'message': 'Dataset loaded and ready for processing'})

        # Tokenize the text
        tokenized_datasets = dataset.map(lambda examples: tokenizer(examples['text'], padding="max_length", truncation=True, max_length=512), batched=True)
        sio.emit('BMAIN: logs', {'taskId':task_details['id'], 'message': 'Tokenization complete'})

        # Define training arguments
        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=task_details['trainingParameters']['numEpochs'],
            per_device_train_batch_size=task_details['trainingParameters']['batchSize'],
            per_device_eval_batch_size=task_details['trainingParameters']['batchSize'],
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=10,
        )

        # Initialize the Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets['train'],
            eval_dataset=tokenized_datasets['validation']
        )
        sio.emit('BMAIN: logs', {'taskId':task_details['id'], 'message': 'Trainer initialized, starting training'})

        # Train the model
        trainer.train()
        sio.emit('BMAIN: logs', {'taskId':task_details['id'], 'message': 'Training complete'})


        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        model.save_pretrained(save_dir)
        tokenizer.save_pretrained(save_dir)
        sio.emit('BMAIN: logs', {'taskId': task_details['id'], 'message': 'Model and tokenizer saved'})

        # Compress the saved model and tokenizer into a folder
        compressed_file = results_dir + '.tar.gz'
        with tarfile.open(compressed_file, 'w:gz') as tar:
            tar.add(results_dir, arcname=os.path.basename(results_dir))

        sio.emit('BMAIN: logs', {'taskId': task_details['id'], 'message': 'Model and tokenizer compressed'})

        # Generate presigned URL
        response = requests.post(SERVER_URL + '/api/generate/presigned-url', json={'fileType': 'tar.gz', 'fileName': os.path.basename(compressed_file)})
        presigned_url = response.text
        if not presigned_url:
            raise Exception('Failed to get presigned URL')

        # Upload the folder to S3 using the presigned URL
        with open(compressed_file, 'rb') as f:
            upload_response = requests.put(presigned_url, data=f)
        if upload_response.status_code != 200:
            raise Exception('Failed to upload the model and tokenizer')

        sio.emit('BMAIN: logs', {'taskId': task_details['id'], 'message': 'Model and tokenizer uploaded to S3'})

        # # Notify server with the link to the uploaded folder
        # uploaded_url = presigned_url.split('?')[0]
        # requests.post(SERVER_URL + 'api/notify-upload', json={'taskId': task_details['id'], 'url': uploaded_url})

        sio.emit('BMAIN: logs', {'taskId': task_details['id'], 'message': 'Server notified with the upload link'})



    except Exception as e:
        sio.emit('BMAIN: execute_error', {'message': str(e), 'taskId': task_details['id'],'nodeId': task_details['nodeId']})
        sio.emit('error', {'message': str(e), 'taskId': task_details['id'],'nodeId': task_details['nodeId']})
        print(f"An error occurred during task execution: {str(e)}")
