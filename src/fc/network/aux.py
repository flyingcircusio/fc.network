"""Auxiliary configurations like mactab, udev, ..."""


class AuxiliaryConfig():

    def generate(self):
        return []


class Demux(AuxiliaryConfig):

    def register(self):
        pass


class Mactab(AuxiliaryConfig):

    def register(self):
        pass


class Udev(AuxiliaryConfig):

    def register(self):
        pass
