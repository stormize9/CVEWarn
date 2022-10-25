CREATE TABLE "Hosts" (
	"id_host"	TEXT NOT NULL UNIQUE,
	"ip"	TEXT,
	"hostname"	TEXT,
	"id_os"	INTEGER,
	"id_infrastructure" INTEGER,
	FOREIGN KEY("id_os") REFERENCES OS(id_os),
	FOREIGN KEY("id_infrastructure") REFERENCES Infrastructure(id_infrastructure),
	PRIMARY KEY("id_host")
);

CREATE TABLE "Applications" (
	"id_application"	INTEGER NOT NULL UNIQUE,
	"application_name"	TEXT,
	"application_version"	TEXT,
	PRIMARY KEY("id_application" AUTOINCREMENT)
);

CREATE TABLE "OS" (
	"id_os"	INTEGER NOT NULL UNIQUE,
	"os_name"	TEXT NOT NULL ,
	"os_version"	TEXT,
	PRIMARY KEY("id_os" AUTOINCREMENT)
);

CREATE TABLE "CVES" (
	"id_cve"	INTEGER NOT NULL UNIQUE,
	"title"	TEXT UNIQUE,
	"publication_date"	DATE,
	"criticality"	INTEGER,
    "description"	INTEGER,
	PRIMARY KEY("id_cve" AUTOINCREMENT)
);

CREATE TABLE "CVES_VER" (
	"id_cve"	INTEGER NOT NULL,
	"version"	TEXT,
	"application" TEXT,
	FOREIGN KEY("id_cve") REFERENCES CVES(id_cve) ON DELETE CASCADE,
	UNIQUE("id_cve","version","application")
);

CREATE TABLE "States" (
	"id_state"	INTEGER NOT NULL UNIQUE,
	"state_name" TEXT,
	PRIMARY KEY("id_state" AUTOINCREMENT)
);

CREATE TABLE "Infrastructure" (
	"id_infrastructure"	INTEGER NOT NULL UNIQUE,
	"nom_referent"	TEXT,
	"prenom_referent"	TEXT,
	"mail_referent"	TEXT,
	"tel_referent"	TEXT,
	"login"	TEXT,
	"password"	TEXT,
	"infrastructure_name" TEXT,
	PRIMARY KEY("id_infrastructure" AUTOINCREMENT)
);

CREATE TABLE "applications_installed" (
	"id_host" TEXT,
    "id_application" INTEGER,
    FOREIGN KEY("id_host") REFERENCES Hosts(id_host),
    FOREIGN KEY("id_application") REFERENCES Applications(id_application)
);

CREATE TABLE "applications_vulnerable" (
	"id_vuln" INTEGER,
	"id_host" TEXT,
	"id_cve" INTEGER,
    "id_application" INTEGER,
	state TEXT DEFAULT 'ON',
	FOREIGN KEY("id_host") REFERENCES Hosts(id_host),
    FOREIGN KEY("id_cve") REFERENCES CVES(id_cve) ON DELETE CASCADE,
    FOREIGN KEY("id_application") REFERENCES Applications(id_application),
	UNIQUE("id_host","id_cve","id_application"),
	PRIMARY KEY("id_vuln" AUTOINCREMENT)
);

CREATE TABLE "os_vulnerable" (
	id_cve INTEGER,
    id_os INTEGER,
    FOREIGN KEY("id_cve") REFERENCES CVES(id_cve),
    FOREIGN KEY("id_os") REFERENCES OS(id_os)
);

INSERT INTO States (state_name)
VALUES 
("A vérifier"),
("Non impactant"),
("A corrigé"),
("Corrigé");

INSERT INTO Infrastructure (nom_referent,prenom_referent,mail_referent,tel_referent,login,password,infrastructure_name)
VALUES
("Letourneur","Raphaël","letourneur.e2004663@etud.univ-ubs.fr","0606060606","raphael", "password","Letourneur Company")

