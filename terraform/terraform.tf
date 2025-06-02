# main.tf
data "aws_availability_zones" "available" {}

provider "aws" {
  region = var.region
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "resume-vpc"
  }
}

resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = element(data.aws_availability_zones.available.names, count.index)
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "resume-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "instance_sg" {
  name        = "resume-instance-sg"
  description = "Allow HTTP and SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "resume-instance-sg"
  }
}

resource "aws_launch_template" "resume_app" {
  name_prefix   = "resume-launch-template-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  key_name      = var.ssh_key_name

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.instance_sg.id]
  }

  user_data = base64encode(<<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install docker.io -y
              systemctl start docker
              systemctl enable docker
              docker login -u ${var.dockerhub_username} -p ${var.dockerhub_token}
              docker pull ${var.dockerhub_username}/resume-matcher-backend:latest
              docker run -d -p 80:8000 -e OPENAI_API_KEY=${var.openai_api_key} ${var.dockerhub_username}/resume-matcher-backend:latest
              EOF
  )

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name = "resume-instance"
    }
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical (Ubuntu)

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_autoscaling_group" "asg" {
  name                      = "resume-asg"
  min_size                  = 2
  max_size                  = 4
  desired_capacity          = 2
  vpc_zone_identifier       = aws_subnet.public[*].id
  launch_template {
    id      = aws_launch_template.resume_app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "resume-instance"
    propagate_at_launch = true
  }
}

resource "aws_lb" "app_lb" {
  name               = "resume-app-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.instance_sg.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name = "resume-lb"
  }
}

resource "aws_lb_target_group" "tg" {
  name     = "resume-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

resource "aws_autoscaling_attachment" "asg_attachment" {
  autoscaling_group_name = aws_autoscaling_group.asg.name
  lb_target_group_arn   = aws_lb_target_group.tg.arn
}
