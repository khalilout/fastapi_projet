import factory
from faker import Faker

fake = Faker("fr_FR")


class UtilisateurDataFactory(factory.Factory):

    class Meta:
        model = dict

    email = factory.LazyFunction(lambda: fake.unique.email())
    mot_de_passe = "azerty123"
    role = "etudiant"


class EntrepriseDataFactory(UtilisateurDataFactory):
    role = "entreprise"
    nom_entreprise = factory.LazyFunction(lambda: fake.company())


class ResponsableDataFactory(UtilisateurDataFactory):
    role = "responsable_pedagogique"


class OffreDataFactory(factory.Factory):

    class Meta:
        model = dict

    titre = factory.LazyFunction(lambda: fake.job())
    mission = factory.LazyFunction(lambda: fake.sentence(nb_words=8))
    competences_requises = factory.LazyFunction(lambda: fake.word())
