class Badalat_3lawat():
    def __init__(self,asasi,galaa_m3isha,badel_sakan,badel_tar7il,tabi3at_3amal,badel_laban,badel_3laj):
        self._asasi = asasi
        self._galaa_m3isha = galaa_m3isha
        self._badel_sakan = badel_sakan
        self._badel_tar7il = badel_tar7il
        self._tabi3at_3amal = tabi3at_3amal
        self._badel_laban = badel_laban
        self._badel_3laj = badel_3laj

    @property
    def asasi(self):
        return self._asasi

    @property
    def galaa_m3isha(self):
        return self._galaa_m3isha

    @property
    def badel_sakan(self):
        return self._badel_sakan

    @property
    def badel_tar7il(self):
        return self._badel_tar7il

    @property
    def tabi3at_3amal(self):
        return self._tabi3at_3amal

    @property
    def badel_laban(self):
        return self._badel_laban

    @property
    def badel_3laj(self):
        return self._badel_3laj
    
    @property
    def ajmali_almoratab(self):
        return (self.asasi+self.galaa_m3isha+self.badel_sakan+self.badel_tar7il+self.tabi3at_3amal+self.badel_laban+self.badel_3laj)

    def __iter__(self):
        props = [
            ('asasi',self.asasi),
            ('galaa_m3isha',self.galaa_m3isha),
            ('badel_sakan',self.badel_sakan),
            ('badel_tar7il',self.badel_tar7il),
            ('tabi3at_3amal',self.tabi3at_3amal),
            ('badel_laban',self.badel_laban),
            ('badel_3laj',self.badel_3laj),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Badalat => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])

class Khosomat():
    def __init__(self,Badalat:Badalat_3lawat,damga=1):
        self.Badalat = Badalat
        self._damga = damga

    @property
    def tameen_ajtima3i(self):
        return self.Badalat.ajmali_almoratab *0.08
    
    @property
    def dariba(self):
        return self.Badalat.ajmali_almoratab *0.05
    
    @property
    def damga(self):
        return self._damga

    @property
    def safi_alisti7gag(self):
        return (self.Badalat.ajmali_almoratab - self.tameen_ajtima3i - self.dariba - self.damga)

    def __iter__(self):
        props = [
            ('tameen_ajtima3i',self.tameen_ajtima3i),
            ('dariba',self.dariba),
            ('damga',self.damga),
            ('ajmali_almoratab',self.Badalat.ajmali_almoratab),
            ('safi_alisti7gag',self.safi_alisti7gag),
        ]

        for p in props:
            yield(p[0],p[1])
    
    def __str__(self) -> str:
        return 'Khosomat => '+', '.join([f'{b[0]}: {round(b[1],2)}' for b in self.__iter__()])
