#!/usr/bin/env python
import boto3

session = boto3.Session()
wellarchitected = session.client('wellarchitected')
cloudwatch = session.client('cloudwatch')

def lambda_handler(event, context):
    risk_counts = []
    workloads = wellarchitected.list_workloads().get('WorkloadSummaries')
    for workload in workloads:
        workload = wellarchitected.get_workload(WorkloadId=workload.get('WorkloadId'))
        risk = {}
        risk['name'] = workload.get('Workload').get('WorkloadName')
        risk['counts'] = workload.get('Workload').get('RiskCounts')
        risk_counts.append(risk)

    for risk in risk_counts:
        for risk_type,count in risk.get('counts').items():
            cloudwatch.put_metric_data(
                Namespace='Well Architected',
                MetricData=[{
                    'MetricName': risk_type,
                    'Value': count,
                    'Unit': 'Count',
                    'Dimensions': [{
                        'Name': 'By Workload',
                        'Value': risk.get('name')
                    }]
                }]
            )
