from transformers import AutoTokenizer, BertForSequenceClassification, TextClassificationPipeline


class UnsmileFiltering:
    def __init__(self):
        self.model_name = "smilegate-ai/kor_unsmile"
        self.model = BertForSequenceClassification.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.pipe = TextClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            device=-1,
            top_k=1,
            function_to_apply="sigmoid",
        )

    def unsmile_filter(self, contents):
        return self.pipe(contents)[0]


post_filtering = UnsmileFiltering()
