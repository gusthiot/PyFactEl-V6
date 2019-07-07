from outils import Outils


class RecaProjet(object):
    """
    Classe pour la création du récapitulatif des projets
    """

    @staticmethod
    def recap(dossier_destination, nom, lignes):
        """
        création du récapitulatif des projets
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param nom: nom du fichier de récapitulation
        :param lignes: lignes de données du détail
        """

        with dossier_destination.writer(nom + ".csv") as fichier_writer:

            ligne = ["Plateforme", "Année", "Mois", "Référence", "Code Client", "Abrev. client", "Projet",
                     "Type", "Intitulé", "Quantité", "Unité", "Prix unitaire", "Montant"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def creation_lignes(edition, somme_client, client, generaux, acces, livraisons, comptes, categories):
        """
        génération des lignes de données du récapitulatif
        :param edition: paramètres d'édition
        :param somme_client: sommes par comptes calculées pour un client donné
        :param client: client donné
        :param generaux: paramètres généraux
        :param acces: accès importés
        :param livraisons: livraisons importées
        :param comptes: comptes importés
        :param categories: catégories importées
        :return: lignes de données du récapitulatif
        """

        lignes = []

        code_client = client['code']
        comptes_utilises = Outils.comptes_in_somme(somme_client, comptes)
        nature = generaux.code_ref_par_code_n(client['nature'])
        ref = nature + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
        if edition.version > 0:
            ref += "-" + str(edition.version)
        base_client = [generaux.centre, edition.annee, edition.mois, ref, client['code_sap'], client['abrev_labo']]

        for num_compte, id_compte in sorted(comptes_utilises.items()):
            compte = comptes.donnees[id_compte]
            base_compte = base_client + [num_compte + " - " + compte['intitule']]

            if code_client in acces.sommes and id_compte in acces.sommes[code_client]['categories']:

                for cat, som_cats in sorted(acces.sommes[code_client]['categories'][id_compte].items()):
                    for id_categorie, som_cat in sorted(som_cats.items()):
                        unite = categories.donnees[id_categorie]['unite']
                        montant = som_cat['mk']
                        if unite == 'hh_mm':
                            quantite = som_cat['quantite']/1440
                        else:
                            quantite = som_cat['quantite']
                        if montant > 0:
                            ligne = base_compte + ['Services', categories.donnees[id_categorie]['intitule'],
                                                   quantite, unite, som_cat['pk'], montant]
                            lignes.append(ligne)

            if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                somme = livraisons.sommes[code_client][id_compte]

                for article in generaux.articles_d3:
                    if article.code_d in somme:
                        if article.code_d == 'C':
                            base_article = base_compte + ['Consumables']
                        else:
                            base_article = base_compte + ['Other']
                        for no_prestation, sip in sorted(somme[article.code_d].items()):
                            if sip['montant'] > 0:
                                ligne = base_article + [str(no_prestation) + " - " + sip['nom'], sip['quantite'],
                                                        sip['unite'], sip['pn'], (sip['montant'] - sip['rabais'])]
                                lignes.append(ligne)

        return lignes
