from importes import Fichier
from outils import Outils
import math


class Acces(Fichier):
    """
    Classe pour l'importation des données de Contrôle Accès Equipement
    """

    cles = ['annee', 'mois', 'id_compte', 'id_user', 'id_machine', 'date_login', 'duree_machine_hp', 'duree_machine_hc',
            'duree_operateur', 'id_op', 'remarque_op', 'remarque_staff']
    nom_fichier = "cae.csv"
    libelle = "Contrôle Accès Equipement"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comptes = []
        self.sommes = {}

    def obtenir_comptes(self):
        """
        retourne la liste de tous les comptes clients
        :return: liste des comptes clients présents dans les données cae importées
        """
        if self.verifie_coherence == 0:
            info = self.libelle + ". vous devez vérifier la cohérence avant de pouvoir obtenir les comptes"
            Outils.affiche_message(info)
            return []
        return self.comptes

    def est_coherent(self, comptes, machines, users):
        """
        vérifie que les données du fichier importé sont cohérentes (id compte parmi comptes,
        id machine parmi machines), et efface les colonnes mois et année
        :param comptes: comptes importés
        :param machines: machines importées
        :param users: users importés
        :return: 1 s'il y a une erreur, 0 sinon
        """
        if self.verifie_date == 0:
            info = self.libelle + ". vous devez vérifier la date avant de vérifier la cohérence"
            Outils.affiche_message(info)
            return 1

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_list = []

        for donnee in self.donnees:
            if donnee['id_compte'] == "":
                msg += "le compte id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif comptes.contient_id(donnee['id_compte']) == 0:
                msg += "le compte id '" + donnee['id_compte'] + "' de la ligne " + str(ligne) + " n'est pas référencé\n"
            elif donnee['id_compte'] not in self.comptes:
                self.comptes.append(donnee['id_compte'])

            if donnee['id_machine'] == "":
                msg += "le machine id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif machines.contient_id(donnee['id_machine']) == 0:
                msg += "le machine id '" + donnee['id_machine'] + "' de la ligne " + str(ligne)\
                       + " n'est pas référencé\n"

            if donnee['id_user'] == "":
                msg += "le user id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif users.contient_id(donnee['id_user']) == 0:
                msg += "le user id '" + donnee['id_user'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnee['duree_machine_hp'], info = Outils.est_un_nombre(donnee['duree_machine_hp'], "la durée machine hp",
                                                                    ligne)
            msg += info
            donnee['duree_machine_hc'], info = Outils.est_un_nombre(donnee['duree_machine_hc'], "la durée machine hc",
                                                                    ligne)
            msg += info
            donnee['duree_operateur'], info = Outils.est_un_nombre(donnee['duree_operateur'],
                                                                   "la durée opérateur", ligne)
            msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_list.append(donnee)

            ligne += 1

        self.donnees = donnees_list
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0

    def calcul_montants(self, machines, categprix, clients, verification, comptes):
        """
        calcule les sous-totaux nécessaires
        :param machines: machines importées
        :param categprix: catégories prix importés et vérifiés
        :param clients: clients importés et vérifiés
        :param verification: pour vérifier si les dates et les cohérences sont correctes
        :param comptes: comptes importés

        """
        if verification.a_verifier != 0:
            info = self.libelle + ". vous devez faire les vérifications avant de calculer les montants"
            Outils.affiche_message(info)
            return

        donnees_list = []
        pos = 0
        for donnee in self.donnees:
            id_compte = donnee['id_compte']
            id_user = donnee['id_user']
            id_machine = donnee['id_machine']
            code_client = comptes.donnees[id_compte]['code_client']
            machine = machines.donnees[id_machine]
            client = clients.donnees[code_client]
            prix_mach = categprix.donnees[client['nature'] + machine['id_cat_mach']]['prix_unit']

            if code_client not in self.sommes:
                self.sommes[code_client] = {'comptes': {}, 'machines': {}}
            scl = self.sommes[code_client]['comptes']
            if id_compte not in scl:
                scl[id_compte] = {}
            sco = scl[id_compte]

            if id_machine not in sco:
                du_hc = round(prix_mach * machine['tx_rabais_hc'] / 100, 2)
                sco[id_machine] = {'duree_hp': 0, 'duree_hc': 0, 'mo': 0, 'runs': 0, 'users': {},
                                   'du_hc': du_hc}
            sco[id_machine]['duree_hp'] += donnee['duree_machine_hp']
            sco[id_machine]['duree_hc'] += donnee['duree_machine_hc']
            sco[id_machine]['mo'] += donnee['duree_operateur']
            if donnee['duree_machine_hp'] > 0 or donnee['duree_machine_hc'] > 0:
                sco[id_machine]['runs'] += 1

            scm = sco[id_machine]['users']

            if id_user not in scm:
                scm[id_user] = {'duree_hp': 0, 'duree_hc': 0, 'mo': 0, 'data': []}

            scm[id_user]['duree_hp'] += donnee['duree_machine_hp']
            scm[id_user]['duree_hc'] += donnee['duree_machine_hc']
            scm[id_user]['mo'] += donnee['duree_operateur']
            scm[id_user]['data'].append(pos)

            scma = self.sommes[code_client]['machines']
            if id_machine not in scma:
                pur_hp = round(prix_mach * machine['tx_penalite_hp'] / 100, 2)
                pur_hc = round(prix_mach * machine['tx_penalite_hc'] / 100 *
                               (1 - machine['tx_rabais_hc'] / 100), 2)
                du_hc = round(prix_mach * machine['tx_rabais_hc'] / 100, 2)
                scma[id_machine] = {'duree_hp': 0, 'duree_hc': 0, 'pur_hp': pur_hp, 'pur_hc': pur_hc, 'du_hc': du_hc,
                                    'dhm': 0, 'users': {}}
            scma[id_machine]['duree_hp'] += donnee['duree_machine_hp']
            scma[id_machine]['duree_hc'] += donnee['duree_machine_hc']

            scmu = scma[id_machine]['users']
            if id_user not in scmu:
                scmu[id_user] = {'duree_hp': 0, 'duree_hc': 0, 'comptes': {}}
            scmu[id_user]['duree_hp'] += donnee['duree_machine_hp']
            scmu[id_user]['duree_hc'] += donnee['duree_machine_hc']

            if id_compte not in scmu[id_user]['comptes']:
                scmu[id_user]['comptes'][id_compte] = {'duree_hp': 0, 'duree_hc': 0}
            scmu[id_user]['comptes'][id_compte]['duree_hp'] += donnee['duree_machine_hp']
            scmu[id_user]['comptes'][id_compte]['duree_hc'] += donnee['duree_machine_hc']

            donnees_list.append(donnee)
            pos += 1
        self.donnees = donnees_list

        for code_client in self.sommes:
            client = clients.donnees[code_client]
            for id_machine in self.sommes[code_client]['machines']:
                scm = self.sommes[code_client]['machines'][id_machine]
                scm['dhm'] += math.ceil(scm['du_hc'] * scm['duree_hc'] / 60)

            self.sommes[code_client]['categories'] = {}
            for id_compte in self.sommes[code_client]['comptes']:
                sco = self.sommes[code_client]['comptes'][id_compte]
                if id_compte not in self.sommes[code_client]['categories']:
                    self.sommes[code_client]['categories'][id_compte] = {}
                scat = self.sommes[code_client]['categories'][id_compte]
                scat['machine'] = {}
                scat['operateur'] = {}
                scat['plateforme'] = {}
                scat['xcher'] = {}
                for id_machine in sco:
                    machine = machines.donnees[id_machine]
                    sco[id_machine]['dhi'] = round(sco[id_machine]['duree_hc'] / 60 * sco[id_machine]['du_hc'], 2)
                    cat_mach = machine['id_cat_mach']
                    cat_mo = machine['id_cat_mo']
                    cat_plat = machine['îd_cat_plat']
                    cat_cher = machine['id_cat_cher']
                    nat = client['nature']

                    if cat_mach not in scat['machine']:
                        prix_mach = categprix.donnees[nat + cat_mach]['prix_unit']
                        scat['machine'][cat_mach] = {'pk': round(prix_mach, 2), 'quantite': 0, 'mk': 0,
                                                     'duree_hp': 0, 'duree_hc': 0, 'mo': 0}

                    if cat_mo not in scat['operateur']:
                        prix_mo = categprix.donnees[nat + cat_mo]['prix_unit']
                        scat['operateur'][cat_mo] = {'pk': round(prix_mo, 2), 'quantite': 0, 'mk': 0}

                    if cat_plat not in scat['plateforme']:
                        prix_plat = categprix.donnees[nat + cat_plat]['prix_unit']
                        scat['plateforme'][cat_plat] = {'pk': round(prix_plat, 2), 'quantite': 0, 'mk': 0}

                    if cat_cher not in scat['xcher']:
                        prix_cher = categprix.donnees[nat + cat_cher]['prix_unit']
                        scat['xcher'][cat_cher] = {'pk': round(prix_cher, 2), 'quantite': 0, 'mk': 0}

                    scat['machine'][cat_mach]['duree_hp'] += sco[id_machine]['duree_hp']
                    scat['machine'][cat_mach]['duree_hc'] += sco[id_machine]['duree_hc']
                    scat['machine'][cat_mach]['mo'] += sco[id_machine]['mo']
                    scat['machine'][cat_mach]['quantite'] += sco[id_machine]['duree_hp']
                    scat['machine'][cat_mach]['quantite'] += sco[id_machine]['duree_hc']
                    scat['operateur'][cat_mo]['quantite'] += sco[id_machine]['mo']
                    scat['plateforme'][cat_plat]['quantite'] += sco[id_machine]['runs']
                    scat['xcher'][cat_cher]['quantite'] += sco[id_machine]['duree_hp']
                    scat['xcher'][cat_cher]['quantite'] += sco[id_machine]['duree_hc']

                for id_categorie in scat['machine']:
                    scat['machine'][id_categorie]['mk'] = round(
                        2 * scat['machine'][id_categorie]['quantite'] / 60 * scat['machine'][id_categorie]['pk'],
                        1) / 2
                for id_categorie in scat['operateur']:
                    scat['operateur'][id_categorie]['mk'] = round(
                        2 * scat['operateur'][id_categorie]['quantite'] / 60 * scat['operateur'][id_categorie]['pk'],
                        1) / 2
                for id_categorie in scat['plateforme']:
                    scat['plateforme'][id_categorie]['mk'] = round(
                        2 * scat['plateforme'][id_categorie]['quantite'] * scat['plateforme'][id_categorie]['pk'],
                        1) / 2
                for id_categorie in scat['xcher']:
                    scat['xcher'][id_categorie]['mk'] = round(
                        2 * scat['xcher'][id_categorie]['quantite'] / 60 * scat['xcher'][id_categorie]['pk'],
                        1) / 2

    def acces_pour_compte(self, id_compte, code_client):
        """
        retourne toutes les données cae pour un compte donné
        :param id_compte: l'id du compte du projet
        :param code_client: le code client du compte
        :return: les données cae pour le projet donné
        """
        donnees_list = []
        for donnee in self.donnees:
            if (donnee['id_compte'] == id_compte) and (donnee['code_client'] == code_client):
                donnees_list.append(donnee)
        return donnees_list
