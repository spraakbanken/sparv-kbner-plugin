
from sparv.api import annotator, get_logger, Output, Annotation

from transformers import pipeline

from sparv_kbner_plugin import interleave_tags_and_tokens

logger = get_logger(__name__)


SENT_SEP = "\n"
TOK_SEP = " "


nlp = pipeline(
    "ner",
    model="KBLab/bert-base-swedish-cased-ner",
    tokenizer="KBLab/bert-base-swedish-cased-ner",
)


@annotator("Named entity tagging with KB-BERT-NER", language=["swe"])
def annotate(
    out_ne_type: Output = Output(
        "<token>:sparv_kbner.ne_type",
        cls="named_entity",
        description="Named entity segment types from KB-BERT-NER",
    ),
    out_ne_score: Output = Output(
        "<token>:sparv_kbner.ne_score",
        cls="named_entity",
        description="Named entity segment types from KB-BERT-NER",
    ),
    word: Annotation = Annotation("<token:word>"),
    sentence: Annotation = Annotation("<sentence>"),
):
    print("sparv_kbner")
    logger.debug("word: %s", word)
    # out_ne.write(["hello"])
    parse_kb_ner_output(
        sentence=sentence, word=word, out_ne_type=out_ne_type, out_ne_score=out_ne_score
    )
    # raise RuntimeError("impl")


def parse_kb_ner_output(
    sentence: Annotation, word: Annotation, out_ne_type: Output, out_ne_score: Output
):
    sentences, _orphans = sentence.get_children(word)
    token_word = list(word.read())
    # sentences_to_tag = [
    #     TOK_SEP.join(token_word[token_index] for token_index in sent)
    #     for sent in sentences
    # ]
    # Escape <, > and &
    # sentences_to_tag = xml.sax.saxutils.escape(sentences_to_tag)
    # stdout = run_nlp(stdin)
    out_type_annotation = word.create_empty_attribute()
    out_score_annotation = word.create_empty_attribute()
    # for sent, sent_to_tag in zip(sentences, sentences_to_tag, strict=True):
    for sent in sentences:
        sent_to_tag = TOK_SEP.join(token_word[token_index] for token_index in sent)
        # tagged_tokens = interleave_tags_and_tokens(
        #     run_nlp_on_sentence(sent_to_tag), token_word, sent, sent_to_tag
        # )
        # tagged_tokens = run_nlp_on_tokens(token_word, sent)
        # logger.debug("tagged_tokens = %s", tagged_tokens)
        # logger.debug("sent = %s", sent)
        # for token_index, tagged_token in zip(sent, tagged_tokens, strict=True):
        for token_index, tag, score in interleave_tags_and_tokens(
            run_nlp_on_sentence(sent_to_tag), token_word, sent
        ):
            # logger.debug(
            #     "token_index = %d, tagged_token = (%s,%s), token_word = %s",
            #     token_index,
            #     tag,
            #     score,
            #     token_word[token_index],
            # )
            # tag = tagged_token.strip().split(TAG_SEP)[TAG_COLUMN]
            # tag = tag_mapping.get(tag, tag)
            out_type_annotation[token_index] = tag
            out_score_annotation[token_index] = score

    logger.info("writing annotations")
    out_ne_type.write(out_type_annotation)
    out_ne_score.write(out_score_annotation)



def run_nlp_on_sentence(sentence: str) -> list[dict]:
    logger.info("run_nlp_on_sentence(len(sentence)='%d') called", len(sentence))
    tokens = []
    # linking_token = ""
    found_link = False
    for token in nlp(sentence):
        # logger.debug("nlp: token = %s", token)
        if token["word"].startswith("##"):
            # logger.debug("found ## in %s", token["word"])
            if tokens and token["start"] == tokens[-1]["end"]:
                tokens[-1]["word"] += token["word"][2:]
                tokens[-1]["end"] = token["end"]
            # else:
            #     logger.info(
            #         "found ## in '%s' (start=%d, end=%d) but no prev token, skipping ... ",
            #         token["word"],
            #         token["start"],
            #         token["end"],
            #     )
            # tokens.append(Token(**token))
        elif found_link:
            # logger.debug("found '%s' before word '%s'", linking_token, token["word"])
            found_link = False
            if token["start"] == tokens[-1]["end"]:
                tokens[-1]["word"] += token["word"]
                tokens[-1]["end"] = token["end"]
                # amend_token_to_last(token, tokens)
            else:
                tokens.append(token)
        elif token["word"] in [",", ".", "-"]:
            # linking_token = token["word"]
            # logger.debug("found '%s'", linking_token)
            found_link = True
            if token["start"] == tokens[-1]["end"]:
                tokens[-1]["word"] += token["word"]
                tokens[-1]["end"] = token["end"]
                # amend_token_to_last(token, tokens)
            else:
                tokens.append(token)
        else:
            tokens.append(token)
        # logger.debug("tokens[-1].word = %s", tokens[-1].word)
        # logger.debug("tokens = %s", tokens)
    return tokens


def find_word_ending(sentence: str, token_end: int) -> int:
    """Find first whitespace from token_end or above."""
    while token_end < len(sentence) and sentence[token_end] != " ":
        token_end += 1
    return token_end


def find_next_token(tokens: list, curr_token: int, curr: int) -> int:
    next_token = curr_token + 1
    while next_token < len(tokens) and tokens[next_token].start < curr:
        next_token += 1
    return next_token


TAGS = {"PER": "PRS"}


def translate_tag(tag: str) -> str:
    return TAGS.get(tag) or tag
