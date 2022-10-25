import sqlite3
import threading

class Database:
    cursor = None
    conn = None
    lock = None
    
    def __init__(self):
        import os.path

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "db.db")
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

    def execute(self, sql, arg1=()):
        self.lock.acquire()
        self.cursor.execute(sql, arg1)
        self.lock.release()
    
    def return_arr_dict(self):
        self.lock.acquire()
        try:
            ncols = len(self.cursor.description)
            colnames = [self.cursor.description[i][0] for i in range(ncols)]
            results = []
            for row in self.cursor.fetchall():
                res = {}
                for i in range(ncols):
                    res[colnames[i]] = row[i]
                results.append(res)
        except:
            results = []
        finally:
            self.lock.release()
        return results

    ##############################
    ##      DASHBOARD           ##
    ##############################

    def select_last_cve(self):
        self.execute(" SELECT *,strftime('%d-%m-%Y', publication_date) AS date_fr,julianday('now') - julianday(publication_date)AS jour FROM CVES ORDER BY publication_date DESC LIMIT 10")
        result = self.return_arr_dict()
        return result

    def select_nb_cve(self):
        self.execute("SELECT * FROM CVES")
        result = self.return_arr_dict()
        return result

    def nb_last_CVE(self):
        self.execute("SELECT COUNT(id_cve) as nb_cve FROM CVES WHERE publication_date >= date('now', '-7 day');")
        result = self.return_arr_dict()
        return result





    #########################
    ##      Join           ##
    #########################

    def select_all_host_information_os(self,id_infra):
        self.execute("SELECT id_host, ip,hostname, os_name, os_version FROM Hosts NATURAL JOIN OS WHERE id_infrastructure=?",(id_infra))
        result = self.return_arr_dict()
        return result

    def select_host_information_with_app(self,id_host):
        self.execute("SELECT id_host, ip,hostname, os_name, os_version, application_name, application_version FROM Applications NATURAL JOIN applications_installed NATURAL JOIN Hosts NATURAL JOIN OS WHERE id_host=?;",(id_host,))
        result = self.return_arr_dict()
        return result
    
    def select_cve_from_host(self,id_host):
        self.execute("select * from applications_vulnerable NATURAL JOIN Applications NATURAL JOIN applications_installed NATURAL JOIN Hosts ;",(id_host))
        result = self.return_arr_dict()
        return result


    ######################################
    ## Host Tables                      ##
    ######################################
        
    def select_all_hosts(self,id_infra):
        self.execute("SELECT * from Hosts where id_infrastructure=?",(id_infra))
        result = self.return_arr_dict()
        return result

    def insert_host(self,id_host,ip,hostname,refos,id_infrastructure):
        self.execute("INSERT INTO Hosts(id_host,ip,hostname,id_os,id_infrastructure) VALUES (?,?,?,?,?)",(id_host,ip,hostname,refos,id_infrastructure))
        self.conn.commit()
        return

    def select_host(self,idhost):
        self.execute("SELECT * FROM Hosts WHERE id_host=?",(idhost,))
        result = self.return_arr_dict()
        return result

    ######################################
    ## Infrastructures Tables           ##
    ######################################

    def select_id_infrastructure_from_login(self,login):
        self.execute("SELECT id_infrastructure,password FROM Infrastructure WHERE login=?",(login,))
        result = self.return_arr_dict()
        return result

    def select_all_users(self):
        self.execute("SELECT id_infrastructure,login,infrastructure_name FROM Infrastructure;")
        result = self.return_arr_dict()
        return result

    def insert_user(self,nom_ref,prenom_ref,mail_ref,tel_ref,login,pwd,infra_name):
        self.execute("INSERT INTO Infrastructure (nom_referent,prenom_referent,mail_referent,tel_referent,login,password,infrastructure_name) \
            VALUES (?,?,?,?,?,?,?)", (nom_ref,prenom_ref,mail_ref,tel_ref,login,pwd,infra_name))
        self.conn.commit()
        return

    def update_user(self,nom,prenom,telephone,mail,id_infra):
        self.execute("UPDATE Infrastructure SET nom_referent=?, prenom_referent=?, mail_referent=?, tel_referent=? WHERE id_infrastructure =?", (nom,prenom,mail,telephone, id_infra))
        self.conn.commit()
        return

    def select_user(self,id_infra):
        self.execute("SELECT * FROM Infrastructure WHERE id_infrastructure=?;",(id_infra,))
        result = self.return_arr_dict()
        return result

    ######################################
    ## OS  Tables                       ##
    ######################################

    def select_all_os(self):
        self.execute("SELECT * from OS")
        result = self.return_arr_dict()
        return result

    def select_id_os_from_OS(self,os_name,os_version):
        self.execute("SELECT id_os FROM OS WHERE os_name=? and os_version=?",(os_name, os_version))
        result = self.return_arr_dict()
        return result

    def select_os_information_from_id_os(self,id_os):
        self.execute("SELECT os_name, os_version FROM OS WHERE id_os=? ",(id_os))
        result = self.return_arr_dict()
        return result

    def insert_os(self,os_name,os_version):
        self.execute("INSERT INTO OS(os_name,os_version) VALUES (?,?)",(os_name,os_version))
        self.conn.commit()
        return


    ######################################
    ## CVE Tables                       ##
    ###################################### 

    def select_all_cve(self,id_infra):
        self.execute("""SELECT DISTINCT * 
                    FROM CVES NATURAL JOIN applications_vulnerable NATURAL JOIN Applications 
                    NATURAL JOIN applications_installed NATURAL JOIN Hosts Where id_infrastructure=? AND state='ON'""",(id_infra,))
        result = self.return_arr_dict()
        return result    

    def app_impacte(self,id_infra):
        self.execute("""SELECT  application_name
            FROM applications_vulnerable NATURAL JOIN CVES NATURAL JOIN Applications 
            NATURAL JOIN applications_installed NATURAL JOIN Hosts Where id_infrastructure=? AND state='ON' GROUP BY application_name
            ORDER BY COUNT(application_name) DESC
            LIMIT 1""",(id_infra))
        result = self.return_arr_dict()
        return result        
    def host_impacte(self,id_infra):
        self.execute("""SELECT  hostname
            FROM applications_vulnerable NATURAL JOIN CVES NATURAL JOIN Applications 
            NATURAL JOIN applications_installed NATURAL JOIN Hosts Where id_infrastructure=? AND state='ON' GROUP BY application_name
            ORDER BY COUNT(application_name) DESC
            LIMIT 1""",(id_infra))
        result = self.return_arr_dict()
        return result    
        
    def highest_cve(self,id_infra):
        self.execute("""SELECT *
FROM applications_vulnerable NATURAL JOIN CVES NATURAL JOIN Applications 
            NATURAL JOIN applications_installed NATURAL JOIN Hosts Where id_infrastructure=? AND state='ON' ORDER BY criticality desc LIMIT 1""",(id_infra))
        result = self.return_arr_dict()
        return result

    def details_cve(self,title_cve):
        self.execute("""SELECT *, count(version) as nb_ver FROM CVES NATURAL LEFT JOIN CVES_VER WHERE title =?""",(title_cve,))
        result = self.return_arr_dict()
        return result

    def put_off_CVE(self,idvuln):
        self.execute("UPDATE applications_vulnerable SET state='OFF' WHERE id_vuln =?",(idvuln,))
        self.conn.commit()
        return
    

    def insert_cve(self,title,criticality,apps_ref):
        self.execute("INSERT INTO CVES(title,criticality,id_application) VALUES (?,?,?)",(title,criticality,apps_ref))
        self.conn.commit()
        return

    ######################################
    ## Application Tables               ##
    ######################################

    def insert_app(self,nomApp,versionApp):
        self.execute("INSERT INTO Applications(application_name,application_version) VALUES (?,?)",(nomApp,versionApp))
        self.conn.commit()
        return

    def select_id_app(self,nomApp,versionApp):
        self.execute("SELECT id_application FROM Applications WHERE application_name=? and application_version=?",(nomApp,versionApp))
        result = self.return_arr_dict()
        return result

    def select_all_apps_from_infra(self,id_infra):
        self.execute("SELECT id_application FROM Applications NATURAL JOIN applications_installed NATURAL JOIN Hosts WHERE id_infrastructure=? ",(id_infra,))
        result = self.return_arr_dict()
        return result
    
    ######################################
    ## Associate Tables                 ##
    ######################################

    def insert_associate_host_apps(self,idapp,idhost):
        self.execute("INSERT INTO applications_installed(id_host,id_application) VALUES (?,?)",(idhost,idapp))
        self.conn.commit()
        return

    def insert_associate_cve_apps(self,id_cve,idapp):
        self.execute("INSERT INTO applications_vulnerable(id_cve,id_application) VALUES (?,?)",(id_cve,idapp))
        self.conn.commit()
        return

    def insert_associate_cve_os(self,id_cve,id_os):
        self.execute("INSERT INTO os_vulnerable(id_cve,id_os) VALUES (?,?)",(id_cve,id_os))
        self.conn.commit()
        return

    def delete_all_associate_apps_host(self,idhost):
        self.execute("DELETE FROM applications_installed WHERE id_host=?", (idhost,))
        self.conn.commit()
        return

    ######################################
    ## Base de donnée                   ##
    ######################################

    def update_cve_sequence(self):
        self.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='CVES';")
        self.conn.commit()
        return


    def select_id_cve(self,id_cve):
        self.execute("SELECT id_cve FROM CVES WHERE title=?",(id_cve,))
        result = self.return_arr_dict()
        return result

    def insert_cve_version(self,id,product,version):
        self.execute("INSERT OR IGNORE INTO CVES_VER(id_cve, version, application) VALUES (?,?,?)",(str(id),version,product))
        self.conn.commit()
        return

    def insert_cve(self,id,date,cvss,summary):
        self.execute("INSERT OR IGNORE INTO CVES(title,publication_date,criticality, description) VALUES (?, ?, ?, ?)",(id,date,cvss,summary))
        self.conn.commit()
        return 

    def insert_last_cve(self,id,date,summary):
        self.execute("INSERT OR IGNORE INTO CVES(title,publication_date, description) VALUES (?, ?, ?)",(id,date,summary))
        self.conn.commit()
        return

    def get_list_application(self):
        self.execute("SELECT * FROM Applications NATURAL JOIN applications_installed")
        result = self.return_arr_dict()
        return result

    def ajout_app_vuln(self,id_host,id_cve,id_app):
        self.execute("INSERT OR IGNORE INTO applications_vulnerable (id_host,id_cve,id_application) VALUES (?,?,?)",(id_host,id_cve,id_app))
        self.conn.commit()
        return
    
    def get_host_id(self,id_app):
        self.execute("SELECT * FROM applications_installed where id_application = ?",(id_app,))
        result = self.return_arr_dict()
        return result

    def correlationdb(self,app,ver):
        # print(app,ver)
        ver = '%'+ver+'%'
        self.execute("SELECT * FROM CVES NATURAL JOIN CVES_VER WHERE application =? and version LIKE ?",[app,ver,])
        result = self.return_arr_dict()
        return result
