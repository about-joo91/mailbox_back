from transformers import (
    AutoTokenizer,
    BertForSequenceClassification,
    TextClassificationPipeline,
)

model_name = "smilegate-ai/kor_unsmile"
model = BertForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
pipe = TextClassificationPipeline(
    model=model, tokenizer=tokenizer, device=-1, top_k=1, function_to_apply="sigmoid"
)
