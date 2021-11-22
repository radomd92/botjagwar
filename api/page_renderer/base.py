from api.model.word import Entry


class PageRenderer(object):
    def render(self, info: Entry) -> str:
        raise NotImplementedError()