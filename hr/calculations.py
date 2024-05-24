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
        return 'Badalat => \n'+'\n'.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class Khosomat():
    def __init__(self,Badalat:Badalat_3lawat,zakat_kafaf,zakat_nisab,m3ash=0,salafiat=0,jazaat=0,damga=1,sandog=0,sandog_kahraba=0):
        self.Badalat = Badalat
        self._zakat_kafaf = zakat_kafaf
        self._zakat_nisab = zakat_nisab
        self._m3ash = m3ash
        self._salafiat = salafiat
        self._jazaat = jazaat
        self._damga = damga
        self._sandog = sandog
        self._sandog_kahraba = sandog_kahraba

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
        return self._sandog_kahraba

    @property
    def salafiat(self):
        return self._salafiat

    @property
    def youm_algoat_almosalaha(self):
        return self.Badalat.ajmali_almoratab /30

    @property
    def zakat(self):
        x = self.Badalat.ajmali_almoratab -self._zakat_kafaf
        if x > self._zakat_nisab:
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
            ('sandog_kahraba',self.sandog_kahraba),
            ('salafiat',self.salafiat),
            ('youm_algoat_almosalaha',self.youm_algoat_almosalaha),
            ('zakat',self.zakat),
            ('ajmali_astgta3at_sanawia',self.ajmali_astgta3at_sanawia),
            ('jazaat',self.jazaat),
            ('ajmali_astgta3at_koli',self.ajmali_astgta3at_koli),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Khosomat => \n'+'\n'.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

def example():
    badal = Badalat_3lawat(15022.0281121467,10708.1720490482,gasima=25000,atfal=60000,moahil=20000,ma3adin=52736.6266882452)
    khosomat = Khosomat(badal,215617,156159,sandog=20000)

    print(badal)
    print("\n")
    print(khosomat)
