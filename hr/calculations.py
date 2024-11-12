import datetime
from calendar import monthrange
from collections import namedtuple
from django.utils import timezone

class Badalat_3lawat():
    def __init__(self,abtdai,galaa_m3isha,gasima=0,atfal=0,moahil=0,shakhsia=0,ma3adin=0,aadoa=0,month=1,year=1970):
        self._abtdai = abtdai
        self._galaa_m3isha = galaa_m3isha
        self._asasi = (self._abtdai +self._galaa_m3isha)
        self._gasima = gasima
        self._atfal = atfal
        self._moahil = moahil
        self._shakhsia = shakhsia
        self._ma3adin = ma3adin
        self._aadoa = aadoa
        self._month = month
        self._year = year

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
    def month(self):
        return self._month
    
    @property
    def year(self):
        return self._year
    
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
    def __init__(self,Badalat:Badalat_3lawat,zaka_kafaf,zaka_nisab,m3ash=0,salafiat=0,jazaat=0,damga=1,sandog=0,sandog_kahraba=0,enable_sandog_kahraba=True,enable_youm_algoat_almosalaha=True,tarikh_2lmilad=None,m3ash_age=100,salafiat_sandog=0,khasm_salafiat_elsandog_min_elomoratab=False,dariba_mokaf2=0,salafiat_3la_2lmoratab=0,salafiat_3la_2lmokaf2=0):
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
        self._tarikh_2lmilad = tarikh_2lmilad
        self._m3ash_age = m3ash_age
        self._salafiat_sandog = salafiat_sandog
        self._salafiat_sandog_remain = 0
        self._salafiat_3la_2lmoratab = salafiat_3la_2lmoratab
        self._salafiat_3la_2lmokaf2 = salafiat_3la_2lmokaf2
        self._khasm_salafiat_elsandog_min_elomoratab = khasm_salafiat_elsandog_min_elomoratab

        self.mokaf2 = Mokaf2(self.Badalat,dariba_mokaf2,self.damga,False,0,salafiat_3la_2lmokaf2=salafiat_3la_2lmokaf2)

    @property
    def m3ash(self):
        return self._m3ash
    
    @property
    def tameen_ajtima3i(self):
        if self._m3ash > 0:
            return 0
        
        return self.Badalat.ajmali_almoratab *0.08
    
    @property
    def sandog(self):
        return self._sandog
    
    @property
    def employee_age(self):
        if not  self._tarikh_2lmilad:
            return 0
        
        now = datetime.date(year=self.Badalat.year,month=self.Badalat.month,day=1)
        delta = now - self._tarikh_2lmilad

        return delta.days // 365
    
    @property
    def dariba(self):
        if self.employee_age >= self._m3ash_age:
            return 0 
                
        return ((self.Badalat.ajmali_almoratab -self.Badalat.shakhsia -self.Badalat.moahil \
                 -self.Badalat.ajtima3ia_atfal -self.Badalat.ajtima3ia_gasima -self.Badalat.makhatir \
                 -1200 -115 -self.tameen_ajtima3i -self.m3ash -self.Badalat.aadoa) *0.15) +2.5
    
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
    def salafiat_sandog(self):
        return self._salafiat_sandog

    @property
    def salafiat_3la_2lmoratab(self):
        return self._salafiat_3la_2lmoratab

    @property
    def salafiat_sandog_remain(self):
        if self.khasm_salafiat_elsandog_min_elomoratab:
            return self.salafiat_sandog

        remain = (self.mokaf2.safi_2l2sti7gag - self.salafiat_sandog)
        if (remain < 0):
            return abs(remain) 
        else:
            return 0
    
    @property
    def khasm_salafiat_elsandog_min_elomoratab(self):
        return self._khasm_salafiat_elsandog_min_elomoratab

    @property
    def youm_algoat_almosalaha(self):
        if self._enable_youm_algoat_almosalaha: 
            return self.Badalat.ajmali_almoratab /30
        
        return 0

    @property
    def zakat(self):
        x = self.Badalat.ajmali_almoratab -self._zaka_kafaf
        if x >= self._zaka_nisab:
            return x *0.025
        return 0

    @property
    def ajmali_astgta3at_sanawia(self):
        ajmali = (self.sandog_kahraba +self.salafiat +self.youm_algoat_almosalaha +self.zakat +self.salafiat_sandog_remain +self.salafiat_3la_2lmoratab)
        return ajmali
    
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
            ('salafiat_sandog',self.salafiat_sandog_remain),
            ('salafiat_3la_2lmoratab',self.salafiat_3la_2lmoratab),
        ]

        props += [   
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

        self.employee = mobashara.employee

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

class Mokaf2():
    def __init__(self,Badalat:Badalat_3lawat,dariba=0.05,damga=1,khasm_salafiat_elsandog_min_elmokaf2=False,salafiat_sandog=0,salafiat_3la_2lmokaf2=0):
        self.Badalat = Badalat
        self._dariba = dariba
        self._damga = damga
        self._salafiat_3la_2lmokaf2 = salafiat_3la_2lmokaf2

        self._khasm_salafiat_elsandog_min_elmokaf2 = khasm_salafiat_elsandog_min_elmokaf2
        self._salafiat_sandog = salafiat_sandog

    @property
    def ajmali_2lmoratab(self):
        return self.Badalat.ajmali_almoratab

    @property
    def dariba(self):
        return (self.ajmali_2lmoratab *self._dariba)

    @property
    def damga(self):
        return self._damga
    
    @property
    def salafiat_sandog(self):
        safi = self.safi_2l2sti7gag_gabl_salafiat_sandog
        if self.khasm_salafiat_elsandog_min_elmokaf2:
            safi -= self._salafiat_sandog
            if (safi <= 0):
                return self.safi_2l2sti7gag_gabl_salafiat_sandog

        return self._salafiat_sandog

    @property
    def salafiat_3la_2lmokaf2(self):
        return self._salafiat_3la_2lmokaf2

    @property
    def khasm_salafiat_elsandog_min_elmokaf2(self):
        return self._khasm_salafiat_elsandog_min_elmokaf2
    
    @property
    def safi_2l2sti7gag_gabl_salafiat_sandog(self):
        return (self.ajmali_2lmoratab - self.dariba -self.damga -self.salafiat_3la_2lmokaf2)

    @property
    def safi_2l2sti7gag(self):
        safi = self.safi_2l2sti7gag_gabl_salafiat_sandog
        if self.khasm_salafiat_elsandog_min_elmokaf2:
            safi -= self.salafiat_sandog
            if (safi < 0):
                safi = 0
        return safi

    def __iter__(self):
        props = [
            ('ajmali_2lmoratab',self.ajmali_2lmoratab),
            ('dariba',self.dariba),
            ('damga',self.damga),
        ]

        if self.khasm_salafiat_elsandog_min_elmokaf2:
            props += [
                ('salafiat_sandog',self.salafiat_sandog),
            ]

        props += [
            ('salafiat_3la_2lmokaf2',self.salafiat_3la_2lmokaf2),
            ('safi_2l2sti7gag',self.safi_2l2sti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Mokaf2 ('+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])+')'
    
    def __repr__(self) -> str:
        return self.__str__()

class M2moria():
    def __init__(self,Badalat:Badalat_3lawat,year,month,m2moria_model,damga=1,m2moria_rate=1.5):
        self.Badalat = Badalat
        self._year = year
        self._month = month
        self._m2moria_model = m2moria_model
        self._damga = damga
        self._m2moria_rate = m2moria_rate

        self.employee = m2moria_model.employee

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
    def ajmali_2lmoratab(self):
        return self.Badalat.ajmali_almoratab

    @property
    def ajr_2lyoum(self):
        return (self.ajmali_2lmoratab /30)

    @property
    def ayam_2l3mal(self):
        start_dt = self._m2moria_model.start_dt
        end_dt = self._m2moria_model.end_dt_actual

        return (self.get_days_between_dates(start_dt,end_dt))

        # ayam_2lmobashra = self.ayam_2lshahar

        # if start_dt > self.akhar_youm_fi_2lshahar: #fi almostagbal
        #     return 0
        
        # if start_dt > self.awal_youm_fi_2lshahar:
        #     ayam_2lmobashra -= (self.get_days_between_dates(self.awal_youm_fi_2lshahar,start_dt))

        # if end_dt:
        #     if end_dt < self.awal_youm_fi_2lshahar:
        #         return 0
            
        #     if end_dt < self.akhar_youm_fi_2lshahar:
        #         ayam_2lmobashra -= (self.get_days_between_dates(end_dt,self.akhar_youm_fi_2lshahar))

        # return ayam_2lmobashra

    @property
    def damga(self):
        return self._damga

    @property
    def safi_2l2sti7gag(self):
        return (self.ajr_2lyoum *self._m2moria_rate *self.ayam_2l3mal) -self.damga

    def __iter__(self):
        props = [
            ('ajmali_2lmoratab',self.ajmali_2lmoratab),
            ('ajr_2lyoum',self.ajr_2lyoum),
            ('ayam_2l3mal',self.ayam_2l3mal),
            ('damga',self.damga),
            ('safi_2l2sti7gag',self.safi_2l2sti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'M2moria ('+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])+')'
    
    def __repr__(self) -> str:
        return self.__str__()

class Wi7datMosa3idaMokaf2tFarigMoratab():
    def __init__(self,payroll_2lsharika,payroll_2ljiha_2l2om,has_diff,damga,sandog):
        self._payroll_2lsharika = payroll_2lsharika
        self._payroll_2ljiha_2l2om = payroll_2ljiha_2l2om
        self._has_diff = has_diff
        self._damga = damga
        self._sandog = sandog
    
    @property
    def payroll_2lsharika(self):
        return self._payroll_2lsharika
    
    @property
    def payroll_2ljiha_2l2om(self):
        return self._payroll_2ljiha_2l2om
    
    @property
    def payroll_diff(self):
        return self.payroll_2lsharika - self.payroll_2ljiha_2l2om
    
    @property
    def has_diff(self):
        return self._has_diff
    
    @property
    def sandog(self):
        return self._sandog
        
    @property
    def dariba(self):
        return (self.payroll_diff *0.05)
    
    @property
    def damga(self):
        return self._damga

    @property
    def safi_alisti7gag(self):
        if self.has_diff:
            return (self.payroll_diff -self.dariba -self.sandog -self.damga)
        
        return 0

    def __iter__(self):
        props = [
            ('payroll_2ljiha_2l2om',self.payroll_2ljiha_2l2om),
            ('payroll_2lsharika',self.payroll_2lsharika),
            ('payroll_diff',self.payroll_diff),
            ('dariba',self.dariba),
            ('sandog',self.sandog),
            ('damga',self.damga),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Wi7datMosa3idaMokaf2tFarigMoratab => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class Wi7datMosa3idaMokaf2():
    def __init__(self,payroll_2lsharika,damga,salafiat_sandog=0):
        self._payroll_2lsharika = payroll_2lsharika
        self._damga = damga
        self._salafiat_sandog = salafiat_sandog
    
    @property
    def payroll_2lsharika(self):
        return self._payroll_2lsharika
                
    @property
    def dariba(self):
        return (self.payroll_2lsharika *0.05)
    
    @property
    def damga(self):
        return self._damga

    @property
    def salafiat_sandog(self):
        return self._salafiat_sandog

    @property
    def safi_alisti7gag(self):
        return (self.payroll_2lsharika -self.dariba -self.damga -self.salafiat_sandog)

    def __iter__(self):
        props = [
            ('payroll_2lsharika',self.payroll_2lsharika),
            ('dariba',self.dariba),
            ('salafiat_sandog',self.salafiat_sandog),
            ('damga',self.damga),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Wi7datMosa3idaMokaf2t => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class Ta3agodMosimiMoratab():
    def __init__(self,ajmali,damga):
        self._ajmali = ajmali
        self._damga = damga
    
    @property
    def ajmali(self):
        return self._ajmali
    
    @property
    def asasi(self):
        return self.ajmali*0.27
        
    @property
    def sakan(self):
        return self.ajmali*0.14
        
    @property
    def tar7il(self):
        return self.ajmali*0.11
        
    @property
    def ma3isha(self):
        return self.ajmali*0.11
        
    @property
    def el3laj(self):
        return self.ajmali*0.10
        
    @property
    def laban(self):
        return self.ajmali*0.07
        
    @property
    def tabi3at_3amal(self):
        return self.ajmali*0.20
                
    @property
    def dariba(self):
        return (self.ajmali *0.05)
    
    @property
    def damga(self):
        return self._damga

    @property
    def t2min(self):
        return (self.ajmali *0.08)
    

    @property
    def safi_alisti7gag(self):
        return (self.ajmali -self.dariba -self.damga -self.t2min)

    def __iter__(self):
        props = [
            ('asasi',self.asasi),
            ('sakan',self.sakan),
            ('tar7il',self.tar7il),
            ('ma3isha',self.ma3isha),
            ('el3laj',self.el3laj),
            ('laban',self.laban),
            ('tabi3at_3amal',self.tabi3at_3amal),
            ('ajmali',self.ajmali),
            ('damga',self.damga),
            ('t2min',self.t2min),
            ('dariba',self.dariba),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Ta3agodMosimiPayroll => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class Ta3agodMosimiMokaf2():
    def __init__(self,mokaf2,damga):
        self._mokaf2 = mokaf2
        self._damga = damga
    
    @property
    def mokaf2(self):
        return self._mokaf2
                    
    @property
    def dariba(self):
        return (self.mokaf2 *0.05)
    
    @property
    def damga(self):
        return self._damga

    @property
    def safi_alisti7gag(self):
        return (self.mokaf2 -self.dariba -self.damga)

    def __iter__(self):
        props = [
            ('mokaf2',self.mokaf2),
            ('damga',self.damga),
            ('dariba',self.dariba),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Ta3agodMosimiMokaf2 => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class MajlisEl2daraMokaf2():
    def __init__(self,mokaf2,damga,asasi,gasima,atfal,moahil,sandog):
        self._mokaf2 = mokaf2
        self._damga = damga
        self._asasi = asasi

        self._gasima = gasima
        self._atfal = atfal
        self._moahil = moahil

        self._sandog = sandog
    
    @property
    def asasi(self):
        return self._asasi
                    
    @property
    def mokaf2(self):
        return self._mokaf2
                    
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
    def dariba(self):
        return (self.mokaf2 *0.15)
    
    @property
    def damga(self):
        return self._damga

    @property
    def sandog(self):
        return self._sandog

    @property
    def ajmali_el2stigta3(self):
        return (self.dariba +self.damga)
    
    @property
    def safi_alisti7gag(self):
        return (self.mokaf2 -self.ajmali_el2stigta3)

    def __iter__(self):
        props = [
            ('mokaf2',self.mokaf2),
            ('dariba',self.dariba),
            ('damga',self.damga),
            ('ajmali_el2stigta3',self.ajmali_el2stigta3),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'MajlisEl2daraMokaf2 => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class BadalatModir3am():
    def __init__(self,abtdai,gasima=0,atfal=0,moahil=0):
        self._abtdai = abtdai
        self._asasi = self._abtdai
        self._gasima = gasima
        self._atfal = atfal
        self._moahil = moahil

    @property
    def abtdai(self):
        return self._abtdai
    
    @property
    def galaa_m3isha(self):
        return self.abtdai*0.50
    
    @property
    def asasi(self):
        return self._asasi
    
    @property
    def tabi3at_3mal(self):
        return self._asasi *0.25
    
    @property
    def mas2olia(self):
        return self._asasi *1.45
    
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
    def ajmali_almoratab(self):
        return (self._asasi +self.tabi3at_3mal +self.galaa_m3isha +self.mas2olia \
                 +self.moahil +self.ajtima3ia_gasima +self.ajtima3ia_atfal)

    def __iter__(self):
        props = [
            ('abtdai',self.abtdai),
            ('galaa_m3isha',self.galaa_m3isha),
            ('tabi3at_3mal',self.tabi3at_3mal),
            ('mas2olia',self.mas2olia),
            ('ajtima3ia_gasima',self.ajtima3ia_gasima),
            ('ajtima3ia_atfal',self.ajtima3ia_atfal),
            ('moahil',self.moahil),
            ('ajmali_almoratab',self.ajmali_almoratab),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'BadalatModir3am => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class KhosomatModir3am():
    def __init__(self,Badalat:BadalatModir3am,zaka_kafaf,zaka_nisab,salafiat=0,damga=1,sandog=0):
        self.Badalat = Badalat
        self._zaka_kafaf = zaka_kafaf
        self._zaka_nisab = zaka_nisab
        self._salafiat = salafiat
        self._damga = damga
        self._sandog = sandog
    
    @property
    def tameen_ajtima3i(self):
        return self.Badalat.ajmali_almoratab *0.08
    
    @property
    def sandog(self):
        return self._sandog
    
    @property
    def dariba(self):
        return ((self.Badalat.ajmali_almoratab -self.tameen_ajtima3i) *0.05) 
    
    @property
    def damga(self):
        return self._damga

    @property
    def salafiat(self):
        return self._salafiat

    @property
    def zakat(self):
        x = self.Badalat.ajmali_almoratab -self._zaka_kafaf
        if x >= self._zaka_nisab:
            return x *0.025
        return 0

    @property
    def ajmali_astgta3at_koli(self):
        return (self.tameen_ajtima3i +self.sandog +self.dariba +self.damga +self.zakat )
    
    @property
    def safi_alisti7gag(self):
        return (self.Badalat.ajmali_almoratab -self.ajmali_astgta3at_koli)

    def __iter__(self):
        props = [
            ('tameen_ajtima3i',self.tameen_ajtima3i),
            ('sandog',self.sandog),
            ('dariba',self.dariba),
            ('zakat',self.zakat),
            ('damga',self.damga),
            ('ajmali_astgta3at_koli',self.ajmali_astgta3at_koli),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'KhosomatModir3am => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class Mokaf2Modir3am():
    def __init__(self,Badalat:Badalat_3lawat,dariba=0.05,damga=1):
        self.Badalat = Badalat
        self._dariba = dariba
        self._damga = damga

    @property
    def ajmali_2lmoratab(self):
        return self.Badalat.ajmali_almoratab

    @property
    def dariba(self):
        return (self.ajmali_2lmoratab *self._dariba)

    @property
    def damga(self):
        return self._damga
    
    @property
    def safi_alisti7gag(self):
        return (self.ajmali_2lmoratab - self.dariba -self.damga)

    def __iter__(self):
        props = [
            ('ajmali_2lmoratab',self.ajmali_2lmoratab),
            ('dariba',self.dariba),
            ('damga',self.damga),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Mokaf2Modir3am ('+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])+')'
    
    def __repr__(self) -> str:
        return self.__str__()

class PayrollValidation():
    def __init__(self,Payroll,Drajat3lawat):
        self.Payroll = Payroll
        self.Drajat3lawat = Drajat3lawat

    def khosomat_validation(self):
        data = []

        for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in self.Payroll.all_employees_payroll_from_db():
            khosomat_list = [round(k[1],2) for k in khosomat]
            l = [emp.code,emp.name,self.Drajat3lawat.DRAJAT_CHOICES[draja_wazifia],self.Drajat3lawat.ALAWAT_CHOICES[alawa_sanawia],badalat.ajmali_almoratab] + khosomat_list
            if khosomat.ajmali_astgta3at_koli > badalat.ajmali_almoratab:
                data.append(l)

        return data
    
    def is_all_khosomat_valid(self):
        flag = True
        for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in self.Payroll.all_employees_payroll_from_db():
            if khosomat.ajmali_astgta3at_koli > badalat.ajmali_almoratab:
                return False

        return flag
