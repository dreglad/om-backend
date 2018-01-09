import requests


class DistributionProvider(object):  
    """
    DistributionProvider. Base class for publishing/distributing
    """
    def __init__(self, stream):
        self.stream = stream
        self.provider = eval(stream.provider + "Provider")

    def retrieve(self):
        return self.provider(self.stream).retrieve()

    def save(self):
        pass

    def create(self):
        pass


class MultimediaProvider(object):
    def __init__(self, stream):
        self.stream = stream.metadata['api_url']

        self.api = self.stream.metadata.

    def retrieve(self):
        return 
