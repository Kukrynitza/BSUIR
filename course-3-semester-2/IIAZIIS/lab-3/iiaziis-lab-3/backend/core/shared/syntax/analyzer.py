from typing import Any
import pymorphy3
from razdel import sentenize, tokenize


class SyntaxAnalyzer:
    POS_MAP = {
        'NOUN': 'существительное',
        'ADJF': 'прилагательное',
        'ADJS': 'краткое прилагательное',
        'COMP': 'сравнительная степень',
        'VERB': 'глагол',
        'INFN': 'инфинитив',
        'PRTF': 'причастие',
        'PRTS': 'краткое причастие',
        'GRND': 'деепричастие',
        'NUMR': 'числительное',
        'NPRO': 'местоимение',
        'PRED': 'предикатив',
        'PREP': 'предлог',
        'CONJ': 'союз',
        'PRCL': 'частица',
        'INTJ': 'междометие',
        'ADVB': 'наречие',
        'PUNCT': 'пунктуация'
    }

    CASE_MAP = {
        'nomn': 'именительный',
        'gent': 'родительный',
        'datv': 'дательный',
        'accs': 'винительный',
        'ablt': 'творительный',
        'loct': 'предложный',
        'voct': 'звательный',
        'gen1': 'родительный 1',
        'gen2': 'родительный 2',
        'acc2': 'винительный 2',
        'loc1': 'предложный 1',
        'loc2': 'предложный 2'
    }

    NUMBER_MAP = {
        'sing': 'единственное',
        'plur': 'множественное'
    }

    GENDER_MAP = {
        'masc': 'мужской',
        'femn': 'женский',
        'neut': 'средний',
        'ms-f': 'общий'
    }

    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer()

    def _get_pos_name(self, pos: str) -> str:
        return self.POS_MAP.get(pos, pos)

    def _get_case_name(self, case: str) -> str:
        return self.CASE_MAP.get(case, case)

    def _get_number_name(self, number: str) -> str:
        return self.NUMBER_MAP.get(number, number)

    def _get_gender_name(self, gender: str) -> str:
        return self.GENDER_MAP.get(gender, gender)

    def _determine_syntax_role(self, pos: str, case: str | None, animacy: str | None, 
                                 word_index: int, sentence_words: list, is_punct: bool = False) -> str:
        """Определение члена предложения на основе грамматических признаков."""
        
        if is_punct or pos == 'PREP' or pos == 'CONJ' or pos == 'PRCL' or pos == 'INTJ':
            return ''
        
        if pos == 'VERB' or pos == 'INFN' or pos == 'PRTF' or pos == 'PRTS' or pos == 'GRND':
            if word_index == 1 and pos == 'VERB':
                return 'сказуемое'
            return 'сказуемое'
        
        if pos == 'ADJF' or pos == 'ADJS' or pos == 'PRTF' or pos == 'PRTS':
            return 'определение'
        
        if pos == 'ADVB':
            return 'обстоятельство'
        
        if pos == 'NUMR':
            return 'определение'
        
        if pos == 'NPRO':
            if case == 'nomn':
                return 'подлежащее'
            return 'дополнение'
        
        if pos == 'NOUN':
            if case == 'nomn':
                for prev_word in sentence_words[:word_index-1]:
                    if prev_word.get('pos') == 'VERB':
                        return 'подлежащее'
                return 'подлежащее'
            elif case in ('gent', 'datv', 'accs', 'ablt', 'loct'):
                return 'дополнение'
            return 'дополнение'
        
        return ''

    def analyze_token(self, token_text: str, word_index: int, sentence_words: list) -> dict[str, Any]:
        """Анализ одного токена."""
        
        parsed = self.morph.parse(token_text)
        
        if not parsed:
            return {
                'token': token_text,
                'pos': '',
                'pos_name': '',
                'lemma': token_text.lower(),
                'case': '',
                'number': '',
                'gender': '',
                'tense': '',
                'person': '',
                'animacy': '',
                'grammemes': {},
                'syntax_role': '',
                'syntax_role_name': ''
            }
        
        p = parsed[0]
        
        is_punctuation = not token_text.isalnum() and not token_text.isalpha()
        pos = p.tag.POS or ''
        case = p.tag.case or ''
        number = p.tag.number or ''
        gender = p.tag.gender or ''
        tense = p.tag.tense or ''
        person = p.tag.person or ''
        animacy = p.tag.animacy or ''
        
        grammemes = {}
        if case:
            grammemes['падеж'] = self._get_case_name(case)
        if number:
            grammemes['число'] = self._get_number_name(number)
        if gender:
            grammemes['род'] = self._get_gender_name(gender)
        if tense:
            grammemes['время'] = tense
        if person:
            grammemes['лицо'] = person
        if animacy:
            grammemes['одушевлённость'] = animacy
        
        syntax_role = self._determine_syntax_role(pos, case, animacy, word_index, sentence_words, is_punctuation)
        
        syntax_role_map = {
            'подлежащее': 'подлежащее',
            'сказуемое': 'сказуемое',
            'дополнение': 'дополнение',
            'определение': 'определение',
            'обстоятельство': 'обстоятельство'
        }
        
        return {
            'token': token_text,
            'pos': 'PUNCT' if is_punctuation else pos,
            'pos_name': 'пунктуация' if is_punctuation else self._get_pos_name(pos),
            'lemma': token_text if is_punctuation else p.normal_form,
            'case': case,
            'case_name': self._get_case_name(case) if case else '',
            'number': number,
            'number_name': self._get_number_name(number) if number else '',
            'gender': gender,
            'gender_name': self._get_gender_name(gender) if gender else '',
            'tense': tense,
            'person': person,
            'animacy': animacy,
            'grammemes': grammemes,
            'syntax_role': syntax_role,
            'syntax_role_name': syntax_role_map.get(syntax_role, '')
        }

    def analyze_sentence(self, sentence_text: str, sentence_index: int) -> dict[str, Any]:
        """Анализ одного предложения."""
        
        tokens = list(tokenize(sentence_text))
        
        sentence_words = []
        for i, token in enumerate(tokens):
            token_analysis = self.analyze_token(token.text, i + 1, [])
            token_analysis['position'] = i + 1
            sentence_words.append(token_analysis)
        
        for i, word in enumerate(sentence_words):
            word['sentence_position'] = i + 1
        
        return {
            'sentence_index': sentence_index + 1,
            'sentence': sentence_text,
            'tokens': sentence_words,
            'token_count': len(tokens)
        }

    def analyze_text(self, text: str) -> list[dict[str, Any]]:
        """Полный анализ текста."""
        
        sentences = list(sentenize(text))
        
        results = []
        for i, sent in enumerate(sentences):
            sentence_analysis = self.analyze_sentence(sent.text, i)
            results.append(sentence_analysis)
        
        return results

    def get_statistics(self, analysis: list[dict[str, Any]]) -> dict[str, Any]:
        """Получение статистики по анализу."""
        
        pos_stats: dict[str, int] = {}
        syntax_role_stats: dict[str, int] = {}
        total_tokens = 0
        
        for sentence in analysis:
            for token in sentence.get('tokens', []):
                total_tokens += 1
                
                pos = token.get('pos_name', '')
                if pos:
                    pos_stats[pos] = pos_stats.get(pos, 0) + 1
                
                role = token.get('syntax_role_name', '')
                if role:
                    syntax_role_stats[role] = syntax_role_stats.get(role, 0) + 1
        
        return {
            'total_sentences': len(analysis),
            'total_tokens': total_tokens,
            'pos_distribution': pos_stats,
            'syntax_role_distribution': syntax_role_stats
        }

    def detect_relations(self, tokens: list) -> list[dict[str, Any]]:
        """Определение синтаксических связей между токенами."""
        
        relations = []
        
        tokens_by_role = {
            'подлежащее': [],
            'сказуемое': [],
            'дополнение': [],
            'определение': [],
            'обстоятельство': []
        }
        
        for token in tokens:
            role = getattr(token, 'syntax_role', '') or ''
            if role in tokens_by_role:
                tokens_by_role[role].append(token)
        
        for subject in tokens_by_role['подлежащее']:
            for predicate in tokens_by_role['сказуемое']:
                if subject.position < predicate.position:
                    relations.append({
                        'from_token_id': subject.id,
                        'to_token_id': predicate.id,
                        'relation_type': 'subject-predicate',
                        'relation_name': 'подлежащее-сказуемое',
                        'description': f'"{subject.token_text}" → "{predicate.token_text}"'
                    })
        
        for predicate in tokens_by_role['сказуемое']:
            for obj in tokens_by_role['дополнение']:
                if predicate.position < obj.position:
                    relations.append({
                        'from_token_id': predicate.id,
                        'to_token_id': obj.id,
                        'relation_type': 'predicate-object',
                        'relation_name': 'сказуемое-дополнение',
                        'description': f'"{predicate.token_text}" → "{obj.token_text}"'
                    })
        
        for attribute in tokens_by_role['определение']:
            for noun in tokens_by_role['подлежащее'] + tokens_by_role['дополнение']:
                if attribute.position < noun.position and attribute.position + 1 == noun.position:
                    relations.append({
                        'from_token_id': attribute.id,
                        'to_token_id': noun.id,
                        'relation_type': 'attribute-noun',
                        'relation_name': 'определение-существительное',
                        'description': f'"{attribute.token_text}" → "{noun.token_text}"'
                    })
        
        for adverbial in tokens_by_role['обстоятельство']:
            for predicate in tokens_by_role['сказуемое']:
                relations.append({
                    'from_token_id': adverbial.id,
                    'to_token_id': predicate.id,
                    'relation_type': 'adverbial-predicate',
                    'relation_name': 'обстоятельство-сказуемое',
                    'description': f'"{adverbial.token_text}" → "{predicate.token_text}"'
                })
        
        return relations
