from ciphers.midori import Midori

# Sbox and linear layer are the same as for Midori

class Mantis(Midori):

    def __init__(self):
        super().__init__()
        self.name = "Mantis"
