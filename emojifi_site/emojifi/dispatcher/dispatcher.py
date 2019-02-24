import json


from emojifi.emojifiers.clap import clappify_text
from emojifi.emojifiers.spongebob import spongebobify_text
from emojifi.emojifiers.emojipasta import emojify_text


TYPE_TO_DISPATCH_FUNC = {
    'search': emojify_text,
    'clap': clappify_text,
    'spongebob': spongebobify_text,
}


def dispatch_request(request):
    """ Dispatches the POST request to the appropriate analyzer functions """
    json_request = json.loads(request.body.decode('utf-8'))
    text = json_request['text']

    if 'type' in json_request:
        dispatch_func = TYPE_TO_DISPATCH_FUNC[json_request['type']]
    else:
        dispatch_func = emojify_text

    return dispatch_func(text)
