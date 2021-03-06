from bs4 import BeautifulSoup
from copy import copy
from string import digits
import requests

PARTS_OF_SPEECH = [
    "noun", "verb", "adjective", "adverb", "determiner",
    "article", "preposition", "conjunction", "proper noun",
    "letter", "character", "phrase", "proverb", "idiom",
    "symbol", "syllable", "numeral", "initialism", "interjection",
    "definitions", "pronoun", "particle", "predicative", "participle",
    "suffix",
]


class EnglishWiktionaryParser(object):
    def __init__(self):
        self.url = "https://en.wiktionary.org/wiki/{}?printable=yes"
        self.soup = None
        self.session = requests.Session()
        self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))
        self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))
        self.language = 'english'
        self.current_word = None
        self.PARTS_OF_SPEECH = copy(PARTS_OF_SPEECH)
        self.INCLUDED_ITEMS = self.PARTS_OF_SPEECH + ['etymology', 'pronunciation']

    def clean_html(self):
        unwanted_classes = ['sister-wikipedia', 'thumb', 'reference', 'cited-source']
        for tag in self.soup.find_all(True, {'class': unwanted_classes}):
            tag.extract()

    @staticmethod
    def remove_digits(string):
        return string.translate(str.maketrans('', '', digits)).strip()

    def get_id_list(self, contents, content_type):
        if content_type == 'etymologies':
            checklist = ['etymology']
        elif content_type == 'pronunciation':
            checklist = ['pronunciation']
        elif content_type == 'definitions':
            checklist = self.PARTS_OF_SPEECH
        else:
            return None
        # Если нет оглавления, то content_id ищем на самой странице
        if len(contents) == 0:
            return [('1', x.title(), x) for x in checklist if self.soup.find('span', {'id': x.title()})]
        # Поиск content_id в оглавлении
        id_list = []
        for content_tag in contents:
            content_index = content_tag.find_previous().text
            text_to_check = self.remove_digits(content_tag.text).strip().lower()
            if text_to_check in checklist:
                content_id = content_tag.parent['href'].replace('#', '')
                id_list.append((content_index, content_id, text_to_check))
        return id_list

    def get_word_data(self):
        contents = self.soup.find_all('span', {'class': 'toctext'})
        word_contents = []
        start_index = None
        for content in contents:
            if content.text.lower() == self.language:
                start_index = content.find_previous().text + '.'
        if not start_index:
            if contents:
                return []
            language_heading = self.soup.find_all(
                "span",
                {"class": "mw-headline"},
                string=lambda s: s.lower() == self.language
            )
            if not language_heading:
                return []
        for content in contents:
            index = content.find_previous().text
            content_text = self.remove_digits(content.text.lower())
            if index.startswith(start_index) and (content_text in self.INCLUDED_ITEMS):
                word_contents.append(content)
        word_data = {
            'examples': self.parse_examples(word_contents),
            'definitions': self.parse_definitions(word_contents),
            'pronunciations': self.parse_pronunciations(word_contents),
        }
        json_obj_list = self.map_to_object(word_data)
        return json_obj_list

    def parse_pronunciations(self, word_contents):
        pronunciation_id_list = self.get_id_list(word_contents, 'pronunciation')
        pronunciation_list = []
        audio_links = []
        pronunciation_text = []
        pronunciation_div_classes = ['mw-collapsible', 'vsSwitcher']
        for pronunciation_index, pronunciation_id, _ in pronunciation_id_list:
            span_tag = self.soup.find_all('span', {'id': pronunciation_id})[0]
            list_tag = span_tag.parent
            while list_tag.name != 'ul':
                list_tag = list_tag.find_next_sibling()
                if list_tag.name == 'p':
                    pronunciation_text.append(list_tag.text)
                    break
                if list_tag.name == 'div' and any(_ in pronunciation_div_classes for _ in list_tag['class']):
                    break
            list_tags = []
            for list_element in list_tag.find_all('li'):
                for nested_list_element in list_element.find_all('ul'):
                    list_tags.append(nested_list_element.extract())
            for super_tag in list_tag.find_all('sup'):
                super_tag.clear()
            list_tags += list_tag.find_all('li')
            for list_element in list_tags:
                for audio_tag in list_element.find_all('div', {'class': 'mediaContainer'}):
                    audio_links.append(audio_tag.find('source')['src'])
                    audio_tag.extract()
                if list_element.text and not list_element.find('table', {'class': 'audiotable'}):
                    prev_end = 0
                    while list_element.text.find('/', prev_end):
                        transcription_start_index = list_element.text.find('/', prev_end)
                        if transcription_start_index < prev_end:
                            break
                        transcription_end_index = list_element.text.find('/', transcription_start_index + 1)
                        pronunciation_text.append(
                            list_element.text[transcription_start_index:transcription_end_index + 1])
                        prev_end = transcription_end_index + 1
            pronunciation_list.append((pronunciation_index, pronunciation_text, audio_links))
        return pronunciation_list

    def parse_definitions(self, word_contents):
        definition_id_list = self.get_id_list(word_contents, 'definitions')
        definition_list = []
        definition_tag = None
        for def_index, def_id, def_type in definition_id_list:
            definition_text = []
            span_tag = self.soup.find_all('span', {'id': def_id})[0]
            table = span_tag.parent.find_next_sibling()
            while table and table.name not in ['h3', 'h4', 'h5']:
                definition_tag = table
                table = table.find_next_sibling()
                if definition_tag.name == 'p':
                    if definition_tag.text.strip():
                        definition_text.append(definition_tag.text.strip())
                if definition_tag.name in ['ol', 'ul']:
                    for element in definition_tag.find_all('li', recursive=False):
                        if element.text:
                            definition_text.append(element.text.strip())
            if def_type == 'definitions':
                def_type = ''
            definition_list.append((def_index, definition_text, def_type))
        return definition_list

    def fetch(self, word):
        response = self.session.get(self.url.format(word))
        self.soup = BeautifulSoup(response.text.replace('>\n<', '><'), 'html.parser')
        self.current_word = word
        self.clean_html()
        return self.get_word_data()