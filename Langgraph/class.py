class Gfg:
    def __init__(self):
        print("Instance ban gaya bhai!")

    def __call__(self):          # ← yeh magic hai
        print("Ab main function ki tarah call ho raha hoon!")

# Object banao
obj = Gfg()        # Yeh __init__ call karega

# Ab object ko call karo jaise function
obj()              # Yeh __call__ call karega
obj()              # Phir se call kar sakte ho