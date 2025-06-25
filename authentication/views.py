from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from django.contrib.auth import authenticate
from .models import CustomUser, Organization, Member
from .serializers import SignupSerializer, OrganizationSerializer, MemberSerializer
from .validators import validate_required_field


class SignupAPIView(APIView):
    def post(self, request):
        context = {"success": 1, "message": "User registered successfully", "data": {}}
        try:
            serializer = SignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            context['data'] = SignupSerializer(user).data
        except ValidationError as e:
            context['success'] = 0
            context['message'] = e.detail
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)


class LoginAPIView(APIView):
    def post(self, request):
        context = {"success": 1, "message": "Login successful", "data": {}}
        try:
            email = validate_required_field(request.data.get('email'), "email")
            password = validate_required_field(request.data.get('password'), "password")

            user = authenticate(request, email=email, password=password)
            if user is None:
                raise ValidationError("Invalid email or password")

            refresh = RefreshToken.for_user(user)
            context['data'] = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                }
            }
        except ValidationError as e:
            context['success'] = 0
            context['message'] = e.detail
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)




class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {
            "success": 1,
            "message": "Logout successful",
            "data": {}
        }
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                raise ValidationError("Refresh token is required for logout.")

            token = RefreshToken(refresh_token)
            token.blacklist()

        except ValidationError as e:
            context['success'] = 0
            context['message'] = str(e)
        except TokenError as e:
            context['success'] = 0
            context['message'] = "Invalid or expired token"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)


class OrganizationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {"success": 1, "message": "Organization created successfully", "data": {}}
        try:
            data = request.data.copy()
            data['created_by'] = request.user.id
            serializer = OrganizationSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            org = serializer.save(created_by=request.user)
            # Make creator a member (admin)
            Member.objects.create(user=request.user, organization=org, is_admin=True)
            context['data'] = OrganizationSerializer(org).data
        except ValidationError as e:
            context['success'] = 0
            context['message'] = e.detail
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)


class OrganizationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {"success": 1, "message": "Organizations fetched successfully", "data": []}
        try:
            organizations = Organization.objects.all()
            serializer = OrganizationSerializer(organizations, many=True)
            context['data'] = serializer.data
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
    

class OrganizationUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        context = {"success": 1, "message": "Organization details fetched", "data": {}}
        try:
            org = Organization.objects.get(id=org_id)
            context['data'] = OrganizationSerializer(org).data
        except Organization.DoesNotExist:
            context['success'] = 0
            context['message'] = "Organization not found"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)

    def put(self, request, org_id):
        context = {"success": 1, "message": "Organization updated successfully", "data": {}}
        try:
            org = Organization.objects.get(id=org_id)
            if not Member.objects.filter(user=request.user, organization=org, is_admin=True).exists():
                raise ValidationError("You are not authorized to update this organization.")

            serializer = OrganizationSerializer(org, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_org = serializer.save()
            context['data'] = OrganizationSerializer(updated_org).data
        except ValidationError as e:
            context['success'] = 0
            context['message'] = e.detail
        except Organization.DoesNotExist:
            context['success'] = 0
            context['message'] = "Organization not found"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)

# ✅ Organization Delete View
class OrganizationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        context = {"success": 1, "message": "Organization details fetched", "data": {}}
        try:
            org = Organization.objects.get(id=org_id)
            context['data'] = OrganizationSerializer(org).data
        except Organization.DoesNotExist:
            context['success'] = 0
            context['message'] = "Organization not found"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)

    def delete(self, request, org_id):
        context = {"success": 1, "message": "Organization deleted successfully", "data": {}}
        try:
            org = Organization.objects.get(id=org_id)
            if not Member.objects.filter(user=request.user, organization=org, is_admin=True).exists():
                raise ValidationError("You are not authorized to delete this organization.")
            org.delete()
        except ValidationError as e:
            context['success'] = 0
            context['message'] = e.detail
        except Organization.DoesNotExist:
            context['success'] = 0
            context['message'] = "Organization not found"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)



class MemberCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {"success": 1, "message": "Member added successfully", "data": {}}
        try:
            serializer = MemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            org = serializer.validated_data['organization']
            if not Member.objects.filter(user=request.user, organization=org, is_admin=True).exists():
                raise ValidationError("Only organization admins can add members.")

            member = serializer.save()
            context['data'] = MemberSerializer(member).data
        except ValidationError as e:
            context['success'] = 0
            context['message'] = e.detail
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)


class MemberListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {"success": 1, "message": "Members fetched successfully", "data": []}
        try:
            members = Member.objects.all()
            serializer = MemberSerializer(members, many=True)
            context['data'] = serializer.data
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)


# ✅ Member Update View
class MemberUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        context = {"success": 1, "message": "Member fetched successfully", "data": {}}
        try:
            member = Member.objects.get(id=member_id)
            context['data'] = MemberSerializer(member).data
        except Member.DoesNotExist:
            context['success'] = 0
            context['message'] = "Member not found"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)

    def put(self, request, member_id):
        context = {"success": 1, "message": "Member updated successfully", "data": {}}
        try:
            member = Member.objects.get(id=member_id)
            if not Member.objects.filter(user=request.user, organization=member.organization, is_admin=True).exists():
                raise ValidationError("Only organization admins can update members.")

            serializer = MemberSerializer(member, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_member = serializer.save()
            context['data'] = MemberSerializer(updated_member).data
        except ValidationError as e:
            context['success'] = 0
            context['message'] = e.detail
        except Member.DoesNotExist:
            context['success'] = 0
            context['message'] = "Member not found"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)


# ✅ Member Delete View
class MemberDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        context = {"success": 1, "message": "Member fetched successfully", "data": {}}
        try:
            member = Member.objects.get(id=member_id)
            context['data'] = MemberSerializer(member).data
        except Member.DoesNotExist:
            context['success'] = 0
            context['message'] = "Member not found"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)

    def delete(self, request, member_id):
        context = {"success": 1, "message": "Member removed successfully", "data": {}}
        try:
            member = Member.objects.get(id=member_id)
            if not Member.objects.filter(user=request.user, organization=member.organization, is_admin=True).exists():
                raise ValidationError("Only organization admins can remove members.")
            member.delete()
        except ValidationError as e:
            context['success'] = 0
            context['message'] = e.detail
        except Member.DoesNotExist:
            context['success'] = 0
            context['message'] = "Member not found"
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
