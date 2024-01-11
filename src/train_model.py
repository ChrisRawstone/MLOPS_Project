
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset, load_metric
import torch
import numpy as np
from accelerate import Accelerator  # Import the Accelerator class
# import hydra


#@hydra.main(config_path="conf", config_name="config")

def main():
    
    # Check if CUDA is available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device = torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu')
    print(f'Using device: {device}')

    # Load the tokenizer
    tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

    # Function to tokenize the input texts
    def tokenize_and_format(examples):
        # Tokenize the inputs and add the labels
        tokenized_inputs = tokenizer(examples['text'], padding='max_length', truncation=True)
        tokenized_inputs['labels'] = examples['generated']
        return tokenized_inputs

    # Load datasets
    train_dataset = load_dataset('csv', data_files='data/processed/train.csv')['train']
    test_dataset = load_dataset('csv', data_files='data/processed/test.csv')['train']

    # Tokenize datasets
    train_dataset = train_dataset.map(tokenize_and_format, batched=True)
    test_dataset = test_dataset.map(tokenize_and_format, batched=True)

    # Load the model
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
    model.to(device)

    # Define training arguments
    #@hydre
   
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
    )

    # Define the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset
    )

    # Train the model
    trainer.train()

    # Evaluate the model
    trainer.evaluate()






if __name__ == '__main__':

    main()

    