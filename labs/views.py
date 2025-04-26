import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from users.models import *
from .serializers import *
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .utils.percentage import calculate_solve_percentages
from kubernetes import client,config
from kubernetes.client.rest import ApiException
import hashlib
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

config.load_incluster_config()
v1=client.CoreV1Api()
batch_v1=client.BatchV1Api()
net_v1=client.NetworkingV1Api(client.ApiClient())

#lab views
class LabList(APIView):
    @swagger_auto_schema(
        operation_summary="List all labs",
        operation_description="Returns a list of all labs. Can be filtered by difficulty via query parameter.",
        responses={200: LabSerializer(many=True)}
    )

    def get(self, request, format=None):
        difficulty = request.query_params.get('difficulty', None) 
        labs = Lab.objects.all()

        if difficulty:
            labs = labs.filter(difficulty=difficulty)  

        serializer = LabSerializer(labs, many=True, context={'request': request})
        return Response(serializer.data)

class LabDetail(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve lab details",
        operation_description="Fetch detailed information for a specific lab.",
        responses={200: LabSerializer()}
    )

    def get(self, request, pk, format=None):
        lab = get_object_or_404(Lab,pk=pk)
        serializer = LabSerializer(lab, context={'request': request})
        return Response(serializer.data)

#labresources views
class LabResourceFileList(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads
    @swagger_auto_schema(
        operation_summary="List resource files for a lab",
        operation_description="Returns all resource files attached to a specific lab.",
        responses={200: LabResourceFileSerializer(many=True)}
    )

    def get(self, request, lab_id, format=None):
        lab_files = LabResourceFile.objects.filter(resource_id=lab_id)
        serializer = LabResourceFileSerializer(lab_files, many=True, context={'request': request})
        return Response(serializer.data)

class LabResourceFileDetail(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve a lab resource file",
        operation_description="Fetch details for a single resource file attached to a lab.",
        responses={200: LabResourceFileSerializer()}
    )

    def get(self, request, pk, format=None):
        lab_file = get_object_or_404(LabResourceFile,pk=pk)
        serializer = LabResourceFileSerializer(lab_file, context={'request': request})
        return Response(serializer.data)

class SubmitFlag(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Submit a flag for a lab",
        operation_description="Submit a flag to solve a lab. If correct, points and badges are awarded.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["flag"],
            properties={
                "flag": openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: 'Flag submission result with earned badges and progress',
            400: 'Incorrect flag or bad input',
            404: 'Lab not found'
        }
    )

    def post(self, request, lab_id, format=None):
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            return Response({"error": "Lab not found"}, status=status.HTTP_404_NOT_FOUND)

        user_flag = request.data.get('flag', '')
        if user_flag != lab.flag:
            return Response({"message": "Incorrect flag!"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure profile exists (create if not)
        profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'points': 0})

        # Check if lab was already solved
        solved_lab, created = SolvedLab.objects.get_or_create(user=request.user, lab=lab)

        if created:
            # Only award points and check for badge if it's solved for the first time
            profile.points += lab.points
            profile.save()

            # Count how many labs in this category the user has solved
            labs_solved_in_category = SolvedLab.objects.filter(user=request.user, lab__category=lab.category).count()

            # Award badge if 2 labs solved in same category
            badge_created = False
            badge_name = f"{lab.category.name}"

            if labs_solved_in_category == 2 and not Badge.objects.filter(user=request.user, badge_name=badge_name).exists():
                Badge.objects.create(user=request.user, badge_name=badge_name)
                badge_created = True
        else:
            # Lab was already solved
            badge_created = False
            badge_name = None
            labs_solved_in_category = SolvedLab.objects.filter(user=request.user, lab__category=lab.category).count()

        # general percentage

        progress = calculate_solve_percentages(request.user)
        request.user.red_team_percent = progress['offensive_percent']
        request.user.blue_team_percent = progress['defensive_percent']
        request.user.save()

        # Percentage solved in this category
        total_labs_in_category = Lab.objects.filter(category=lab.category).count()
        percentage_solved = (labs_solved_in_category / total_labs_in_category) * 100 if total_labs_in_category else 0

        # Most recently solved lab
        last_solved_lab = SolvedLab.objects.filter(user=request.user).order_by('-solved_on').first()

        return Response({
            "message": "Correct flag! Points added." if created else "Flag already submitted before.",
            "percentage_solved": percentage_solved,
            "last_solved_lab": {
                "lab_id": last_solved_lab.lab.id,
                "title": last_solved_lab.lab.title,
                "solved_on": last_solved_lab.solved_on
            },
            "badge_earned": badge_created,
            "badge_name": badge_name if badge_created else None
        }, status=status.HTTP_200_OK)
        
class SolveProgress(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get user's solve progress",
        operation_description="Returns the user's current solve progress across categories (offensive and defensive).",
        responses={200: 'Progress percentages'}
    )

    def get(self, request):
        user = request.user
        
        progress = calculate_solve_percentages(user)
        return Response(progress, status=200)
    
class SolvedLabList(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="List solved labs",
        operation_description="Returns the list of labs that the authenticated user has solved.",
        responses={200: SolvedLabSerializer(many=True)}
    )

    def get(self, request, format=None):
        solved_labs = SolvedLab.objects.filter(user=request.user)
        serializer = SolvedLabSerializer(solved_labs, many=True)
        return Response(serializer.data)

class BadgeList(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="List earned badges",
        operation_description="Returns all badges earned by the authenticated user.",
        responses={200: BadgeSerializer(many=True)}
    )

    def get(self, request, format=None):
        badges = Badge.objects.filter(user=request.user)
        serializer = BadgeSerializer(badges, many=True)
        return Response(serializer.data)
    
class Search(APIView):
    @swagger_auto_schema(
        operation_summary="Search labs",
        operation_description="Search for labs by title, description, author, or category name.",
        manual_parameters=[
            openapi.Parameter('query', openapi.IN_QUERY, description="Search keyword", type=openapi.TYPE_STRING)
        ],
        responses={200: 'Search results list', 400: 'Query parameter missing'}
    )

    def get(self,request):
        query = request.GET.get('query',None)
        if not query:
            return Response({"error": "Query cannot be empty"}, status=400)
        
        results = Lab.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(author__icontains=query) | Q(category__name__icontains=query)).values("id","title","description","points","author","category__name")

        return Response(results)
    
