import datetime
import numpy as np


def createClusters(startidx, endidx):
    # pojedyncze
    MOS = np.array([1 if (i + 3) % 7 == 0 else 0 for i in range(1, 366)])
    TUS = np.array([1 if (i + 2) % 7 == 0 else 0 for i in range(1, 366)])
    WES = np.array([1 if (i + 1) % 7 == 0 else 0 for i in range(1, 366)])
    THS = np.array([1 if (i) % 7 == 0 else 0 for i in range(1, 366)])
    FRS = np.array([1 if (i + 6) % 7 == 0 else 0 for i in range(1, 366)])
    SAS = np.array([1 if (i + 5) % 7 == 0 else 0 for i in range(1, 366)])
    SUS = np.array([1 if (i + 4) % 7 == 0 else 0 for i in range(1, 366)])
    ALLS = MOS + TUS + WES + THS + FRS + SAS + SUS

    # podwojne
    MOTU = MOS + TUS
    TUWE = TUS + WES
    WETH = WES + THS
    THFR = THS + FRS
    FRSA = FRS + SAS
    SASU = SAS + SUS
    SUMO = SUS + MOS

    # potrojne
    MOTUWE = MOS + TUS + WES
    TUWETH = TUS + WES + THS
    WETHFR = WES + THS + FRS
    THFRSA = THS + FRS + SAS
    FRSASU = FRS + SAS + SUS
    SASUMO = SAS + SUS + MOS
    SUMOTU = SUS + MOS + TUS

    # poczworne
    MOTUWETH = MOS + TUS + WES + THS
    TUWETHFR = TUS + WES + THS + FRS
    WETHFRSA = WES + THS + FRS + SAS
    THFRSASU = THS + FRS + SAS + SUS
    FRSASUMO = FRS + SAS + SUS + MOS
    SASUMOTU = SAS + SUS + MOS + TUS
    SUMOTUWE = SUS + MOS + TUS + WES

    # pięcioelementowe
    MOTUWETHFR = MOS + TUS + WES + THS + FRS
    TUWETHFRSA = TUS + WES + THS + FRS + SAS
    WETHFRSASU = WES + THS + FRS + SAS + SUS
    THFRSASUMO = THS + FRS + SAS + SUS + MOS
    FRSASUMOTU = FRS + SAS + SUS + MOS + TUS
    SASUMOTUWE = SAS + SUS + MOS + TUS + WES
    SUMOTUWETH = SUS + MOS + TUS + WES + THS

    # sześcioelementowe
    MOTUWETHFRSA = ALLS - SUS
    TUWETHFRSASU = ALLS - MOS
    WETHFRSASUMO = ALLS - TUS
    THFRSASUMOTU = ALLS - WES
    FRSASUMOTUWE = ALLS - THS
    SASUMOTUWETH = ALLS - FRS
    SUMOTUWETHFR = ALLS - SAS

    # specjalne
    holidates = "01/01, 06/01, 05/04, 01/05, 03/05, 23/05, 03/06, 15/08, 01/11, 11/11, 25/12, 26/12".split(", ")

    def _date_to_index(dates, year):
        for i in range(len(dates)):
            dates[i] += "/" + year
            dates[i] = datetime.datetime.strptime(dates[i], "%d/%m/%Y").timetuple().tm_yday
        return dates

    _date_to_index(holidates, "2021")
    HOLIDAYS = np.array([1 if i in holidates else 0 for i in range(1, 366)])
    HOLIDAYS += SUS
    HOLIDAYS[HOLIDAYS[:] == 2] = 1

    # robocze
    WORKINGDAYS = MOTUWETHFR - HOLIDAYS
    WORKINGDAYS[WORKINGDAYS[:] == -1] = 0

    # przedświąteczne

    PREHOLIDAYS = np.ones_like(HOLIDAYS)
    for i in range(PREHOLIDAYS.shape[0] - 1):
        PREHOLIDAYS[i] = HOLIDAYS[i + 1]

    PREHOLIDAYS -= HOLIDAYS
    PREHOLIDAYS[PREHOLIDAYS[:] < 0] = 0

    CLUSTERS = np.array([
        MOS, TUS, WES, THS, FRS, SAS, SUS,
        MOTU, TUWE, WETH, THFR, FRSA, SASU, SUMO,
        MOTUWE, TUWETH, WETHFR, THFRSA, FRSASU, SASUMO, SUMOTU,
        MOTUWETH, TUWETHFR, WETHFRSA, THFRSASU, FRSASUMO, SASUMOTU, SUMOTUWE,
        MOTUWETHFR, TUWETHFRSA, WETHFRSASU, THFRSASUMO, FRSASUMOTU, SASUMOTUWE, SUMOTUWETH,
        MOTUWETHFRSA, TUWETHFRSASU, WETHFRSASUMO, THFRSASUMOTU, FRSASUMOTUWE, SASUMOTUWETH, SUMOTUWETHFR,
        PREHOLIDAYS, HOLIDAYS, WORKINGDAYS, ALLS,
    ])
    CLUSTERS_NAMES = "Mondays, Tuesdays, Wednesdays, Thursdays, Fridays, Saturdays, Sundays, " \
                     "Mondays and Tuesdays, Tuesdays and Wednesdays, Wednesdays and Thursdays, Thursdays and Fridays, " \
                     "Fridays and Saturdays, Weekends, Sundays and Mondays, from Monday to Wednesday, " \
                     "from Tuesday to Thursday, from Wednesday to Friday, from Thursday to Saturday, " \
                     "from Friday to Sunday, from Saturday to Monday, from Sunday to Tuesday, from Monday to Thursday, " \
                     "from Tuesday to Friday, from Wednesday to Saturday, from Thursday to Sunday, " \
                     "from Friday to Monday, from Saturday to Tuesday, from Sunday to Wednesday, " \
                     "from Monday to Friday, from Tuesday to Saturday, from Wednesday to Sunday, " \
                     "from Thursday to Monday, from Friday to Tuesday, from Saturday to Wednesday, " \
                     "from Sunday to Thursday, from Monday to Saturday, from Tuesday to Sunday, " \
                     "from Wednesday to Monday, from Thursday to Tuesday, from Friday to Wednesday, " \
                     "from Saturday to Thursday, from Sunday to Friday, Days before Holidays, Holidays, " \
                     "Working days, All days".split(", ")
    # CLUSTERS_DATES = np.array([(datetime.datetime(2021, 1, 1) + datetime.timedelta(i - 1)).strftime("%d/%m/%Y") for i in range(startidx, endidx+1)])
    CLUSTERS_DATES = np.array([(datetime.datetime(2021, 1, 1) + datetime.timedelta(i - 1)).timetuple().tm_yday for i in
                               range(startidx, endidx + 1)])
    return CLUSTERS[:, startidx - 1:endidx], CLUSTERS_NAMES, CLUSTERS_DATES,


if __name__ == "__main__":
    x, y, z = createClusters(1, 3)
    print(len(x), len(y))

    print(x.shape)
    print(z)
