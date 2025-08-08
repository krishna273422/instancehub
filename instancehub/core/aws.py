"""
AWS EC2 management core functionality.
"""

import boto3
import time
from botocore.exceptions import ClientError
from typing import List, Dict, Optional

class EC2Manager:
    """Manages AWS EC2 instances."""
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize EC2 manager with specified region."""
        self.region = region
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.ec2_resource = boto3.resource('ec2', region_name=region)
    
    def list_instances(self, state_filter: Optional[str] = None, 
                      tag_filter: Optional[str] = None) -> List[Dict]:
        """
        List EC2 instances with optional filtering.
        
        Args:
            state_filter: Filter by instance state (running, stopped, etc.)
            tag_filter: Filter by tag in format 'key=value'
        
        Returns:
            List of instance dictionaries
        """
        filters = []
        
        if state_filter:
            filters.append({'Name': 'instance-state-name', 'Values': [state_filter]})
        
        if tag_filter and '=' in tag_filter:
            key, value = tag_filter.split('=', 1)
            filters.append({'Name': f'tag:{key}', 'Values': [value]})
        
        try:
            if filters:
                response = self.ec2_client.describe_instances(Filters=filters)
            else:
                response = self.ec2_client.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_data = {
                        'id': instance['InstanceId'],
                        'name': self._get_instance_name(instance),
                        'state': instance['State']['Name'],
                        'type': instance['InstanceType'],
                        'public_ip': instance.get('PublicIpAddress'),
                        'private_ip': instance.get('PrivateIpAddress'),
                        'launch_time': instance.get('LaunchTime'),
                        'vpc_id': instance.get('VpcId'),
                        'subnet_id': instance.get('SubnetId')
                    }
                    instances.append(instance_data)
            
            return instances
            
        except ClientError as e:
            raise Exception(f"Failed to list instances: {e}")
    
    def start_instance(self, instance_id: str, wait: bool = False) -> bool:
        """
        Start an EC2 instance.
        
        Args:
            instance_id: The instance ID to start
            wait: Whether to wait for the instance to be running
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ec2_client.start_instances(InstanceIds=[instance_id])
            
            if wait:
                waiter = self.ec2_client.get_waiter('instance_running')
                waiter.wait(InstanceIds=[instance_id])
            
            return True
            
        except ClientError as e:
            raise Exception(f"Failed to start instance {instance_id}: {e}")
    
    def stop_instance(self, instance_id: str, wait: bool = False) -> bool:
        """
        Stop an EC2 instance.
        
        Args:
            instance_id: The instance ID to stop
            wait: Whether to wait for the instance to be stopped
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ec2_client.stop_instances(InstanceIds=[instance_id])
            
            if wait:
                waiter = self.ec2_client.get_waiter('instance_stopped')
                waiter.wait(InstanceIds=[instance_id])
            
            return True
            
        except ClientError as e:
            raise Exception(f"Failed to stop instance {instance_id}: {e}")
    
    def restart_instance(self, instance_id: str, wait: bool = False) -> bool:
        """
        Restart an EC2 instance.
        
        Args:
            instance_id: The instance ID to restart
            wait: Whether to wait for the restart to complete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # First stop the instance
            self.stop_instance(instance_id, wait=True)
            # Then start it again
            self.start_instance(instance_id, wait=wait)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to restart instance {instance_id}: {e}")
    
    def get_instance_details(self, instance_id: str) -> Optional[Dict]:
        """
        Get detailed information about an instance.
        
        Args:
            instance_id: The instance ID to get details for
        
        Returns:
            Dictionary with instance details or None if not found
        """
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            
            if not response['Reservations']:
                return None
            
            instance = response['Reservations'][0]['Instances'][0]
            
            details = {
                'Instance ID': instance['InstanceId'],
                'Name': self._get_instance_name(instance),
                'State': instance['State']['Name'],
                'Instance Type': instance['InstanceType'],
                'Public IP': instance.get('PublicIpAddress', 'N/A'),
                'Private IP': instance.get('PrivateIpAddress', 'N/A'),
                'VPC ID': instance.get('VpcId', 'N/A'),
                'Subnet ID': instance.get('SubnetId', 'N/A'),
                'Security Groups': ', '.join([sg['GroupName'] for sg in instance.get('SecurityGroups', [])]),
                'Launch Time': str(instance.get('LaunchTime', 'N/A')),
                'Architecture': instance.get('Architecture', 'N/A'),
                'Platform': instance.get('Platform', 'Linux'),
                'Monitoring': instance.get('Monitoring', {}).get('State', 'N/A')
            }
            
            return details
            
        except ClientError as e:
            raise Exception(f"Failed to get instance details: {e}")
    
    def _get_instance_name(self, instance: Dict) -> str:
        """Extract instance name from tags."""
        tags = instance.get('Tags', [])
        for tag in tags:
            if tag['Key'] == 'Name':
                return tag['Value']
        return 'N/A'
