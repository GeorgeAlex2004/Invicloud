# E-Commerce Inventory CI/CD Pipeline

This project demonstrates a complete CI/CD pipeline for an E-Commerce Inventory Microservice using:

- **Application**: Python Flask
- **Source Control**: Git / GitHub
- **Containerization**: Docker
- **Infrastructure as Code**: Terraform
- **Cloud Provider**: AWS (EKS for Kubernetes)
- **CI**: GitHub Actions
- **CD**: ArgoCD (GitOps)

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── products-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── terraform/
│   └── main.tf
└── config-repo/
    └── products-service/
        ├── deployment.yaml
        └── service.yaml
```

## Step-by-Step Execution Guide

### Phase 1: Initial Setup and Local Testing

#### 1. Initialize Git & Push Application Code

```bash
git init
git add .
git commit -m "Initial project setup"
git remote add origin https://github.com/GeorgeAlex2004/Invicloud.git
git push -u origin main
```

#### 2. Test Docker Locally

```bash
# Replace with your Docker Hub username
docker build -t georgealex2004/products-service:latest ./products-service/
docker run -d -p 5000:5000 --name products-api georgealex2004/products-service:latest
```

Verify by visiting http://localhost:5000/products in your browser. Then stop and remove the container:

```bash
docker stop products-api && docker rm products-api
```

### Phase 2: Provision Cloud Infrastructure (EKS Cluster)

#### 3. Configure AWS CLI

Ensure your AWS CLI is configured with the necessary permissions:

```bash
aws configure
```

#### 4. Deploy Infrastructure with Terraform

Navigate to the terraform directory:

```bash
cd terraform
terraform init
terraform plan
terraform apply --auto-approve
```

**Note**: This process will take 15-20 minutes.

#### 5. Configure kubectl to Connect to EKS

After terraform apply finishes, it will output a command. Copy and run it:

```bash
# Example output: aws eks --region us-east-1 update-kubeconfig --name ecommerce-cluster
$(terraform output -raw kubeconfig_command)
```

Verify the connection to your new cluster:

```bash
kubectl get nodes
```

### Phase 3: Configure CI/CD

#### 6. Set Up GitHub Secrets for CI

Go to your application repository on GitHub -> Settings -> Secrets and variables -> Actions.
Create two new repository secrets:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub personal access token

#### 7. Push and Trigger CI

Push the code again (or make a small change) to trigger the GitHub Actions workflow. Verify that it successfully builds and pushes the image to Docker Hub.

#### 8. Set Up the Configuration Repository

Create a new, separate GitHub repository (e.g., `ecommerce-inventory-config`).
Push the deployment.yaml and service.yaml files from the `config-repo` directory into a `products-service` directory in this new repo.

#### 9. Install ArgoCD on the EKS Cluster

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### 10. Access the ArgoCD UI

Forward the port to access the server on your local machine:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Get the initial admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

Open https://localhost:8080 in your browser. Log in with username `admin` and the password from the previous command.

#### 11. Create the ArgoCD Application

In the ArgoCD UI, click **+ NEW APP**.

- **Application Name**: `products-service`
- **Project Name**: `default`
- **Sync Policy**: Automatic (also check Prune Resources and Self Heal)
- **Repository URL**: Your config repo URL (e.g., `https://github.com/user/ecommerce-inventory-config.git`)
- **Revision**: `HEAD`
- **Path**: `products-service`
- **Cluster URL**: `https://kubernetes.default.svc`
- **Namespace**: `default`

Click **CREATE**. ArgoCD will now automatically deploy your application.

#### 12. Verify the Deployment

```bash
kubectl get svc products-service-svc
```

Copy the EXTERNAL-IP address from the service and open `http://<EXTERNAL-IP>/products` in your browser. You should see the JSON output from your service.

### Phase 4: Monitoring (Optional but Recommended)

#### 13. Install Prometheus and Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

#### 14. Access Grafana Dashboard

```bash
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
```

Get the Grafana admin password:

```bash
kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 -d; echo
```

Log in to http://localhost:3000 with username `admin` and the retrieved password to explore your cluster's metrics.

## Important Notes

1. **Replace Placeholders**: Make sure to replace `<your-dockerhub-username>`, `<your-github-repo-url>`, and `<your-config-repo-url>` with your actual values throughout the configuration files.

2. **AWS Permissions**: Ensure your AWS credentials have the necessary permissions to create EKS clusters, VPCs, and other AWS resources.

3. **Docker Hub**: You'll need a Docker Hub account and personal access token for the CI pipeline.

4. **Costs**: Running an EKS cluster will incur AWS costs. Remember to clean up resources when done testing.

5. **Security**: This setup is for demonstration purposes. For production use, consider additional security measures like RBAC, network policies, and secrets management.

## Troubleshooting

- If you encounter permission issues with AWS, ensure your IAM user/role has the necessary EKS permissions
- If Docker builds fail, check your Docker Hub credentials in GitHub Secrets
- If ArgoCD sync fails, verify the configuration repository URL and path are correct
- For EKS connectivity issues, ensure your kubectl context is properly configured
