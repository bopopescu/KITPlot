import sys,os
import sqlalchemy
import mysql.connector
try:
    from .db_map import *
except:
    from db_map import *
from sqlalchemy.orm import sessionmaker


class KITSearch(object):

    def __init__(self,cred):
        """ cred = {"host"      : "...",
                    "database"  : "...",
                    "user"      : "...",
                    "passwd"    : "..."}
        """
        self.engine = sqlalchemy.create_engine("mysql+mysqlconnector://" +
                                          cred["user"] + ":" + cred["passwd"] +
                                          "@" + cred["host"] + ":" +
                                          "3306" + "/" + cred["database"])

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    #####################
    # basic table search#
    #####################
    def search_in_info(self,val,para=None):
        if para == "name" or para == None:
            data = self.session.query(db_info).filter_by(name=val)
        elif para == "UID":
            data = self.session.query(db_info).filter_by(ID=val)
        return data

    def search_in_probe(self,val,para=None):
        if para == "PID" or para == None:
            data = self.session.query(db_probe).filter_by(probeid=val)
        elif para == "UID":
            data = self.session.query(db_probe).filter_by(ID=val)
        return data

    def search_in_probe_data(self,val,para=None):
        if para == "PID" or para == None:
            data = self.session.query(db_probe_data).filter_by(probeid=val)
        return data

    def search_in_alibava(self,val,para=None):
        if para == "run" or para == None:
            data = self.session.query(db_alibava).filter_by(run=val)
        elif para == "UID":
            data = self.session.query(db_alibava).filter_by(alibava_uid=val)
        elif para == "ID":
            data = self.session.query(db_alibava).filter_by(ID=val)
        return data

    def search_in_annealing(self,val,para=None):
        if para == "ID" or para == None:
            data = self.session.query(db_annealing).filter_by(ID=val)
        return data

    def search_in_irradiation(self,val,para=None):
        if para == "ID" or para == None:
            data = self.session.query(db_irradiation).filter_by(ID=val)
        return data

    ####################
    # combined searches#
    ####################
    def probe_search_for_name(self,name,project):
        dic = {}
        PID = []
        for col in self.search_in_info(name,para="name"):
            if col.project == project:
                UID = col.ID
        for row in self.search_in_probe(UID,"UID"):
            PID.append(row.probeid)
        for run in PID:
            sub = self.probe_search_for_PID(run)
            temp = sub.pop("PID")
            sub.update({"PID" : temp})
            dic.update({temp : sub})
        return dic

    def probe_search_for_PID(self,PID):
        dic = {}
        dataX = []
        dataY = []
        dataZ = []
        temp = []
        rh = []
        err = []
        time = []
        bias_cur = []

        for row in self.search_in_probe_data(PID):
            dataX.append(row.datax)
            dataY.append(row.datay)
            dataZ.append(row.dataz)
            temp.append(row.temperature)
            rh.append(row.RH)
            err.append(row.errory)
            time.append(row.time)
            bias_cur.append(row.bias_current)

        dic.update({"dataX"     : dataX,
                    "dataY"     : dataY,
                    "dataZ"     : dataZ,
                    "temp"      : temp,
                    "rh"        : rh,
                    "err"       : err,
                    "time"      : time,
                    "bias_cur"  : bias_cur})

        for col in self.search_in_probe(PID):
            dic.update({"paraX"     : col.paraX,
                        "paraY"     : col.paraY,
                        "t0"        : col.temperature,
                        "h0"        : col.RH,
                        "PID"       : col.probeid,
                        "UID"       : col.ID,
                        "date"      : col.date})

        for col in self.search_in_info(dic["UID"],para="UID"):
            dic.update({"name"      : col.name,
                        "project"   : col.project})

        fluence, pt = self.getFluence(dic["UID"],dic["date"])
        dic.update({"fluence"       : fluence,
                    "particletype"  : pt})
        return dic

    def ali_search_for_run(self,nr):
        dic = {}
        for col in self.search_in_alibava(nr):
            dic.update({"voltage"       : col.voltage,
                        "e_sig"         : col.electron_sig,
                        "e_sig_err"     : col.signal_e_err,
                        "gain"          : col.gain,
                        "seed"          : col.SeedSigENC_MPV,
                        "seed_err"      : col.SeedSigENC_MPV_err,
                        "seedADC"       : col.SeedSig_MPV,
                        "seedADC_err"   : col.SeedSig_MPV_err})
            ID = col.ID
            date = col.date

        dic.update({"annealing" : self.getAnnealing(ID,date)})

        for col in self.search_in_info(ID,para="UID"):
            dic.update({"name"      : col.name,
                        "Fp"        : col.F_p_aim_n_cm2,
                        "Fn"        : col.F_n_aim_n_cm2,
                        "project"   : col.project})

        return dic

    def ali_search_for_name_voltage(self,name,voltage,project):
        dic = {}
        for col in self.search_in_info(name,"name"):
            if col.project == project:
                ID = col.ID
        for col in self.search_in_alibava(ID,"ID"):
            sub = {}
            if (voltage*0.99)<abs(col.voltage)<(voltage*1.01):
                sub.update({"voltage"       : col.voltage,
                            "date"          : col.date,
                            "e_sig"         : col.electron_sig,
                            "e_sig_err"     : col.signal_e_err,
                            "gain"          : col.gain,
                            "seed"          : col.SeedSigENC_MPV,
                            "seed_err"      : col.SeedSigENC_MPV_err,
                            "annealing"     : self.getAnnealing(ID,col.date),
                            "name"          : name,
                            "project"       : project,
                            "fluence"       : None})
                dic.update({col.run : sub})
        return dic

    def ali_search_for_name_annealing(self,name,annealing,project):
        dic = {}
        for col in self.search_in_info(name,"name"):
            if col.project == project:
                ID = col.ID
        for col in self.search_in_alibava(ID,"ID"):
            sub = {}
            if (annealing*0.99)<abs(self.getAnnealing(ID,col.date))<(annealing*1.01):
                sub.update({"voltage"       : col.voltage,
                            "date"          : col.date,
                            "e_sig"         : col.electron_sig,
                            "e_sig_err"     : col.signal_e_err,
                            "gain"          : col.gain,
                            "seed"          : col.SeedSigENC_MPV,
                            "seed_err"      : col.SeedSigENC_MPV_err,
                            "annealing"     : self.getAnnealing(ID,col.date)})
                dic.update({col.run : sub})
        return dic

    def getAnnealing(self,ID,date):
        annealing = 0
        for col in self.search_in_annealing(ID):
            if date>col.date:
                annealing += col.equiv
        return round(annealing)

    def getFluence(self,ID,date):
        fluence = 0
        pt = []
        for col in self.search_in_irradiation(ID):
            if date.date()>col.date:
                fluence += col.F_n_cm2
                pt.append(col.particletype)
        if set(pt) == set(["n","p"]):
            pt = "(n,p)"
        elif len(pt) == 1:
            pt = pt[0]
        else:
            pt = ""
        return ("{:0.0e}".format(fluence), pt)

    def getSession(self):
        return self.session

if __name__ == '__main__':

    db = {"host": "192.168.13.2",
          "database": "sample",
          "user": "abfrage",
          "passwd": "JtjTN9M4WpQr,29t"}
    s = KITSearch(db)
    print(s.probe_search_for_name("Irradiation_04"))
    # print(s.ali_search_for_name_voltage("KIT_Test_07",600))
