from aws_cdk import (
    core as cdk,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as event,
    aws_events_targets as events_targets,
    aws_cloudwatch as cloudwatch
)


# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.``
from aws_cdk import core


class CdkStack(cdk.Stack):
    
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
    
        region = cdk.Stack.of(self).region
        account = cdk.Stack.of(self).account

        publish_role = iam.Role(
            self, 'PublishWorkloadMetricsRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )

        publish_function = _lambda.Function(
            self, 'PublishWorkloadMetrics',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='publish_workload_metrics.lambda_handler',
            code=_lambda.Code.asset('lambda'),
            role=publish_role
        )

        publish_event = event.Rule(
            self, 'publish_workload_metrics_event',
            description='Scheduled event to run PublishWorkloadMetrics lambda',
            enabled=True,
            schedule=event.Schedule.rate(cdk.Duration.minutes(5)),
            targets=[events_targets.LambdaFunction(publish_function)]
        )

        publish_role.add_to_policy(iam.PolicyStatement(
            resources=['arn:aws:logs:{}:{}:*'.format(region, account)],
            actions=['logs:CreateLogGroup']
        ))

        publish_role.add_to_policy(iam.PolicyStatement(
            resources=['arn:aws:logs:{}:{}:log-group:/aws/lambda/publish_workload_risk_metrics:*'.format(region, account)],
            actions=['logs:CreateLogStream',
                     'logs:PutLogEvents']
        ))

        publish_role.add_to_policy(iam.PolicyStatement(
            resources=['*'],
            actions=['wellarchitected:ListWorkloads',
                    'cloudwatch:PutMetricData',
                    'wellarchitected:GetWorkload']
        ))

        workload_metrics_dashboard = cloudwatch.Dashboard(
            self, 'WellArchitectedToolWorkloadMetricsDashboard',
            dashboard_name='WellArchitectedToolWorkloadsMetrics'
        )

        workload_graph_widget = cloudwatch.GraphWidget(
            title='Test Workload Metrics',
            width=6,
            height=6,
            left=[cloudwatch.Metric(
                metric_name='MEDIUM',
                namespace='Well Architected',
                statistic="avg",
                label='MEDIUM',
                dimensions_map={'By Workload': 'test'}
            ), cloudwatch.Metric(
                metric_name='HIGH',
                namespace='Well Architected',
                statistic="avg",
                label='HIGH',
                dimensions_map={'By Workload': 'test'}
            ), cloudwatch.Metric(
                metric_name='UNANSWERED',
                namespace='Well Architected',
                statistic="avg",
                label='UNANSWERED',
                dimensions_map={'By Workload': 'test'}
            ), cloudwatch.Metric(
                metric_name='NONE',
                namespace='Well Architected',
                statistic="avg",
                label='NONE',
                dimensions_map={'By Workload': 'test'}
            ), cloudwatch.Metric(
                metric_name='NOT_APPLICABLE',
                namespace='Well Architected',
                statistic="avg",
                label='NOT_APPLICABLE',
                dimensions_map={'By Workload': 'test'}
            )
            ]
        )

        workload_metrics_dashboard.add_widgets(workload_graph_widget)