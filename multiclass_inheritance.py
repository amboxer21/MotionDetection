class Animal(object):
    def __init__(self,animal,*args):
        super(Animal, self).__init__(*args)
        print("init " + animal)

class GoodBoy(object):
    def __init__(self,goodboy,*args):
        super(GoodBoy, self).__init__(*args)
        print("init " + goodboy )

class Dog(object):
    def __init__(self,opts,*args):
        super(Dog, self).__init__(*args)
        print("args[0] => " + str(opts[0]))
        print("args[1] => " + str(opts[1]))
        for arg in opts:
            print("init " + str(arg))

class GermanShepard(Dog,GoodBoy,Animal):
    def __init__(self):
        print("init GermanShepard")
        super(GermanShepard,self).__init__(["Dog","trr"],"GoodBoy","Animal")

if __name__ == '__main__':
    GermanShepard()
