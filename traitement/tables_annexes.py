from outils import Outils
from latex import Latex


class TablesAnnexes(object):

    @staticmethod
    def table_tps_res_xmu(code_client, reservations, machines, users):
        """
        Tps RES X/M/U - Table Client Détail Temps Réservations/Machine/User
        :param code_client: code du client concerné
        :param reservations: réservations importées
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """

        if code_client in reservations.sommes:
            structure = r'''{|c|c|c|c|c|}'''
            legende = r'''Détail des réservations machines par utilisateur'''
            contenu = r'''
                \cline{4-5}
                \multicolumn{3}{c}{} & \multicolumn{2}{|c|}{Durée réservée} \\
                \cline{4-5}
                \multicolumn{3}{c|}{} & HP & HC \\
                \hline
                '''

            somme = reservations.sommes[code_client]

            machines_reservees = Outils.machines_in_somme(somme, machines)

            for id_categorie, mics in sorted(machines_reservees.items()):
                for nom_machine, id_machine in sorted(mics.items()):

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'hp': Outils.format_heure(somme[id_machine]['res_hp']),
                                    'hc': Outils.format_heure(somme[id_machine]['res_hc'])}
                    contenu += r'''
                            \multicolumn{3}{|l|}{\textbf{%(machine)s}} & \hspace{5mm} %(hp)s &
                            \hspace{5mm} %(hc)s \\
                            \hline
                            ''' % dico_machine

                    utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                    for nom, upi in sorted(utilisateurs.items()):
                        for prenom, ids in sorted(upi.items()):
                            for id_user in sorted(ids):
                                smu = somme[id_machine]['users'][id_user]
                                dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                             'hp': Outils.format_heure(smu['res_hp']),
                                             'hc': Outils.format_heure(smu['res_hc'])}
                                contenu += r'''
                                        \multicolumn{3}{|l|}{\hspace{5mm} %(user)s} & %(hp)s & %(hc)s \\
                                        \hline
                                        ''' % dico_user
                                for p1 in smu['data']:
                                    res = reservations.donnees[p1]
                                    login = Latex.echappe_caracteres(res['date_debut']).split()
                                    temps = login[0].split('-')
                                    date = temps[0]
                                    for p2 in range(1, len(temps)):
                                        date = temps[p2] + '.' + date
                                    if len(login) > 1:
                                        heure = login[1]
                                    else:
                                        heure = ""

                                    sup = ""
                                    if res['date_suppression'] != "":
                                        sup = "Supprimé le : " + res['date_suppression']
                                    dico_pos = {'date': date, 'heure': heure, 'sup': Latex.echappe_caracteres(sup),
                                                'hp': Outils.format_heure(res['duree_fact_hp']),
                                                'hc': Outils.format_heure(res['duree_fact_hc'])}
                                    contenu += r'''
                                                \hspace{10mm} %(date)s & %(heure)s & %(sup)s & %(hp)s \hspace{5mm} &
                                                 %(hc)s \hspace{5mm} \\
                                                \hline
                                            ''' % dico_pos

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_tps_m_cae_xmu(code_client, acces, contenu_cae_xmu):
        """
        Tps_M CAE X/M/U - Table Client Récap Temps mach avec pénalités /Machine/User
        :param code_client: code du client concerné
        :param acces: accès importés
        :param contenu_cae_xmu: contenu généré pour cette table
        :return: table au format latex
        """

        if code_client in acces.sommes and contenu_cae_xmu != "":
            structure = r'''{|l|c|c|}'''
            legende = r'''Récapitulatif des utilisations machines par utilisateur'''
            contenu = r'''
                \cline{2-3}
                \multicolumn{1}{c|}{} & HP & HC \\
                \hline'''

            contenu += contenu_cae_xmu

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_tps_penares_xmu(code_client, scl, sommes_acces, sommes_reservations, machines, users):
        """
        Tps Penares X/M/U - Table Client Durées Pénalités réserv./Machine/User
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_acces: sommes des accès importés
        :param sommes_reservations: sommes des réservations importées
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """

        if code_client in sommes_reservations:
            structure = r'''{|l|c|c|c|c|c|c|}'''
            legende = r'''Statistiques des réservations et des utilisations machines'''
            contenu = r'''
                \cline{3-7}
                \multicolumn{2}{c}{} & \multicolumn{3}{|c|}{Réservation} & Utilisation & Pénalités \\
                \hline
                 & & Durée & Taux & Util. Min. & Durée & Durée \\
                \hline'''

            ac_somme = None
            if code_client in sommes_acces:
                ac_somme = sommes_acces[code_client]['machines']

            machines_utilisees = Outils.machines_in_somme(scl['res'], machines)

            for id_categorie, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    re_hp = sommes_reservations[code_client][id_machine]['res_hp']
                    re_hc = sommes_reservations[code_client][id_machine]['res_hc']
                    tx_hp = machines.donnees[id_machine]['tx_occ_eff_hp']
                    tx_hc = machines.donnees[id_machine]['tx_occ_eff_hc']

                    ac_hp = 0
                    ac_hc = 0
                    if ac_somme and id_machine in ac_somme:
                        ac_hp = ac_somme[id_machine]['duree_hp']
                        ac_hc = ac_somme[id_machine]['duree_hc']

                    tot_hp = scl['res'][id_machine]['tot_hp']
                    tot_hc = scl['res'][id_machine]['tot_hc']

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'ac_hp': Outils.format_heure(ac_hp), 'ac_hc': Outils.format_heure(ac_hc),
                                    're_hp': Outils.format_heure(re_hp), 're_hc': Outils.format_heure(re_hc),
                                    'tot_hp': Outils.format_heure(tot_hp), 'tot_hc': Outils.format_heure(tot_hc)}

                    sclu = scl['res'][id_machine]['users']
                    utilisateurs = Outils.utilisateurs_in_somme(sclu, users)

                    if re_hp > 0:
                        contenu += r'''
                            %(machine)s & HP & \hspace{5mm} %(re_hp)s & & & \hspace{5mm} %(ac_hp)s
                            & \hspace{5mm} %(tot_hp)s \\
                             \hline
                             ''' % dico_machine

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    ac = sclu[id_user]['ac_hp']
                                    re = sclu[id_user]['re_hp']
                                    mini = sclu[id_user]['mini_hp']
                                    tot = sclu[id_user]['tot_hp']
                                    if ac > 0 or re > 0:
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'ac': Outils.format_heure(ac),
                                                     're': Outils.format_heure(re), 'tx': tx_hp,
                                                     'mini': Outils.format_heure(mini),
                                                     'tot': Outils.format_heure(tot)}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & HP & %(re)s & %(tx)s & %(mini)s & %(ac)s
                                            & %(tot)s \\
                                            \hline
                                            ''' % dico_user

                    if re_hc > 0:
                        contenu += r'''
                            %(machine)s & HC & \hspace{5mm} %(re_hc)s & & & \hspace{5mm} %(ac_hc)s
                            & \hspace{5mm} %(tot_hc)s  \\
                             \hline
                             ''' % dico_machine

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    ac = sclu[id_user]['ac_hc']
                                    re = sclu[id_user]['re_hc']
                                    mini = sclu[id_user]['mini_hc']
                                    tot = sclu[id_user]['tot_hc']
                                    if ac > 0 or re > 0:
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'ac': Outils.format_heure(ac),
                                                     're': Outils.format_heure(re), 'tx': tx_hc,
                                                     'mini': Outils.format_heure(mini),
                                                     'tot': Outils.format_heure(tot)}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & HC & %(re)s & %(tx)s & %(mini)s & %(ac)s
                                            & %(tot)s \\
                                            \hline
                                            ''' % dico_user

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def contenu_tps_m_cae_xmu(code_client, scl, sommes_acces, machines, users, comptes):
        """
        contenu Tps_M CAE X/M/U - Table Client Récap Temps mach avec pénalités /Machine/User
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_acces: sommes des accès importés
        :param machines: machines importées
        :param users: users importés
        :param comptes: comptes importés
        :return: contenu
        """

        contenu = ""
        if code_client in sommes_acces:
            somme = sommes_acces[code_client]['machines']
            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_categorie, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    if id_machine in scl['res']:
                        pur_hp = somme[id_machine]['pur_hp']
                        pur_hc = somme[id_machine]['pur_hc']
                        tx_hp = machines.donnees[id_machine]['tx_occ_eff_hp']
                        tx_hc = machines.donnees[id_machine]['tx_occ_eff_hc']
                        if (pur_hc > 0 and tx_hc > 0) or (pur_hp > 0 and tx_hp > 0):
                            dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                            'hp': Outils.format_heure(somme[id_machine]['duree_hp']),
                                            'hc': Outils.format_heure(somme[id_machine]['duree_hc'])}
                            contenu += r'''
                               \textbf{%(machine)s} & \hspace{5mm} %(hp)s & \hspace{5mm} %(hc)s \\
                                \hline
                                ''' % dico_machine

                            utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                            for nom, upi in sorted(utilisateurs.items()):
                                for prenom, ids in sorted(upi.items()):
                                    for id_user in sorted(ids):
                                        smu = somme[id_machine]['users'][id_user]
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'hp': Outils.format_heure(smu['duree_hp']),
                                                     'hc': Outils.format_heure(smu['duree_hc'])}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & %(hp)s & %(hc)s \\
                                            \hline
                                            ''' % dico_user

                                        comptes_utilises = Outils.comptes_in_somme(smu['comptes'], comptes)

                                        for num_compte, id_compte in sorted(comptes_utilises.items()):
                                            smuc = smu['comptes'][id_compte]
                                            compte = comptes.donnees[id_compte]
                                            intitule_compte = Latex.echappe_caracteres(compte['numero']
                                                                                       + " - " + compte['intitule'])
                                            dico_compte = {'compte': intitule_compte,
                                                           'hp': Outils.format_heure(smuc['duree_hp']),
                                                           'hc': Outils.format_heure(smuc['duree_hc'])}
                                            contenu += r'''
                                                \hspace{10mm} %(compte)s & %(hp)s \hspace{5mm} & %(hc)s \hspace{5mm} \\
                                                \hline
                                                ''' % dico_compte
        return contenu

    @staticmethod
    def table_prix_xaj(scl, generaux, contenu_prix_xaj):
        """
        Prix XA/J - Table Client Récap Articles/Compte
        :param scl: sommes client calculées
        :param generaux: paramètres généraux
        :param contenu_prix_xaj: contenu généré de la table
        :return: table au format latex
        """

        structure = r'''{|l|l|r|r|'''
        legende = r'''Récapitulatif des projets'''

        contenu = r'''
            \hline
            Projet & Type & \multicolumn{1}{c|}{Procédés}'''

        for article in generaux.articles_d3:
            structure += r'''r|'''
            contenu += r''' & \multicolumn{1}{c|}{
            ''' + Latex.echappe_caracteres(article.intitule_court) + r'''}'''
        structure += r'''}'''
        contenu += r'''& \multicolumn{1}{c|}{Total} \\
            \hline
            '''

        contenu += contenu_prix_xaj

        dico = {'procedes': Outils.format_2_dec(scl['mt']),
                'total': Outils.format_2_dec((scl['somme_t']-scl['r']-scl['e']))}

        contenu += r'''Total article & & %(procedes)s''' % dico

        for categorie in generaux.codes_d3():
            contenu += r''' & ''' + Outils.format_2_dec(scl['tot_cat'][categorie])

        contenu += r'''& %(total)s \\
            \hline
            ''' % dico

        return Latex.long_tableau(contenu, structure, legende)

    @staticmethod
    def table_prix_xf(scl, generaux, filtre, contenu_prix_xf):
        """
        Prix XF - Table Client Récap Postes de la facture
        :param scl: sommes client calculées
        :param generaux: paramètres généraux
        :param filtre: si nul pour code n
        :param contenu_prix_xf: contenu généré de la table
        :return: table au format latex
        """

        brut = scl['rm'] + scl['somme_t_mm'] + scl['em']
        for cat, tt in scl['sommes_cat_m'].items():
            brut += tt
        if scl['somme_t'] > 0 or (filtre == "NON" and brut > 0):
            structure = r'''{|c|l|r|r|r|}'''
            legende = r'''Récapitulatif des postes de la facture'''

            dico = {'emom': Outils.format_2_dec(scl['em']), 'emor': Outils.format_2_dec(scl['er']),
                    'emo': Outils.format_2_dec(scl['e']), 'resm': Outils.format_2_dec(scl['rm']),
                    'resr': Outils.format_2_dec(scl['rr']), 'res': Outils.format_2_dec(scl['r']),
                    'int_emo': Latex.echappe_caracteres(generaux.articles[0].intitule_long),
                    'int_res': Latex.echappe_caracteres(generaux.articles[1].intitule_long),
                    'p_emo': generaux.poste_emolument, 'p_res': generaux.poste_reservation}

            contenu = r'''
                \hline
                N. Poste & Poste & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
                & \multicolumn{1}{c|}{Total} \\
                \hline'''
            if scl['em'] > 0 and not (filtre == "OUI" and scl['e'] == 0):
                contenu += r'''
                    %(p_emo)s & %(int_emo)s & %(emom)s & %(emor)s & %(emo)s \\
                    \hline''' % dico
            if scl['rm'] > 0 and not (filtre == "OUI" and scl['r'] == 0):
                contenu += r'''
                    %(p_res)s & %(int_res)s & %(resm)s & %(resr)s & %(res)s \\
                    \hline
                    ''' % dico

            contenu += contenu_prix_xf

            contenu += r'''\multicolumn{4}{|r|}{Total}
                & ''' + Outils.format_2_dec(scl['somme_t']) + r'''\\
                \hline
                '''
            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_qte_lvr_jdu(code_client, id_compte, intitule_compte, generaux, livraisons, users):
        """
        Qté LVR J/D/U - Table Compte Détail Quantités livrées/Prestation (code D)/User
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param generaux: paramètres généraux
        :param livraisons: livraisons importées
        :param users: users importés
        :return: table au format latex
        """

        structure = r'''{|l|c|c|c|}'''
        legende = r'''Détails des prestations livrées'''

        contenu = r'''
            '''
        i = 0
        somme = livraisons.sommes[code_client][id_compte]
        for article in generaux.articles_d3:
            if article.code_d in somme:
                if i == 0:
                    i += 1
                else:
                    contenu += r'''\multicolumn{4}{c}{} \\
                        '''
                contenu += r'''
                    \hline
                    \multicolumn{1}{|l|}{
                    \textbf{''' + intitule_compte + " - " + Latex.echappe_caracteres(article.intitule_long) + r'''
                    }} & Quantité & Unité & Rabais \\
                    \hline
                    '''
                for no_prestation, sip in sorted(somme[article.code_d].items()):
                    dico_prestations = {'nom': Latex.echappe_caracteres(sip['nom']),
                                        'num': no_prestation,
                                        'quantite': "%.1f" % sip['quantite'],
                                        'unite': Latex.echappe_caracteres(sip['unite']),
                                        'rabais': Outils.format_2_dec(sip['rabais'])}
                    contenu += r'''
                        %(num)s - %(nom)s & \hspace{5mm} %(quantite)s & %(unite)s
                        & \hspace{5mm} %(rabais)s \\
                        \hline
                        ''' % dico_prestations

                    utilisateurs = Outils.utilisateurs_in_somme(sip['users'], users)

                    for nom, upi in sorted(utilisateurs.items()):
                        for prenom, ids in sorted(upi.items()):
                            for id_user in sorted(ids):
                                spu = sip['users'][id_user]
                                dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                             'quantite': "%.1f" % spu['quantite'],
                                             'unite': Latex.echappe_caracteres(sip['unite']),
                                             'rabais': Outils.format_2_dec(spu['rabais'])}
                                contenu += r'''
                                    \hspace{5mm} %(user)s & %(quantite)s & %(unite)s & %(rabais)s \\
                                    \hline
                                ''' % dico_user

                                for pos in spu['data']:
                                    liv = livraisons.donnees[pos]
                                    rem = ""
                                    dl = ""
                                    if liv['remarque'] != "":
                                        rem = "; Remarque : " + liv['remarque']
                                    if liv['date_livraison'] != "":
                                        dl = "Dt livraison: " + liv['date_livraison'] + ";"
                                    op = users.donnees[liv['id_operateur']]
                                    dico_pos = {'date_liv': Latex.echappe_caracteres(dl),
                                                'quantite': "%.1f" % liv['quantite'],
                                                'rabais': Outils.format_2_dec(liv['rabais_r']),
                                                'id': Latex.echappe_caracteres(liv['id_livraison']),
                                                'unite': Latex.echappe_caracteres(sip['unite']),
                                                'responsable': Latex.echappe_caracteres(op['prenom'] + " " + op['nom']),
                                                'commande': Latex.echappe_caracteres(liv['date_commande']),
                                                'remarque': Latex.echappe_caracteres(rem)}
                                    contenu += r'''
                                        \hspace{10mm} %(date_liv)s N. livraison: %(id)s
                                        & %(quantite)s \hspace{5mm} & %(unite)s & %(rabais)s \hspace{5mm} \\
        
                                        \hspace{10mm} \scalebox{.8}{Commande: %(commande)s;
                                        Resp: %(responsable)s%(remarque)s} & & & \\
                                        \hline
                                    ''' % dico_pos

        return Latex.long_tableau(contenu, structure, legende)

    @staticmethod
    def table_tps_cae_jkmu(code_client, id_compte, intitule_compte, users, machines, categories, acces):
        """
        Tps CAE J/K/M/U - Table Compte Détail Temps CAE/Catégorie Machine/Machine/User
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param users: users importés
        :param machines: machines importées
        :param categories: catégories importées
        :param acces: accès importés
        :return: table au format latex
        """

        if code_client in acces.sommes and id_compte in acces.sommes[code_client]['comptes']:
            structure = r'''{|l|l|l|c|c|c|}'''
            legende = r'''Détails des utilisations machines'''

            contenu = r'''
                \hline
                \multicolumn{3}{|l|}{\multirow{2}{*}{\scriptsize{\textbf{''' + intitule_compte + r'''}}}}
                & \multicolumn{2}{c|}{Machine} & Main d'oeuvre \\
                \cline{4-6}
                \multicolumn{3}{|l|}{} & HP & HC &  \\
                \hline
                '''

            somme = acces.sommes[code_client]['comptes'][id_compte]
            som_cat = acces.sommes[code_client]['categories'][id_compte]['machine']

            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_categorie, mics in sorted(machines_utilisees.items()):
                dico_cat = {'hp': Outils.format_heure(som_cat[id_categorie]['duree_hp']),
                            'hc': Outils.format_heure(som_cat[id_categorie]['duree_hc']),
                            'mo': Outils.format_heure(som_cat[id_categorie]['mo'])}
                contenu += r'''
                    \multicolumn{3}{|l|}
                    {\textbf{''' + Latex.echappe_caracteres(categories.donnees[id_categorie]['intitule']) + r'''}} &
                     \hspace{5mm} %(hp)s & \hspace{5mm} %(hc)s &
                     \hspace{5mm} %(mo)s \\
                    \hline''' % dico_cat

                for nom_machine, id_machine in sorted(mics.items()):

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'hp': Outils.format_heure(somme[id_machine]['duree_hp']),
                                    'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                    'mo': Outils.format_heure(somme[id_machine]['mo'])}
                    contenu += r'''
                        \multicolumn{3}{|l|}{\hspace{2mm} \textbf{%(machine)s}} & \hspace{3mm} %(hp)s & 
                        \hspace{3mm} %(hc)s & \hspace{3mm} %(mo)s \\
                        \hline
                        ''' % dico_machine

                    utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                    for nom, upi in sorted(utilisateurs.items()):
                        for prenom, ids in sorted(upi.items()):
                            for id_user in sorted(ids):
                                smu = somme[id_machine]['users'][id_user]
                                dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                             'hp': Outils.format_heure(smu['duree_hp']),
                                             'hc': Outils.format_heure(smu['duree_hc']),
                                             'mo': Outils.format_heure(smu['mo'])}
                                contenu += r'''
                                    \multicolumn{3}{|l|}{\hspace{5mm} %(user)s} & %(hp)s & %(hc)s & %(mo)s \\
                                    \hline
                                ''' % dico_user
                                for p1 in smu['data']:
                                    cae = acces.donnees[p1]
                                    login = Latex.echappe_caracteres(cae['date_login']).split()
                                    temps = login[0].split('-')
                                    date = temps[0]
                                    for p2 in range(1, len(temps)):
                                        date = temps[p2] + '.' + date
                                    if len(login) > 1:
                                        heure = login[1]
                                    else:
                                        heure = ""

                                    rem = ""
                                    if id_user != cae['id_op']:
                                        op = users.donnees[cae['id_op']]
                                        rem += "op : " + op['nom'] + " " + op['prenom']
                                    if cae['remarque_op'] != "":
                                        if rem != "":
                                            rem += "; "
                                        rem += "rem op : " + cae['remarque_op']
                                    if cae['remarque_staff'] != "":
                                        if rem != "":
                                            rem += "; "
                                        rem += "rem CMi : " + cae['remarque_staff']

                                    dico_pos = {'date': date, 'heure': heure,
                                                'rem': Latex.echappe_caracteres(rem),
                                                'hp': Outils.format_heure(cae['duree_machine_hp']),
                                                'hc': Outils.format_heure(cae['duree_machine_hc']),
                                                'mo': Outils.format_heure(cae['duree_operateur'])}
                                    contenu += r'''
                                        \hspace{10mm} %(date)s & %(heure)s & \parbox{5cm}{%(rem)s}
                                        & %(hp)s \hspace{5mm} & %(hc)s \hspace{5mm} & %(mo)s \hspace{5mm} \\
                                        \hline
                                    ''' % dico_pos

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_lvr_jd(code_client, id_compte, intitule_compte, sco, sommes_livraisons, generaux):
        """
        Prix LVR J/D - Table Compte Récap Prestations livrées/code D
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_livraisons: sommes des livraisons importées
        :param generaux: paramètres généraux
        :return: table au format latex
        """

        if code_client in sommes_livraisons and id_compte in sommes_livraisons[code_client]:
            somme = sommes_livraisons[code_client][id_compte]
            structure = r'''{|l|r|c|r|r|r|}'''
            legende = r'''Consommables et autres prestations'''
            contenu_prests = ""
            for article in generaux.articles_d3:
                if article.code_d in somme:
                    if contenu_prests != "":
                        contenu_prests += r'''
                            \multicolumn{6}{c}{} \\
                            '''

                    contenu_prests += r'''
                        \hline
                        \multicolumn{1}{|l|}{
                        \textbf{''' + intitule_compte + " - " + Latex.echappe_caracteres(article.intitule_long) + r'''
                        }} & \multicolumn{1}{c|}{Quantité} & Unité & \multicolumn{1}{c|}{P.U.}
                        & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais} \\
                        \hline
                        '''
                    for no_prestation, sip in sorted(somme[article.code_d].items()):
                        dico_prestations = {'nom': Latex.echappe_caracteres(sip['nom']),
                                            'num': no_prestation,
                                            'quantite': "%.1f" % sip['quantite'],
                                            'unite': Latex.echappe_caracteres(sip['unite']),
                                            'pn': Outils.format_2_dec(sip['pn']),
                                            'montant': Outils.format_2_dec(sip['montant']),
                                            'rabais': Outils.format_2_dec(sip['rabais'])}
                        contenu_prests += r'''
                            %(num)s - %(nom)s & \hspace{5mm} %(quantite)s & %(unite)s & %(pn)s & %(montant)s
                            & %(rabais)s  \\
                            \hline
                            ''' % dico_prestations
                    dico_prestations = {'montant': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                        'rabais': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d])}
                    contenu_prests += r'''
                        \multicolumn{4}{|r|}{Total} & %(montant)s & %(rabais)s  \\
                        \hline
                        ''' % dico_prestations
            return Latex.tableau(contenu_prests, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_cae_jk(code_client, id_compte, intitule_compte, sco, sommes_acces, categories):
        """
        Prix CAE J/K - Table Compte Récap Procédés/Catégorie Machine
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_acces: sommes des accès importés
        :param categories: catégories importées
        :return: table au format latex
        """

        if code_client in sommes_acces and id_compte in sommes_acces[code_client]['comptes']:

            structure = r'''{|l|c|c|r|r|}'''
            legende = r'''Services'''
            contenu = r'''
                \hline
                \textbf{''' + intitule_compte + r'''} & Unité & Quantité & \multicolumn{1}{c|}{PU} &
                 \multicolumn{1}{c|}{Montant}   \\
                \hline
                '''

            for cat, som_cat in sorted(sommes_acces[code_client]['categories'][id_compte].items()):

                for id_categorie, cats in sorted(som_cat.items()):
                    montant = cats['mk']
                    unite = categories.donnees[id_categorie]['unite']
                    if unite == 'hh_mm':
                        quantite = Outils.format_heure(cats['quantite'])
                    else:
                        quantite = cats['quantite']
                    if montant > 0:
                        dico_cat = {'intitule': Latex.echappe_caracteres(categories.donnees[id_categorie]['intitule']),
                                    'pk': Outils.format_2_dec(cats['pk']),
                                    'unite': Latex.echappe_caracteres(unite),
                                    'quantite': quantite,
                                    'mk': Outils.format_2_dec(montant)}
                        contenu += r'''
                            %(intitule)s & %(unite)s & %(quantite)s & %(pk)s & %(mk)s  \\
                            \hline
                            ''' % dico_cat

            dico_cat = {'mkj': Outils.format_2_dec(sco['somme_j_mk'])}

            contenu += r'''
                \multicolumn{4}{|r|}{Total} & %(mkj)s \\
                \hline
                ''' % dico_cat

            return Latex.tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_ja(sco, generaux):
        """
        Prix JA - Table Compte Récap Articles
        :param sco: sommes compte calculées
        :param generaux: paramètres généraux
        :return: table au format latex
        """

        structure = r'''{|l|r|r|r|}'''
        legende = r'''Récapitulatif des articles du projet'''

        contenu = r'''
            \cline{2-4}
            \multicolumn{1}{r|}{} & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
            & \multicolumn{1}{c|}{Net} \\
            \hline'''

        if sco['somme_j_mm'] > 0:
            dico = {'mm': Outils.format_2_dec(sco['somme_j_mm']), 'mr': Outils.format_2_dec(sco['somme_j_mr']),
                    'mj': Outils.format_2_dec(sco['mj']),
                    'int_proc': Latex.echappe_caracteres(generaux.articles[2].intitule_long)}
            contenu += r'''
                %(int_proc)s & %(mm)s & %(mr)s & %(mj)s \\
                \hline
                ''' % dico

        total = sco['mj']
        for article in generaux.articles_d3:
            total += sco['tot_cat'][article.code_d]
            if sco['sommes_cat_m'][article.code_d]:
                dico = {'intitule': Latex.echappe_caracteres(article.intitule_long),
                        'cmj': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                        'crj': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                        'cj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
                contenu += r'''
                %(intitule)s & %(cmj)s & %(crj)s & %(cj)s \\
                \hline
                ''' % dico

        contenu += r'''\multicolumn{3}{|r|}{Total} & ''' + Outils.format_2_dec(total) + r'''\\
        \hline
        '''

        return Latex.tableau(contenu, structure, legende)

    @staticmethod
    def table_prix_jdmu(code_client, id_compte, intitule_compte, sco, sommes_acces, machines, users):
        """
        Prix JD/M/U - Table Compte Déductions HC (Rabais) par Machine
        :param code_client: code du client concerné
        :param id_compte: id du compte concerné
        :param intitule_compte: intitulé du compte concerné
        :param sco: sommes compte calculées
        :param sommes_acces: sommes des accès importés
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """

        if sco['somme_j_dhi'] > 0 and code_client in sommes_acces and id_compte in sommes_acces[code_client]['comptes']:
            structure = r'''{|l|c|r|r|}'''
            legende = r'''Rabais d’utilisation de machines en heures creuses'''
            contenu = r'''
                \hline
                \multicolumn{2}{|l|}{\textbf{''' + intitule_compte + r'''}} & \multicolumn{1}{c|}{Temps Mach.}
                 & \multicolumn{1}{c|}{Rabais (CHF)} \\
                \hline
                '''

            somme = sommes_acces[code_client]['comptes'][id_compte]
            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_categorie, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    if somme[id_machine]['dhi'] > 0:
                        dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                        'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                        'dhi': Outils.format_2_dec(somme[id_machine]['dhi'])}
                        contenu += r'''
                            \hspace{2mm} %(machine)s & HC & %(hc)s & %(dhi)s \\
                            \hline
                            ''' % dico_machine

                        utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    smu = somme[id_machine]['users'][id_user]
                                    if smu['duree_hc'] > 0:
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'hc': Outils.format_heure(smu['duree_hc'])}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & HC & %(hc)s \hspace{5mm} & \\
                                            \hline
                                        ''' % dico_user

            dico = {'rabais_d': Outils.format_2_dec(sco['somme_j_dhi_d']),
                    'rabais': Outils.format_2_dec(sco['somme_j_dhi'])}

            contenu += r'''
                \multicolumn{3}{|r|}{Arrondi} & %(rabais_d)s \\
                \hline
                \multicolumn{3}{|r|}{Total} & %(rabais)s \\
                \hline
                ''' % dico

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_points_xbmu(code_client, scl, sommes_acces, machines, users):
        """
        Points XB/M/U - Table Client Récap Bonus/MAchine/User
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_acces: sommes des accès importés
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """
        if scl['somme_t_mb'] > 0:
            structure = r'''{|l|c|r|r|}'''
            legende = r'''Récapitulatif des bonus d’utilisation en heures creuses'''

            contenu = r'''
                \cline{3-4}
                \multicolumn{2}{l|}{} & \multicolumn{1}{c|}{Temps Mach.} & \multicolumn{1}{c|}{Points Bonus} \\
                \hline
                '''

            somme = sommes_acces[code_client]['machines']
            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_categorie, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    if somme[id_machine]['dhm'] > 0:
                        dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                        'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                        'dhm': somme[id_machine]['dhm']}
                        contenu += r'''
                            \hspace{2mm} %(machine)s & HC & %(hc)s & %(dhm)s \\
                            \hline
                            ''' % dico_machine

                        utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    smu = somme[id_machine]['users'][id_user]
                                    if smu['duree_hc'] > 0:
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'hc': Outils.format_heure(smu['duree_hc'])}
                                        contenu += r'''
                                            \hspace{5mm} %(user)s & HC & %(hc)s \hspace{5mm} & \\
                                            \hline
                                        ''' % dico_user

            dico = {'bht': scl['somme_t_mb']}
            contenu += r'''
                \multicolumn{3}{|r|}{\textbf{Total points de bonus}} & %(bht)s \\
                \hline
                ''' % dico

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""

    @staticmethod
    def table_prix_xrmu(code_client, scl, sommes_reservations, machines, users):
        """
        Prix XR/M/U - Table Client Récap Pénalités Réservations/Machine/user
        :param code_client: code du client concerné
        :param scl: sommes client calculées
        :param sommes_reservations: sommes des réservations importées
        :param machines: machines importées
        :param users: users importés
        :return: table au format latex
        """
        if scl['rm'] > 0:
            structure = r'''{|l|c|c|r|r|}'''
            legende = r'''Récapitulatif des pénalités de réservation'''

            contenu = r'''
                \cline{3-5}
                \multicolumn{2}{l|}{} & \multicolumn{1}{c|}{Pénalités} & \multicolumn{1}{c|}{PU} 
                & \multicolumn{1}{c|}{Montant} \\
                \cline{3-5}
                \multicolumn{2}{l|}{} & \multicolumn{1}{c|}{Durée} & \multicolumn{1}{c|}{CHF/h} 
                & \multicolumn{1}{c|}{CHF} \\
                \hline
                '''

            somme = sommes_reservations[code_client]

            machines_reservees = Outils.machines_in_somme(somme, machines)

            for id_categorie, mics in sorted(machines_reservees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    scm = scl['res'][id_machine]
                    contenu_hp = ""
                    contenu_hc = ""
                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'duree_hp': Outils.format_heure(scm['tot_hp']),
                                    'pu_hp': Outils.format_2_dec(somme[id_machine]['pu_hp']),
                                    'montant_hp': Outils.format_2_dec(scm['mont_hp']),
                                    'duree_hc': Outils.format_heure(scm['tot_hc']),
                                    'pu_hc': Outils.format_2_dec(somme[id_machine]['pu_hc']),
                                    'montant_hc': Outils.format_2_dec(scm['mont_hc'])}
                    if scm['mont_hp'] > 0:
                        contenu_hp += r'''
                                %(machine)s & HP & %(duree_hp)s & %(pu_hp)s  & %(montant_hp)s \\
                                \hline
                                ''' % dico_machine

                    if scm['mont_hc'] > 0:
                        contenu_hc += r'''
                                %(machine)s & HC & %(duree_hc)s & %(pu_hc)s  & %(montant_hc)s \\
                                \hline
                                ''' % dico_machine

                    utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                    for nom, upi in sorted(utilisateurs.items()):
                        for prenom, ids in sorted(upi.items()):
                            for id_user in sorted(ids):
                                smu = scm['users'][id_user]
                                dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                             'duree_hp': Outils.format_heure(smu['tot_hp']),
                                             'duree_hc': Outils.format_heure(smu['tot_hc'])}
                                if scm['mont_hp'] > 0 and smu['tot_hp'] > 0:
                                    contenu_hp += r'''
                                            \hspace{5mm} %(user)s & HP & %(duree_hp)s \hspace{5mm} & & \\
                                            \hline
                                            ''' % dico_user

                                if scm['mont_hc'] > 0 and smu['tot_hc'] > 0:
                                    contenu_hc += r'''
                                            \hspace{5mm} %(user)s & HC & %(duree_hc)s \hspace{5mm} & & \\
                                            \hline
                                            ''' % dico_user
                    contenu += contenu_hp
                    contenu += contenu_hc

            dico = {'penalite_d': Outils.format_2_dec(scl['rm_d']),
                    'penalite': Outils.format_2_dec(scl['rm']),
                    'rabais': Outils.format_2_dec(scl['rr']),
                    'total': Outils.format_2_dec(scl['r'])}

            contenu += r'''
                \multicolumn{4}{|r|}{Arrondi} & %(penalite_d)s \\
                \hline
                \multicolumn{4}{|r|}{Total} & %(penalite)s \\
                \hline
                \multicolumn{4}{|r|}{Rabais} & %(rabais)s \\
                \hline
                \multicolumn{4}{|r|}{\textbf{Total à payer}} & %(total)s \\
                \hline
                ''' % dico

            return Latex.long_tableau(contenu, structure, legende)
        else:
            return ""
