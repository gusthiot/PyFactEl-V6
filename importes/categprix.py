from importes import Fichier
from outils import Outils


class CategPrix(Fichier):
    """
    Classe pour l'importation des données de Catégories Prix
    """

    nom_fichier = "categprix.csv"
    cles = ['nature', 'id_categorie', 'prix_unit']
    libelle = "Catégories Prix"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, generaux, categories):
        """
        vérifie que les données du fichier importé sont cohérentes,
        et efface les colonnes mois et année
        :param generaux: paramètres généraux
        :param categories: catégories importées
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        natures = []
        couples = []
        ids = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['nature'] == "":
                msg += "la nature client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['nature'] not in generaux.obtenir_code_n():
                msg += "la nature client de la ligne " + str(ligne) + " n'existe pas dans les codes N\n"
            elif donnee['nature'] not in natures:
                if donnee['nature'] not in natures:
                    natures.append(donnee['nature'])
                else:
                    msg += "la nature '" + donnee['nature'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            if donnee['id_categorie'] == "":
                msg += "l'id catégorie " + str(ligne) + " ne peut être vide\n"
            elif categories.contient_id(donnee['id_categorie']) == 0:
                msg += "l'id catégori de la ligne " + str(ligne) + " n'existe pas dans les catégories \n"
            elif donnee['id_categorie'] not in ids:
                ids.append(donnee['id_categorie'])

            if (donnee['id_categorie'] != "") and (donnee['nature'] != ""):
                couple = [donnee['id_categorie'], donnee['nature']]
                if couple not in couples:
                    couples.append(couple)
                else:
                    msg += "Couple id catégorie '" + donnee['id_categorie'] + "' et nature '" + \
                           donnee['nature'] + "' de la ligne " + str(ligne) + " pas unique\n"

            donnee['prix_unit'], info = Outils.est_un_nombre(donnee['prix_unit'], "le prix unitaire ", ligne)
            msg += info

            donnees_dict[donnee['nature'] + donnee['id_categorie']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        for code_n in generaux.obtenir_code_n():
            if code_n not in natures:
                msg += "La nature '" + code_n + "' dans les paramètres généraux n'est pas présente dans " \
                                                         "les catégories prix\n"

        for id_cat in ids:
            for nature in natures:
                couple = [id_cat, nature]
                if couple not in couples:
                    msg += "Couple id catégorie '" + id_cat + "' et nature client '" + \
                           nature + "' n'existe pas\n"

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
