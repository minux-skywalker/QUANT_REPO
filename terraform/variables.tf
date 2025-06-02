variable "region" {
  description = "AWS region to deploy resources"
  default     = "ap-south-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of CIDRs for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "availability_zones" {
  description = "AZs to deploy resources"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "desired_capacity" {
  description = "Desired number of EC2 instances in Auto Scaling Group"
  default     = 2
}

variable "min_size" {
  description = "Minimum number of instances in Auto Scaling Group"
  default     = 1
}

variable "max_size" {
  description = "Maximum number of instances in Auto Scaling Group"
  default     = 3
}

variable "dockerhub_username" {
  description = "Docker Hub username"
  type        = string
}

variable "dockerhub_token" {
  description = "Docker Hub token or password"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key to be passed as env variable"
  type        = string
  sensitive   = true
}

variable "ssh_key_name" {
  description = "EC2 Key Pair name"
  type        = string
}

