import sqlite3
import sys

def get_application():
    try:
            conn = sqlite3.connect('..\ProjetCyber2\db\db.db')
            cur = conn.cursor()
            REQUETE_AJOUT = """Select IDApplication
                            From Applications
                            Where NomApplication = \'"""+application+"""\';"""


            cur.execute(REQUETE_AJOUT)
            rows = cur.fetchall()
            for row in rows:
                print(row)

    except sqlite3.Error as error:
        print("Erreur : ", error)
    except UnboundLocalError as error:
        print("Erreur application inconnue : ", error)
        sys.exit()