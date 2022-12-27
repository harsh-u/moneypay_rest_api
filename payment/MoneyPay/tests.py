from django.test import TestCase

# Create your tests here.


# @api_view(['GET', 'POST'])
# def snippet_list(request):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     if request.method == 'GET':
#         print("I am in Get")
#
#         users = User.objects.all().order_by('-date_joined')
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         print(request.data)
#         is_valid = check_user_data(request.data)
#         if not is_valid:
#             return Response("Not a valid user", status=status.HTTP_400_BAD_REQUEST)
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# def check_user_data(user_data):
#     username = user_data.get("username")
#     regex = '[a-zA-z0-9]$'
#     if len(username) > 4:
#         if re.search(regex, username):
#             return True
#         else:
#             print("Not in correct format")
#             return False
#     print("username length is too small")
#     return False
