from khatabat.models import HarkatKhatabat,Khatabat,Motab3atKhatabat

# arr = [('1', 3), ('Gm-11-1', 8), ('Gm-11-2', 10), ('Gm-11-3', 11), ('Gm-11-4', 8), ('Gm-11-5', 8), ('Gm-11-6', 4), ('Gm-11-7', 15), ('Gm-11-8', 16), ('Gm-11-9', 4), ('Gm-11-10', 12), ('Gm-11-11', 4), ('Gm-11-12', 5), ('Gm-11-13', 4), ('Gm-11-14', 4), ('Gm-11-15', 4), ('Gm-11-16', 4), ('Gm-11-17', 4), ('Gm-11-18', 4), ('Gm-11-19', 4), ('Gm-11-20', 4), ('Gm-11-21', 4), ('Gm-11-32', 4), ('Gm-11-42', 21), ('Gm-11-43', 20), ('Gm-11-44', 22), ('Gm-12-1', 4), ('Gm-12-3', 5), ('Gm-12-4', 13), ('Gm-11-22', 4), ('Gm-11-23', 4), ('Gm-11-41', 4), ('Gm-11-27', 4), ('Gm-11-26', 4), ('Gm-11-25', 4), ('Gm-11-31', 25), ('Gm-11-31', 4), ('Gm-11-33', 4), ('Gm-11-34', 4), ('Gm-11-35', 4), ('Gm-11-36', 4), ('Gm-11-42', 5), ('Gm-12-5', 28), ('Gm-12-6', 4), ('Gm-12-7', 4), ('Gm-12-8', 4), ('Gm-12-9', 4), ('Gm-12-10', 4), ('Gm-12-11', 4), ('Gm-12-12', 20), ('Gm-12-13', 4), ('Gm-12-14', 18)]
def load_old_forwarded_to(arr):
    for a in arr:
        obj = HarkatKhatabat.objects.filter(letter__letter_number=a[0],).first()
        obj.forwarded_to.add(a[1])
        obj.save()

def add_year_to_letter_number(year=25):
    qs = Khatabat.objects.all()
    for obj in qs:
        id = obj.letter_number
        a = obj.letter_number.split('-')
        if len(a) == 3:
            new_letter = f'{a[0]}-{year}-{a[1]}-{a[2]}'.upper()

            obj.letter_number = new_letter
            obj.save()

            qs2 = HarkatKhatabat.objects.filter(letter=id)
            qs2.update(letter=new_letter)

            qs3 = Motab3atKhatabat.objects.filter(letter=id)
            qs3.update(letter=new_letter)

            obj = Khatabat.objects.get(letter_number=id).delete()
            print(id)

