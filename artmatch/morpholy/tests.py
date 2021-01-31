from django.test import TestCase
from django.urls import reverse


class IndexViewTests(TestCase):
    def test_full_post(self):
        url = reverse('morpholy:index')
        post_data = {
            "text": "大きな男の人に声をかける、素早い女の人",
            "select_part": [
                "名詞",
                "動詞",
                "形容詞"]}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertContains(response, "名詞")
        self.assertContains(response, "声")

        self.assertContains(response, "動詞")
        self.assertContains(response, "かける")

        self.assertContains(response, "形容詞")
        self.assertContains(response, "素早い")

    def test_noun_post(self):
        url = reverse('morpholy:index')
        post_data = {"text": "大きな男の人に声をかける、素早い女の人", "select_part": ["名詞"]}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertContains(response, "名詞")
        self.assertContains(response, "声")

        self.assertNotContains(response, "動詞")
        self.assertNotContains(response, "かける")

        self.assertNotContains(response, "形容詞")
        self.assertNotContains(response, "素早い")

    def test_verb_post(self):
        url = reverse('morpholy:index')
        post_data = {"text": "大きな男の人に声をかける、素早い女の人", "select_part": ["動詞"]}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertNotContains(response, "名詞")
        self.assertNotContains(response, "声")

        self.assertContains(response, "動詞")
        self.assertContains(response, "かける")

        self.assertNotContains(response, "形容詞")
        self.assertNotContains(response, "素早い")

    def test_adjective_post(self):
        url = reverse('morpholy:index')
        post_data = {"text": "大きな男の人に声をかける、素早い女の人", "select_part": ["形容詞"]}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertNotContains(response, "名詞")
        self.assertNotContains(response, "声")

        self.assertNotContains(response, "動詞")
        self.assertNotContains(response, "かける")

        self.assertContains(response, "形容詞")
        self.assertContains(response, "素早い")

    def test_noun_verb_post(self):
        url = reverse('morpholy:index')
        post_data = {
            "text": "大きな男の人に声をかける、素早い女の人",
            "select_part": [
                "名詞",
                "動詞"]}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertContains(response, "名詞")
        self.assertContains(response, "声")

        self.assertContains(response, "動詞")
        self.assertContains(response, "かける")

        self.assertNotContains(response, "形容詞")
        self.assertNotContains(response, "素早い")

    def test_noun_adjective_post(self):
        url = reverse('morpholy:index')
        post_data = {
            "text": "大きな男の人に声をかける、素早い女の人",
            "select_part": [
                "名詞",
                "形容詞"]}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertContains(response, "名詞")
        self.assertContains(response, "声")

        self.assertNotContains(response, "動詞")
        self.assertNotContains(response, "かける")

        self.assertContains(response, "形容詞")
        self.assertContains(response, "素早い")

    def test_verb_adjective_post(self):
        url = reverse('morpholy:index')
        post_data = {
            "text": "大きな男の人に声をかける、素早い女の人",
            "select_part": [
                "動詞",
                "形容詞"]}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertNotContains(response, "名詞")
        self.assertNotContains(response, "声")

        self.assertContains(response, "動詞")
        self.assertContains(response, "かける")

        self.assertContains(response, "形容詞")
        self.assertContains(response, "素早い")

    def test_nothing_post(self):
        url = reverse('morpholy:index')
        post_data = {"text": "", "select_part": []}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertContains(response, "名詞")
        self.assertNotContains(response, "声")

        self.assertContains(response, "動詞")
        self.assertNotContains(response, "かける")

        self.assertContains(response, "形容詞")
        self.assertNotContains(response, "素早い")

        self.assertContains(response, "出力項目を選んでください")

    def test_no_select_part_post(self):
        url = reverse('morpholy:index')
        post_data = {"text": "大きな男の人に声をかける、素早い女の人", "select_part": []}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertContains(response, "名詞")
        self.assertContains(response, "動詞")
        self.assertContains(response, "形容詞")
        self.assertContains(response, "出力項目を選んでください")

    def test_no_text_post(self):
        url = reverse('morpholy:index')
        post_data = {"text": "", "select_part": ["名詞"]}

        response = self.client.post(
            url, post_data, follow=True)

        self.assertContains(response, "名詞")
        self.assertContains(response, "動詞")
        self.assertContains(response, "形容詞")
        self.assertNotContains(response, "出力項目を選んでください")
