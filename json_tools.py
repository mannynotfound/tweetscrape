import io, json

def save_json(route, filename, data):
    with io.open('data/{}/{}.json'.format(route, filename),
                 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))

def load_json(route, filename):
    with io.open('data/{}/{}.json'.format(route, filename),
                 encoding='utf-8') as f:
        return json.load(f)

