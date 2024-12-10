# AudioTransformer

[Frontend lives here](http://65.109.142.90:8501/)

AudioTransformer is an ongoing personal project focused on deploying a fine-tuned version of Whisper for audio transcription. This project leverages a containerized architecture to efficiently manage and scale the transcription service.

## Project Overview

- **Frontend**: Hosted using a Streamlit server, accessible at [http://65.109.142.90:8501/](http://65.109.142.90:8501/).
- **Backend**: Retrieves the model and performs inference on incoming audio transcription requests.
- **Storage**: MinIO is used to store different versions of the transcription model.
- **Database**: PostgreSQL is utilized to log user behavior and interactions.
- **Traffic Management**: Nginx is configured to handle traffic and SSL termination.

## Deployment

The application is deployed on a remote Hetzner server.

## Architecture

The architecture is modular and scalable. Docker containers have a single purpose and are designed to be stateless.

![Container Architecture](public/images/container_architecture.jpg)

## Stack

![Technology Stack](public/images/stack.png)

## Getting Started

To get started with the AudioTransformer project, you can visit the frontend interface at the provided URL and explore the transcription capabilities.

## Contributing

Contributions to the project are welcome. Please feel free to open issues or submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
