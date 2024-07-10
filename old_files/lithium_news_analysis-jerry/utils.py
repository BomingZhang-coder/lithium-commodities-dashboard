import re
from newspaper import Article
import unidecode
import contractions
import en_core_web_sm
import string

spacy_nlp = en_core_web_sm.load()

def extract_article(url, language=None):
    try:
        article = Article(url)
        if language:
            article = Article(url, language='zh')
        article.download()
        article.parse()
        article.nlp()
        res = {
            'authors': article.authors,
            'date':article.publish_date,
            'title': article.title,
            'text': article.text,
            'summary': article.summary,
            'keywords': article.keywords,
        }
        return res
    except:
        return 1


def preprocess_text(text):

    # remove URLs
    text = re.sub(r'http\S+', '', text)

    # remove mentions and hashtags
    text = re.sub(r'@\w+|#\w+', '', text)

    # remove accented characters from text, e.g. café
    text = unidecode.unidecode(text)

    # expand shortened words, e.g. don't to do not
    text = contractions.fix(text)
    
    # remove punctuation and convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation)).lower()

    # remove newline characters
    text = re.sub('\n', ' ', text)

    # remove extra whitespace
    text = re.sub('\s+', ' ', text).strip()

    # # treatment for numbers
    # doc = spacy_nlp(text)
    # tokens = [w2n.word_to_num(token.text) if token.pos_ == 'NUM' else token for token in doc]
    # print(tokens)
    # text = ' '.join(tokens)

    return text


def remove_stopwords(text, sw):
    output = [i for i in text.split() if i not in sw]
    return output    

def remove_numbers(text):
    doc = spacy_nlp(' '.join(text))
    output = [token.text for token in doc if token.pos_ != 'NUM']
    return output

def stem_text(text, stemmer):
    stem_lst = [stemmer.stem(word) for word in text]
    return stem_lst

def lemmatize_text(text, lemmatizer):
    lemm_lst = [lemmatizer.lemmatize(word) for word in text]
    return lemm_lst


def url_to_clean_text(*, 
                      url: str, 
                      stopwords: list[str], 
                      lemmatizer,
                      remove_num_or_not: bool = True,
                      language: str = None,
                      ):
    """
    Keyword Only
    """
    try:
        text = extract_article(url, language)['text']
        text = preprocess_text(text)
        text = remove_stopwords(text, stopwords)
        if remove_num_or_not:
            text = remove_numbers(text)
        text = lemmatize_text(text, lemmatizer)
        return ' '.join(text)
    except:
        return 1