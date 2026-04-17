from.Logger import Info, Fail, Warning, Print_Values

# For now this is for testing. However, this will be highly useful when applying the Ontology

def decorator(func):
    def wrapper(*args, **kwargs):
        # With this you can read assigned values. Therefore, they can be checked, whether they follow the ontology
        # Also reducing optional values or preprocess data, to make it valid.
        Warning("This decorator was called and these are the parameters of the function")
        for key, value in kwargs.items():
            print("%s == %s" % (key, value))

        # Function call
        temp = func(*args, **kwargs)
        

        print("Something is happening after the function is called.")
        print("Output of the function is: {}".format(temp))

        return temp

    return wrapper

