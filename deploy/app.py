from aws_cdk import (
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_autoscaling as autoscaling,
    Stack, App, Duration, CfnOutput
)
from constructs import Construct

class MultiServiceEcsStack(Stack):
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
        default_target_group = elbv2.ApplicationTargetGroup(
            self, "DefaultTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,  # Explicitly specify HTTP
            health_check=elbv2.HealthCheck(
                path="/",
                interval=Duration.seconds(30)
            )
        )
        listener.add_target_groups("DefaultRule", target_groups=[default_target_group])

        # Priority counter for listener rules
        priority = 1

        # Iterate through each service to create Fargate tasks and services
        for service in services:
            # Define the task definition with increased CPU and memory for 11GB containers
            task_definition = ecs.FargateTaskDefinition(
                self, f"{service['name']}-TaskDef",
                cpu=4096,          # 4 vCPU
                memory_limit_mib=12288  # 12 GiB of memory
            )

            # Add container to the task definition
            container = task_definition.add_container(
                f"{service['name']}-Container",
                image=ecs.ContainerImage.from_asset(f"../servers/{service['name']}"),
                memory_limit_mib=12288,  # Match task definition: 12 GiB
                command=["python", "server.py", "--host", "0.0.0.0", f"--port", f"{service['port']}"],
                logging=ecs.LogDriver.aws_logs(stream_prefix=service['name'])
            )

            # Add port mapping for the container
            container.add_port_mappings(ecs.PortMapping(container_port=service['port']))

            # Create the Fargate service
            fargate_service = ecs.FargateService(
                self, f"{service['name']}-Service",
                cluster=cluster,
                task_definition=task_definition,
                desired_count=1,
                assign_public_ip=False,
                health_check_grace_period=Duration.seconds(60)
            )

            # Create a target group for this service
            target_group = elbv2.ApplicationTargetGroup(
                self, f"{service['name']}-Target",
                vpc=vpc,
                port=service['port'],
                protocol=elbv2.ApplicationProtocol.HTTP,  # Explicitly specify HTTP
                targets=[fargate_service],
                health_check=elbv2.HealthCheck(
                    path="/",
                    interval=Duration.seconds(30)
                )
            )

            # Add a listener rule for path-based routing
            listener.add_action(
                f"{service['name']}-Rule",
                priority=priority,
                conditions=[elbv2.ListenerCondition.path_patterns([service['path'] + "/*"])],
                action=elbv2.ListenerAction.forward([target_group])
            )

            # Add auto-scaling to the Fargate service
            scaling = fargate_service.auto_scale_task_count(
                min_capacity=1,
                max_capacity=4
            )

            # Scale based on CPU utilization (target 70%)
            scaling.scale_on_cpu_utilization(
                f"{service['name']}-CpuScaling",
                target_utilization_percent=70,
                scale_in_cooldown=Duration.seconds(60),
                scale_out_cooldown=Duration.seconds(60)
            )

            # Increment priority for the next rule
            priority += 1

        # Output the ALB DNS name for accessing the services
        CfnOutput(
            self, "LoadBalancerDNS",
            value=alb.load_balancer_dns_name,
            description="DNS name of the Application Load Balancer"
        )

# App and stack instantiation
app = App()
MultiServiceEcsStack(app, "MultiServiceEcsStack")
app.synth()