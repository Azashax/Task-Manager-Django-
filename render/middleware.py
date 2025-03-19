# # from django.utils.deprecation import MiddlewareMixin
# #
# # class AddUserToEnvironMiddleware(MiddlewareMixin):
# #     def process_request(self, request):
# #         if request.user.is_authenticated:
# #             request.environ['user'] = request.user
#
# from django.utils.deprecation import MiddlewareMixin
# from .models import StorageActiveUser
#
# import logging
# logger = logging.getLogger(__name__)
#
#
# class LogRequestMiddleware(MiddlewareMixin):
#
#     def process_request(self, request):
#         try:
#             log_message = f"Processing request: {request.method} {request.path}"
#             print("log_message----", log_message)
#             logger.info(log_message)
#             if request.user.is_authenticated and request.method != "GET" and request.path_info.strip('/').split('/')[1] == "render":
#                 path = request.resolver_match
#                 StorageActiveUser.objects.create(
#                     user=request.user,
#                     table=request.body,
#                     action=request.method.lower(),
#                     fields=path
#                 )
#                 user_log_message = f"Authenticated request started by {request.user} to {path}"
#                 print(user_log_message)
#                 logger.info(user_log_message)
#             else:
#                 unauth_log_message = f"Unauthenticated request to {request.path}"
#                 print(unauth_log_message)
#                 logger.info(unauth_log_message)
#         except Exception as e:
#             error_message = f"Error logging request start: {e}"
#             print(error_message)
#             logger.error(error_message)
