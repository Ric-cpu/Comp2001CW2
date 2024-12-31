# Comp2001CW2
# Trail Service Microservice

A RESTful microservice for managing trails and location points, developed as part of the COMP2001 coursework. The microservice supports CRUD operations, uses JWT-based authentication, and is containerized with Docker.


## Key Features
- CRUD operations for managing trails and location points.
- JWT-based authentication and role-based access control.
- RESTful API principles.
- Swagger UI for API documentation and testing.



## Prerequisites
- Docker must be installed on your machine.
- Ensure your system can access port 8000 (or map it differently when running the container).



## Deployment Instructions
To deploy and run the microservice:

Pull the Docker Image:
Copy code:
docker pull rickardo827/trail_service

Run the Docker Container:
Copy code:
docker run -p 8000:8000 rickardo827/trail_service

Access the Swagger UI: After running those commands above, open the following URL in a web browser.
Copy link:
http://127.0.0.1:8000/swagger/


