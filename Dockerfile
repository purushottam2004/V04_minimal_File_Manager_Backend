# Minimal Dockerfile for MCP Python sandbox (not for code deployment)
# Uses official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /sandbox

#Install any extra packages here using pip if needed
RUN pip install numpy pandas matplotlib scipy seaborn scikit-learn sympy

# The container will run user scripts mounted into /sandbox 