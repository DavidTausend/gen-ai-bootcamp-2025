import unittest
from unittest.mock import patch, MagicMock
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class TestEmbeddings(unittest.TestCase):
    def setUp(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def test_embedding_generation(self):
        text = "Das ist ein Test."
        embedding = self.model.encode(text)
        self.assertEqual(len(embedding.shape), 1)
        self.assertGreater(len(embedding), 0)

    def test_cosine_similarity(self):
        text1 = "Ich liebe Programmieren."
        text2 = "Programmieren macht Spaß."
        emb1 = self.model.encode(text1)
        emb2 = self.model.encode(text2)
        similarity = util.cos_sim(torch.tensor(emb1), torch.tensor(emb2))
        self.assertGreater(similarity.item(), 0.5)

class TestTextGeneration(unittest.TestCase):
    def setUp(self):
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium')
        self.model = AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-medium')

    def test_generate_response(self):
        input_text = "Wie geht es dir?"
        input_ids = self.tokenizer.encode(input_text, return_tensors='pt')
        chat_history_ids = self.model.generate(input_ids, max_length=50, pad_token_id=self.tokenizer.eos_token_id)
        response = self.tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

class TestYouTubeTranscript(unittest.TestCase):
    @patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript')
    def test_transcript_fetch(self, mock_get_transcript):
        mock_get_transcript.return_value = [{'text': 'Hallo Welt', 'start': 0, 'duration': 5}]
        from youtube_transcript_api import YouTubeTranscriptApi

        video_id = "dummy_video_id"
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['de'])

        self.assertEqual(len(transcript), 1)
        self.assertEqual(transcript[0]['text'], 'Hallo Welt')

if __name__ == '__main__':
    unittest.main()
