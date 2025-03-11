from aws_cdk import (
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_autoscaling as autoscaling,
    core as cdk
)
from constructs import Construct

class MultiServiceEcsStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with public and private subnets
        vpc = ec2.Vpc(self, "MyVpc", max_azs=2)

        # Create an ECS cluster within the VPC
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        # Define the services and their respective ports
        services = [
            {"name": "audio-index", "port": 8080, "path": "/audio"},
            {"name": "video-index", "port": 8081, "path": "/video"},
            {"name": "image-index", "port": 8082, "path": "/image"},
            {"name": "doc-index", "port": 8083, "path": "/doc"},
        ]

        # Create an Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, "ALB",
            vpc=vpc,
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )

        # Create a single listener for the ALB on port 80
        listener = alb.add_listener("Listener", port=80)

        # Default target group (for unmatched paths, will return 404 by default)
        default_target_group = listener.add_targets(
            "Default",
            port=80,
            targets=[ecs_patterns.ApplicationLoadBalancedServiceBaseProps(
                health_check=elbv2.HealthCheck(path="/", interval=cdk.Duration.seconds(30))
            )]
        )

        # Priority counter for listener rules
        priority = 1

        # Iterate through each service to create Fargate tasks and services
        for service in services:
            # Define the task definition for the service with increased CPU and memory
            task_definition = ecs.FargateTaskDefinition(
                self, f"{service['name']}-TaskDef",
                cpu=512,  # 0.5 vCPU (increased)
                memory_limit_mib=1024  # 1 GiB of memory (increased)
            )

            # Add container to the task definition
            container = task_definition.add_container(
                f"{service['name']}-Container",
                image=ecs.ContainerImage.from_asset(f"./{service['name']}"),
                memory_limit_mib=1024,
                command=["python", "server.py", "--host", "0.0.0.0", f"--port", f"{service['port']}"],
                logging=ecs.LogDriver.aws_logs(stream_prefix=service['name'])
            )

            # Add port mapping for the container
            container.add_port_mappings(ecs.PortMapping(container_port=service['port']))

            # Create the Fargate service
            fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
                self, f"{service['name']}-Service",
                cluster=cluster,
                task_definition=task_definition,
                desired_count=1,
                assign_public_ip=False,
                listener=None,  # Manually attach to the ALB listener
                health_check_grace_period=cdk.Duration.seconds(60)
            )

            # Create a target group for this service
            target_group = listener.add_targets(
                f"{service['name']}-Target",
                port=service['port'],
                targets=[fargate_service],
                path_pattern=service['path'] + "/*",  # Route based on path
                priority=priority,
                health_check=elbv2.HealthCheck(
                    path="/",  # Adjust if your services have a specific health check endpoint
                    interval=cdk.Duration.seconds(30)
                )
            )

            # Add auto-scaling to the Fargate service
            scaling = fargate_service.service.auto_scale_task_count(
                min_capacity=1,  # Minimum 1 task
                max_capacity=4   # Maximum 4 tasks
            )

            # Scale based on CPU utilization (target 70%)
            scaling.scale_on_cpu_utilization(
                f"{service['name']}-CpuScaling",
                target_utilization_percent=70,
                scale_in_cooldown=cdk.Duration.seconds(60),
                scale_out_cooldown=cdk.Duration.seconds(60)
            )

            # Increment priority for the next rule
            priority += 1

        # Output the ALB DNS name for accessing the services
        cdk.CfnOutput(
            self, "LoadBalancerDNS",
            value=alb.load_balancer_dns_name,
            description="DNS name of the Application Load Balancer"
        )

# App and stack instantiation
app = cdk.App()
MultiServiceEcsStack(app, "MultiServiceEcsStack")
app.synth()