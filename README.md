# DevOps Dashboard

Used a single NAT gw to reduce cost. For production environments there should be one NAT gw per AZ
ECR is set to mutable for development simplicity. Production would use immutable tags with git SHA-based versioning to prevent image tampering.
To be updated.