class CreateMachine(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def check_pod(pod_name,pod_namespace):
        try:
            v1.read_namespaced_pod(name=pod_name,namespace=pod_namespace)
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            raise
    @swagger_auto_schema(
        operation_summary="Create a machine instance for a lab",
        operation_description="Creates a machine instance (Kubernetes pod) for the user to work on a machine-type lab.",
        responses={
            200: 'Machine already running',
            201: 'Machine created successfully',
            400: 'Lab is not a machine',
            404: 'Lab not found'
        }
    )

    def post(self,request,pk):
        machine=get_object_or_404(Lab,pk=pk)
        if not machine.is_machine:
            return Response({'detail':'lab is not a machine'},status=status.HTTP_400_BAD_REQUEST)
        
        pod_name=f"machine-{machine.id}-{hashlib.md5(request.user.username.encode()).hexdigest()}"
        if self.check_pod(pod_name,'lab-pods'):
            return Response({
                'pod_name':pod_name,
                'link':request.build_absolute_uri(f"/{request.user.username}/{machine.id}/"),
                'status':'running'
            })
        
        container=client.V1Container(
            name=pod_name,
            image=machine.image,
            ports=[client.V1ContainerPort(container_port=8443)]
        )

        job=client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(
                name=pod_name,
            ),
            spec=client.V1JobSpec(
                ttl_seconds_after_finished=1,
                active_deadline_seconds=600,
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        name=pod_name,
                        labels={'app':pod_name,'lab':str(machine.id),'user':request.user.username}
                    ),
                    spec=client.V1PodSpec(
                        containers=[container],
                        restart_policy="Never"
                    )
                )
            )
        )
        created_job=batch_v1.create_namespaced_job(namespace="lab-pods",body=job)

        owner_refrences=[
            client.V1OwnerReference(
                api_version="batch/v1",
                kind="Job",
                name=pod_name,
                uid=created_job.metadata.uid,
                controller=True,
                block_owner_deletion=True
            )
        ]

        service=client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=pod_name+'-service',
                owner_references=owner_refrences
            ),
            spec=client.V1ServiceSpec(
                selector={'app':pod_name},
                ports=[
                    client.V1ServicePort(
                        port=machine.port,
                        target_port=machine.port
                    )
                ],
            )
        )

        ingress=client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(
                name=pod_name+'-ingress',
                owner_references=owner_refrences,
                annotations={
                    "traefik.ingress.kubernetes.io/router.middlewares": "lab-pods-stripprefix@kubernetescrd"
                }
            ),
            spec=client.V1IngressSpec(
                rules=[
                    client.V1IngressRule(
                        host="cybermaster.tech",
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path=f"/{request.user.username}/{machine.id}",
                                    path_type="Prefix",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            name=pod_name+'-service',
                                            port=client.V1ServiceBackendPort(
                                                number=machine.port
                                            )
                                        )
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        )

        v1.create_namespaced_service(namespace="lab-pods",body=service)
        net_v1.create_namespaced_ingress(namespace="lab-pods",body=ingress)
        
        return Response({
            'pod_name':pod_name,
            'link':request.build_absolute_uri(f"/{request.user.username}/{machine.id}/"),
            'status':'created'
        },status=status.HTTP_201_CREATED)
