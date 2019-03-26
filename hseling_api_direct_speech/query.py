from bs4 import BeautifulSoup


def query_data(query_type, contents, tags):
    if isinstance(contents, bytes):
        text = contents.decode('utf-8')
    else:
        text = contents
    tree = read_xml(text)
    if query_type == "tags":
        return {"tags": get_tags_from(tree, tags)}
    elif query_type == "statistics":
        return get_statistics(tree)
    elif query_type == "examples":
        return {"tags": get_examples(tree, tags)}
    else:
        return {"error": "incorrect query type"}


def get_tags_from(tree, tag_with_param):
    tag = tag_with_param["tag"]
    if "param" in tag_with_param:
        return [i.text for i in tree.findAll(tag, tag_with_param["param"])]
    else:
        return [i.text for i in tree.findAll(tag)]


def get_statistics(tree):
    result = {}
    tags_with_params = {"speech": [],
                        "said": [{"type": "direct"}, {"type": "indirect"},
                                 {"aloud": "true"}, {"aloud": "false"}],
                        "author_comment": [],
                        "speech_verb": [{"semantic": "speech"},
                                        {"semantic": "action"},
                                        {"semantic": "thought"},
                                        {"semantic": "song"},
                                        {"emotion": "neutral"},
                                        {"emotion": "loud"},
                                        {"emotion": "rude"},
                                        {"emotion": "sad"},
                                        {"emotion": "interrupt"},
                                        {"emotion": "yes"},
                                        {"emotion": "no"},
                                        {"emotion": "emotional"},
                                        {"emotion": "question"}]}
    for tag in tags_with_params:
        result[tag] = len(tree.findAll(tag))
        for param in tags_with_params[tag]:
            str_param = "_".join([k + "_" + v for k, v in param.items()])
            result[tag + "_" + str_param] = len(tree.findAll(tag, param))
    return result


def get_examples(tree, tags):
    result = {}
    for tag in tags:
        result[tag] = [str(i) for i in tree.findAll(tag)]
    return result


def read_xml(text):
    return BeautifulSoup('<text>' + text + '</text>', "lxml")
