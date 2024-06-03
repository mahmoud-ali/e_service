import datetime
from calendar import monthrange
from collections import namedtuple

class Badalat_3lawat():
    def __init__(self,abtdai,galaa_m3isha,gasima=0,atfal=0,moahil=0,shakhsia=0,ma3adin=0,aadoa=0):
        self._abtdai = abtdai
        self._galaa_m3isha = galaa_m3isha
        self._asasi = (self._abtdai +self._galaa_m3isha)
        self._gasima = gasima
        self._atfal = atfal
        self._moahil = moahil
        self._shakhsia = shakhsia
        self._ma3adin = ma3adin
        self._aadoa = aadoa

    @property
    def abtdai(self):
        return self._abtdai
    
    @property
    def galaa_m3isha(self):
        return self._galaa_m3isha
    
    @property
    def asasi(self):
        return self._asasi
    
    @property
    def tabi3at_3mal(self):
        return self._asasi *0.75
    
    @property
    def tamtheel(self):
        return self._asasi *0.20
    
    @property
    def mihna(self):
        return self._asasi *0.50
    
    @property
    def ma3adin(self):
        return self._ma3adin
    
    @property
    def makhatir(self):
        return self.ma3adin *6

    @property
    def aadoa(self):
        return self._aadoa

    @property
    def ajtima3ia_gasima(self):
        return self._gasima
    
    @property
    def ajtima3ia_atfal(self):
        return self._atfal
    
    @property
    def moahil(self):
        return self._moahil
    
    @property
    def shakhsia(self):
        return self._shakhsia
    
    @property
    def ajmali_almoratab(self):
        return (self._asasi +self.tabi3at_3mal +self.tamtheel +self.mihna +self.ma3adin \
                 +self.makhatir +self.aadoa +self.ajtima3ia_gasima +self.ajtima3ia_atfal \
                 +self.moahil +self.shakhsia)

    def __iter__(self):
        props = [
            ('abtdai',self.abtdai),
            ('galaa_m3isha',self.galaa_m3isha),
            ('asasi',self.asasi),
            ('tabi3at_3mal',self.tabi3at_3mal),
            ('tamtheel',self.tamtheel),
            ('mihna',self.mihna),
            ('ma3adin',self.ma3adin),
            ('makhatir',self.makhatir),
            ('aadoa',self.aadoa),
            ('ajtima3ia_gasima',self.ajtima3ia_gasima),
            ('ajtima3ia_atfal',self.ajtima3ia_atfal),
            ('moahil',self.moahil),
            ('shakhsia',self.shakhsia),
            ('ajmali_almoratab',self.ajmali_almoratab),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Badalat => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class Khosomat():
    def __init__(self,Badalat:Badalat_3lawat,zaka_kafaf,zaka_nisab,m3ash=0,salafiat=0,jazaat=0,damga=1,sandog=0,sandog_kahraba=0,enable_sandog_kahraba=True,enable_youm_algoat_almosalaha=True):
        self.Badalat = Badalat
        self._zaka_kafaf = zaka_kafaf
        self._zaka_nisab = zaka_nisab
        self._m3ash = m3ash
        self._salafiat = salafiat
        self._jazaat = jazaat
        self._damga = damga
        self._sandog = sandog
        self._sandog_kahraba = sandog_kahraba
        self._enable_sandog_kahraba = enable_sandog_kahraba
        self._enable_youm_algoat_almosalaha = enable_youm_algoat_almosalaha

    @property
    def tameen_ajtima3i(self):
        return self.Badalat.ajmali_almoratab *0.08
    
    @property
    def m3ash(self):
        return self._m3ash
    
    @property
    def sandog(self):
        return self._sandog
    
    @property
    def dariba(self):
        return (self.Badalat.ajmali_almoratab -self.Badalat.shakhsia -self.Badalat.moahil \
                 -self.Badalat.ajtima3ia_atfal -self.Badalat.ajtima3ia_gasima -self.Badalat.makhatir \
                 -1200 -116 -self.tameen_ajtima3i) *0.15 +2.5
    
    @property
    def damga(self):
        return self._damga

    @property
    def ajmali_astgta3at_asasia(self):
        return (self.tameen_ajtima3i +self.m3ash +self.sandog +self.dariba +self.damga)

    @property
    def sandog_kahraba(self):
        if self._enable_sandog_kahraba:
            return self._sandog_kahraba
        
        return 0

    @property
    def salafiat(self):
        return self._salafiat

    @property
    def youm_algoat_almosalaha(self):
        if self._enable_youm_algoat_almosalaha: 
            return self.Badalat.ajmali_almoratab /30
        
        return 0

    @property
    def zakat(self):
        x = self.Badalat.ajmali_almoratab -self._zaka_kafaf
        if x > self._zaka_nisab:
            return x *0.025
        return 0

    @property
    def ajmali_astgta3at_sanawia(self):
        return (self.sandog_kahraba +self.salafiat +self.youm_algoat_almosalaha +self.zakat)
    
    @property
    def jazaat(self):
        return self._jazaat

    @property
    def ajmali_astgta3at_koli(self):
        return (self.ajmali_astgta3at_asasia +self.ajmali_astgta3at_sanawia +self.jazaat)
    
    @property
    def safi_alisti7gag(self):
        return (self.Badalat.ajmali_almoratab -self.ajmali_astgta3at_koli)

    def __iter__(self):
        props = [
            ('tameen_ajtima3i',self.tameen_ajtima3i),
            ('m3ash',self.m3ash),
            ('sandog',self.sandog),
            ('dariba',self.dariba),
            ('damga',self.damga),
            ('ajmali_astgta3at_asasia',self.ajmali_astgta3at_asasia),
        ]

        if self._enable_sandog_kahraba:
            props += [   
                ('sandog_kahraba',self.sandog_kahraba),
            ]
        props += [   
            ('salafiat',self.salafiat),
         ]
        
        if self._enable_youm_algoat_almosalaha:
            props += [   
                ('youm_algoat_almosalaha',self.youm_algoat_almosalaha),
            ]
            
        props += [   
            ('zakat',self.zakat),
            ('ajmali_astgta3at_sanawia',self.ajmali_astgta3at_sanawia),
            ('jazaat',self.jazaat),
            ('ajmali_astgta3at_koli',self.ajmali_astgta3at_koli),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Khosomat => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class Mobashara():
    def __init__(self,year,month,mobashara,vactions=[],takleef=[]):
        self._year = year
        self._month = month
        self._mobashara = mobashara
        self._vactions = vactions
        self._takleef = takleef

        if not self._mobashara.end_dt:
            self._mobashara.end_dt = self.akhar_youm_fi_2lshahar

        self.ayam_2l2jazaa = 0
        if hasattr(self,'_mobashara'):
            for ftra in self._vactions:
                if ftra.start_dt < self._mobashara.start_dt and self._mobashara.start_dt > self.awal_youm_fi_2lshahar:
                    ftra.start_dt = self._mobashara.start_dt

                if ftra.start_dt < self.awal_youm_fi_2lshahar:
                    ftra.start_dt = self.awal_youm_fi_2lshahar

                if not ftra.end_dt_actual or ftra.end_dt_actual > self.akhar_youm_fi_2lshahar:
                    ftra.end_dt_actual = self.akhar_youm_fi_2lshahar

                if hasattr(self._mobashara,'end_dt_actual') and self._mobashara.end_dt < self.akhar_youm_fi_2lshahar:
                    ftra.end_dt_actual = self._mobashara.end_dt
                self.ayam_2l2jazaa += (self.get_days_between_dates(ftra.start_dt,ftra.end_dt_actual) +1)

        self.ftrat_2ltaklif = []
        for ftra in self._takleef:
            if ftra.start_dt < self.awal_youm_fi_2lshahar:
                ftra.start_dt = self.awal_youm_fi_2lshahar

            if not hasattr(ftra,'end_dt_actual') or not ftra.end_dt_actual or ftra.end_dt_actual > self.akhar_youm_fi_2lshahar:
                ftra.end_dt_actual = self.akhar_youm_fi_2lshahar

            c =  (self.get_days_between_dates(ftra.start_dt,ftra.end_dt_actual) +1)
            self.ftrat_2ltaklif.append((c,ftra.mokalaf_rate))

        self.ayam_2ltaklif = sum(map(lambda obj: obj[0] , self.ftrat_2ltaklif))

        self.gemat_2ltaklif = sum(map(lambda obj: obj[0]*obj[1] , self.ftrat_2ltaklif))

    @property
    def ayam_2lshahar(self):
        return monthrange(self._year, self._month)[1]

    @property
    def awal_youm_fi_2lshahar(self):
        return datetime.date(self._year,self._month,1)

    @property
    def akhar_youm_fi_2lshahar(self):
        return datetime.date(self._year,self._month,self.ayam_2lshahar)

    def get_days_between_dates(self,start,end):
        if start > end:
            return -1

        return (end - start).days
    
    @property
    def ayam_2lmobashara_2lkoliah(self):
        if not self._mobashara: #sha'9 '3ir mobasher
            return 0
                
        start_dt = self._mobashara.start_dt
        end_dt = self._mobashara.end_dt

        ayam_2lmobashra = self.ayam_2lshahar

        if start_dt > self.akhar_youm_fi_2lshahar: #mobashara fi almostagbal
            return 0
        
        if start_dt > self.awal_youm_fi_2lshahar:
            ayam_2lmobashra -= (self.get_days_between_dates(self.awal_youm_fi_2lshahar,start_dt))

        if end_dt:
            if end_dt < self.awal_youm_fi_2lshahar:
                return 0
            
            if end_dt < self.akhar_youm_fi_2lshahar:
                ayam_2lmobashra -= (self.get_days_between_dates(end_dt,self.akhar_youm_fi_2lshahar))

        return ayam_2lmobashra

    def get_overlapping(self,start_dt1,end_dt1,start_dt2,end_dt2):
        Range = namedtuple('Range', ['start', 'end'])

        r1 = Range(start=start_dt1, end=end_dt1)
        r2 = Range(start=start_dt2, end=end_dt2)
        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        delta = (earliest_end - latest_start).days + 1
        overlap = max(0, delta)
        return overlap    

    @property
    def ayam_2ltaklif_2lmotgati3(self):
        if not self._mobashara or not self._takleef:
            return 0

        count = 0
        for ftra in self._takleef:
            count += self.get_overlapping(self._mobashara.start_dt,self._mobashara.end_dt,ftra.start_dt,ftra.end_dt_actual)

        return count

    @property
    def ayam_2lmobashara_2lsafi(self):        
        return (self.ayam_2lmobashara_2lkoliah - self.ayam_2l2jazaa - self.ayam_2ltaklif_2lmotgati3)

    @property
    def safi_2l2sti7gag(self):
        mobashra_safi_2lgima = self.ayam_2lmobashara_2lsafi *self._mobashara.employee_rate

        return (mobashra_safi_2lgima+self.gemat_2ltaklif)

    def __iter__(self):
        props = [
            ('ayam_2lmobashara_2lsafi',self.ayam_2lmobashara_2lsafi),
            ('ayam_2l2jazaa',self.ayam_2l2jazaa),
            ('ayam_2ltaklif',self.ayam_2ltaklif),
            ('safi_2l2sti7gag',self.safi_2l2sti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Mobashara ('+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])+')'
    
    def __repr__(self) -> str:
        return self.__str__()

def example():
    # badal = Badalat_3lawat(15022.0281121467,10708.1720490482,gasima=25000,atfal=60000,moahil=20000,ma3adin=52736.6266882452)
    # khosomat = Khosomat(badal,215617,156159,sandog=20000)

    # print(badal)
    # print("\n")
    # print(khosomat)

    year = 2024
    month = 5

    class Empty:
        def __str__(self) -> str:
            end = None
            if hasattr(self,'end_dt'):
                end = self.end_dt
            elif hasattr(self,'end_dt_actual'):
                end = self.end_dt_actual

            return f'start: {self.start_dt}, end: {end}'
        def __repr__(self) -> str:
            return self.__str__()

    obj = Empty()

    #mobashara tbd2 o tantahi khlal 2lshahr
    obj.start_dt = datetime.date(year,month,2)
    obj.end_dt = datetime.date(year,month,15)

    mobashara = Mobashara(year,month,obj)

    #mobashara tbd2 khlal 2lshahr o bdon nehaia
    obj.start_dt = datetime.date(year,month,2)
    obj.end_dt = None

    mobashara = Mobashara(year,month,obj)
    print("mobashara tbd2 khlal 2lshahr o bdon nehaia",obj.start_dt,obj.end_dt,mobashara.ayam_2lmobashara_2lkoliah)

    #mobashara fi awal youm fi 2lshahr o bdon nehaia
    obj.start_dt = datetime.date(year,month,1)
    obj.end_dt = None

    mobashara = Mobashara(year,month,obj)
    print("mobashara fi awal youm fi 2lshahr o bdon nehaia",obj.start_dt,obj.end_dt,mobashara.ayam_2lmobashara_2lkoliah)

    #mobashara gabl 2lshahr o bdon nehaia
    obj.start_dt = datetime.date(year,month-1,2)
    obj.end_dt = None

    mobashara = Mobashara(year,month,obj)
    print("mobashara gabl 2lshahr o bdon nehaia",obj.start_dt,obj.end_dt,mobashara.ayam_2lmobashara_2lkoliah)

    #mobashara entahat gabl awal 2lshahr
    obj.start_dt = datetime.date(year,month-2,2)
    obj.end_dt = datetime.date(year,month-1,2)

    mobashara = Mobashara(year,month,obj)
    print("mobashara entahat gabl awal 2lshahr",obj.start_dt,obj.end_dt,mobashara.ayam_2lmobashara_2lkoliah)

    #mobashara entahat fi awal 2lshahr
    obj.start_dt = datetime.date(year,month-2,2)
    obj.end_dt = datetime.date(year,month,1)

    mobashara = Mobashara(year,month,obj)
    print("mobashara entahat fi awal 2lshahr",obj.start_dt,obj.end_dt,mobashara.ayam_2lmobashara_2lkoliah)

    #mobashara entahat fi n9 2lshahr
    obj.start_dt = datetime.date(year,month-2,2)
    obj.end_dt = datetime.date(year,month,15)

    mobashara = Mobashara(year,month,obj)
    print("mobashara entahat fi n9 2lshahr",obj.start_dt,obj.end_dt,mobashara.ayam_2lmobashara_2lkoliah)

    #mobashara entahat fi akher 2lshahr
    obj.start_dt = datetime.date(year,month-2,2)
    obj.end_dt = datetime.date(year,month,31)

    mobashara = Mobashara(year,month,obj)
    print("mobashara entahat fi akher 2lshahr",obj.start_dt,obj.end_dt,mobashara.ayam_2lmobashara_2lkoliah)

    #ayam 2l2jazaa
    obj.start_dt = datetime.date(year,month,15)
    obj.end_dt = datetime.date(year,month,31)
    obj.employee_rate = 50000.0
    obj1 = Empty()
    obj1.start_dt = datetime.date(year,month-1,2)
    obj1.end_dt_actual = datetime.date(year,month,6)
    obj2 = Empty()
    obj2.start_dt = datetime.date(year,month,20)
    obj2.end_dt_actual = datetime.date(year,month+1,5)

    obj3 = Empty()
    obj3.start_dt = datetime.date(year,month,13)
    obj3.end_dt_actual = datetime.date(year,month,14)
    obj3.mokalaf_rate = 60000.0

    mobashara = Mobashara(year,month,obj,[obj1,obj2],[obj3])
    print(mobashara)

    return mobashara
