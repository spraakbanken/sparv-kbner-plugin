from typing import Optional
from sparv_kbner.core import (
    # Token,
    find_word_ending,
    # interleave_tags_and_sentence,
    interleave_tags_and_tokens,
    run_nlp_on_sentence,
    # run_nlp_on_tokens,
)
import pytest


SENTENCES = {
    "ikea": "Ikea ( namnet är bildat av initialerna för Ingvar Kamprad Elmtaryd Agunnaryd ) är ett multinationellt möbelföretag som grundades 1943 av Ingvar Kamprad .",  # noqa: E501
    "verksamhetsåret": "Under verksamhetsåret 2012 omsatte Ikeakoncernen 241 miljarder kronor .",  # noqa: E501
    "kammerling": "– Jag tycker att Sveriges landslag ska vara nöjda , säger experten Anna-Karin Kammerling till Sveriges Radio .",  # noqa: E501
    "gruppen": "Gruppen föreslår ändringar i reglerna för 2,7 miljarder kronor .",
    "belarusen": "Poliser grep sedan två personer på flygplanet , belarusen Roman Protasevitj och hans flickvän Sofia Sapega .",  # noqa: E501
    "det-börjar": "Den börjar klockan 19.15 .",
    "encrochat": "Det programmet heter Encrochat .",
    "artisterna": "Det är till exempel artisterna Tusse , Dotter och Kikki Danielsson .",  # noqa: E501
    "street-race": "Filmerna handlar bland annat om olagliga tävlingar med bilar som kallas street-race .",  # noqa: E501
    "kvinnolobby": "Det säger Clara Berglund som är ledare för gruppen Sveriges kvinnolobby .",  # noqa: E501
    "internet": "Det går också att kolla klockan på internet på sajten 90510.se .",
}


@pytest.mark.parametrize(
    "sentence_name, token_end, expected",
    [("verksamhetsåret", 21, 21), ("verksamhetsåret", 39, 48), ("encrochat", 28, 30)],
)
def test_find_word_ending(sentence_name: str, token_end: int, expected: int) -> None:
    sentence = SENTENCES[sentence_name]

    assert find_word_ending(sentence, token_end) == expected
    assert sentence[find_word_ending(sentence, token_end)] == " "





@pytest.mark.parametrize(
    "sentence_name, expected_tags",
    [
        (
            "belarusen",
            [
                (9,"PRS"),
                (10,"PRS"),
                (14,"PRS"),
                (15,"PRS"),
            ],
        ),
        ("det-börjar", [(2,"TME"), (3,"TME")]),
        # ("encrochat", [None, None, None, "PRS", None]),
        (
            "artisterna",
            [
                (5,"PRS"),
                (6,"PRS"),  # TODO Should this be None?,
                (7,"PRS"),
                (8,"PRS"),  # TODO Should this be None?,
                (9,"PRS"),
                (10,"PRS"),
            ],
        ),
        (
            "street-race",
            [
                (11,"EVN",)
            ],
        ),
        (
            "kvinnolobby",
            [(2,"PRS"), (3,"PRS"), (9, "LOC")],
        ),
        (
            "internet",
            [
                (10,"WRK"),
            ],
        ),
    ],
)
def test_interleave_tags_and_tokens_run_nlp_on_sentence(
    sentence_name: str, expected_tags: list[Optional[str]]
) -> None:
    sentence = SENTENCES[sentence_name]
    token_word = sentence.split(" ")
    sent = list(range(len(token_word)))
    result = interleave_tags_and_tokens(
        run_nlp_on_sentence(sentence), token_word, sent
    )
    tags = [(t[0],t[1]) for t in result]
    assert tags == expected_tags
