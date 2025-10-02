import traceback
from django.http import HttpResponseServerError

class Debug500Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            print(f"❌ INTERNAL SERVER ERROR: {e}")
            traceback.print_exc()

            return HttpResponseServerError("Internal Server Error")
