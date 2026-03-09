from datasets import load_dataset
from transformers import BartTokenizer, BartForConditionalGeneration, Trainer, TrainingArguments

model_name = "facebook/bart-large-cnn"

tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

dataset = load_dataset("scientific_papers", "pubmed", trust_remote_code=True)

train_ds = dataset["train"].select(range(200))
val_ds = dataset["validation"].select(range(50))

def preprocess(example):
    inputs = tokenizer(
        example["article"],
        max_length=1024,
        truncation=True,
        padding="max_length"
    )
    targets = tokenizer(
        text_target=example["abstract"],
        max_length=256,
        truncation=True,
        padding="max_length"
    )
    inputs["labels"] = targets["input_ids"]
    return inputs

train_ds = train_ds.map(preprocess, batched=False)
val_ds = val_ds.map(preprocess, batched=False)

cols = ["input_ids", "attention_mask", "labels"]
train_ds.set_format(type="torch", columns=cols)
val_ds.set_format(type="torch", columns=cols)

training_args = TrainingArguments(
    output_dir="./biomed_summarizer",
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    num_train_epochs=1,
    learning_rate=2e-5,
    logging_steps=10,
    save_steps=100,
    eval_strategy="steps",
    eval_steps=50,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds
)

trainer.train()
trainer.save_model("./biomed_summarizer")
tokenizer.save_pretrained("./biomed_summarizer")