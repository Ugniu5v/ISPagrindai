from django.shortcuts import redirect
from django.http import HttpRequest
from django.urls import reverse
from django.http import QueryDict

def login_required(arg):
    ''' 
    Dekoratorius kuris nukreipia į prisijungimą jeigu nėra naudotojo sesijoje bei neieleidžia prieiti prie puslapio jeigu neatitinka rolė.  
    Užtikrina kad `request.session` bus:  
    ```
    request.session["user"] = True
    request.session["user_id"] = user.pk
    request.session["user_name"] = user.username
    request.session["user_email"] = user.email
    request.session["user_role"] = user.role
    ```
    '''
    # Dekoratorius be argumentu
    if callable(arg):
        func = arg
        def wrapper(request, *args, **kwargs):
            # Ar prisijungęs
            if "user" not in request.session:
                q = QueryDict(mutable=True)
                q["next"] = request.get_full_path()
                return redirect(f"{reverse('users:userLogin')}?{q.urlencode()}")

            return func(request, *args, **kwargs)
        return wrapper
    # Dekoratorius su argumentu
    else:
        role: str = arg
        def decorator(func):
            def wrapper(request, *args, **kwargs):
                # Ar prisijungęs
                if "user" not in request.session:
                    q = QueryDict(mutable=True)
                    q["next"] = request.get_full_path()
                    return redirect(f"{reverse('users:userLogin')}?{q.urlencode()}")

                # Ar atitinka rolė
                if role is not None and request.session["user_role"] != role:
                    return redirect("homepage")
                
                return func(request, *args, **kwargs)
            return wrapper
        return decorator
    
# Dekoratoriaus pavizdys

# def d(arg):
#     if callable(arg):  # Assumes optional argument isn't.
#         def newfn():
#             print('my default message')
#             return arg()
#         return newfn
#     else:
#         def d2(fn):
#             def newfn():
#                 print(arg)
#                 return fn()
#             return newfn
#         return d2